"""
placeReflection
Copyright (C) 2021-2022, Ingo Clemens, brave rabbit, www.braverabbit.com

    GNU GENERAL PUBLIC LICENSE Version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------

Description:

This tool places the selected object at a reflected position based on
the view vector and the surface normal of a mesh at the cursor position.
Though any object can be placed this way it's main usage is to easily
place a light so that the main light reflection occurs at the point of
the cursor.

------------------------------------------------------------------------

Usage:

1. Select the light or object to place.
2. Activate placeReflection from the object menu in the 3d view or by
   searching for it with F3.
3. LMB drag the mouse over the surface to define the object's reflection
   point.
4. Use the scrollwheel on the mouse to set the distance of the object to
   the surface.
   When holding Shift the movement gets slower, holding Ctrl increases
   the speed.
5. Press Return/Enter to exit the tool or RMB to cancel.
6. Adjust the additional options, like axis or affecting only position
   or rotation through the redo panel at the bottom of the 3d view.

------------------------------------------------------------------------

Changelog:

0.8.0 - 2022-02-17
      - Fixed several issues related to adjusting the distance with the
        mouse wheel before continuing to drag over the surface.
      - Removed the tool from the current tool panel as it felt
        misplaced.

0.7.0 - 2021-04-15
      - Added the light distance to the operator and redo panel.

0.6.0 - 2021-04-07
      - First public release

------------------------------------------------------------------------
"""

bl_info = {"name": "Place Reflection",
           "author": "Ingo Clemens",
           "version": (0, 8, 0),
           "blender": (2, 92, 0),
           "category": "Lighting",
           "location": "View3D > Object",
           "description": "Place lights and reflected objects by dragging over a surface",
           "warning": "",
           "doc_url": "https://www.braverabbit.com/place-reflection",
           "tracker_url": ""}

import bpy
import bpy.utils.previews
from bpy_extras import view3d_utils

import math
from mathutils import Vector
import os


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

# The default axis of the object used for alignment. The sign is
# actually inverted in order to have the axis point at the object and
# not away from it.
AIM_AXIS = "Z"
# True, if the object's location is affected.
USE_LOCATION = True
# True, if the object's rotation is affected.
USE_ROTATION = True
# The default distance of the object to place.
DISTANCE = 0.0
# The speed factor when Shift is pressed when using the mouse wheel.
SPEED_SLOW = 0.1
# The speed factor when Ctrl is pressed when using the mouse wheel.
SPEED_FAST = 10.0


# ----------------------------------------------------------------------
# Property enum values
# ----------------------------------------------------------------------

AXIS_ITEMS = (("-X", "X", ""),
              ("X", "-X", ""),
              ("-Y", "Y", ""),
              ("Y", "-Y", ""),
              ("-Z", "Z", ""),
              ("Z", "-Z", ""))


# ----------------------------------------------------------------------
# Main Operator
# ----------------------------------------------------------------------

class OBJECT_OT_PlaceReflection(bpy.types.Operator):
    """Operator class for the tool.
    """
    bl_idname = "view3d.place_reflection"
    bl_label = "Place Reflection"
    bl_description = "Drag over a surface to position the reflection of the selected object"
    bl_options = {'REGISTER', 'UNDO'}

    axis_value: bpy.props.EnumProperty(name="Axis",
                                       description="The axis which is oriented towards the surface",
                                       items=AXIS_ITEMS,
                                       default=AIM_AXIS)
    location_value: bpy.props.BoolProperty(name="Location",
                                           description="Affect the location of the selected object",
                                           default=USE_LOCATION)
    rotation_value: bpy.props.BoolProperty(name="Rotation",
                                           description="Affect the rotation of the selected object",
                                           default=USE_ROTATION)
    distance_value: bpy.props.FloatProperty(name="Distance",
                                            description="The distance of the selected object to "
                                                        "the surface. Set to 0 to use the current "
                                                        "distance of the object",
                                            default=DISTANCE)

    startPos = None
    startRot = None
    isDragging = False
    dragPos = None
    reflVector = None
    dist = 1.0
    shiftPressed = False
    ctrlPressed = False

    isModal = False

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        This method is mandatory for displaying the redo panel.

        :param context: The current context.
        :type context: bpy.context
        """
        self.applyPlacement(context.object)
        self.isModal = False
        return {'FINISHED'}

    def modal(self, context, event):
        """Modal operator function.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        # --------------------------------------------------------------
        # Global switches which define the current action.
        # --------------------------------------------------------------

        # Switch between drag mode and adjusting the distance with the
        # scroll wheel.
        if event.type == 'LEFTMOUSE':
            if not self.isDragging:
                self.isDragging = True
            else:
                self.isDragging = False
        # Set the distance adjustment to fine.
        if 'SHIFT' in event.type:
            if not self.shiftPressed:
                self.shiftPressed = True
            else:
                self.shiftPressed = False
        # Set the distance adjustment to coarse.
        if 'CTRL' in event.type:
            if not self.ctrlPressed:
                self.ctrlPressed = True
            else:
                self.ctrlPressed = False

        # Adjust the distance.
        if event.type in ['WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
            self.set_distance_factor(event.type)
            self.set_position(context.object)

        # Place the selected object by LMB-dragging the cursor.
        if event.type == 'MOUSEMOVE' and self.isDragging:
            self.drag_placement(context, event)

        # End the operator.
        elif event.type in {'RET', 'NUMPAD_ENTER'}:
            self.reset(context)
            return {'FINISHED'}

        # Cancel the operator.
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.cancel(context)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        """Invoke the operator.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        self.isModal = True

        if context.object:
            context.window_manager.modal_handler_add(self)
            context.workspace.status_text_set("LMB-Drag: Place, "
                                              "Esc/RMB: Cancel, "
                                              "Mouse Wheel: Distance, "
                                              "Ctrl + Mouse Wheel: Fast, "
                                              "Shift + Mouse Wheel: Slow")

            # Get the location and rotation of the object for
            # cancelling.
            self.startPos = context.object.location.copy()
            self.startRot = context.object.rotation_euler.copy()

            return {'RUNNING_MODAL'}

        self.report({'WARNING'}, "No object selected to place")
        return self.cancel(context)

    def cancel(self, context):
        """Reset and cancel the current operation.

        :param context: The current context.
        :type context: bpy.context

        :return: The enum for cancelling the operator.
        :rtype: enum
        """
        self.isModal = False

        # Set the location and rotation back to their original values.
        if context.object:
            context.object.location = self.startPos
            context.object.rotation_euler = self.startRot

        # Reset the operator.
        self.reset(context)

        return {'CANCELLED'}

    def reset(self, context):
        """Reset the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        self.isModal = False
        self.isDragging = False
        context.workspace.status_text_set(None)

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def drag_placement(self, context, event):
        """Perform the placement of the object based on the current
        cursor position.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event

        :return: True, if an object is found and the placement can be
                 performed.
        :rtype: bool
        """
        region = context.region
        regionView3d = context.region_data
        viewPos = event.mouse_region_x, event.mouse_region_y

        # Convert the screen position of the cursor to a world view
        # position and vector.
        # By default the vector is already normalized.
        viewVector = view3d_utils.region_2d_to_vector_3d(region, regionView3d, viewPos)
        viewOrigin = view3d_utils.region_2d_to_origin_3d(region, regionView3d, viewPos)

        # Cast a ray into the view and return the hit object and related
        # data.
        result, pos, normal, index, obj, mat = context.scene.ray_cast(context.view_layer.depsgraph,
                                                                      viewOrigin,
                                                                      viewVector)

        # Discontinue if no intersection can be found or if the
        # intersected object is the object to be placed.
        if not result or obj == context.object:
            return False

        self.dragPos = pos

        # Calculate the reflection vector.
        self.reflVector = reflection_vector(viewVector, normal)

        # Get the current distance to the object's intersection point at
        # the first drag and set this as the distance to use for the
        # entire cycle of the placement.
        # In case the object is in it's default position either at the
        # world center of the cursor position use the distance of the
        # view to the surface point.
        cursorPos = context.scene.cursor.location
        objPos = context.object.location
        if objPos == Vector((0.0, 0.0, 0.0)) or objPos == cursorPos:
            self.dist = distance(viewOrigin, self.dragPos)
        else:
            self.dist = distance(self.dragPos, context.object.location)

        # Apply the new position and rotation.
        self.applyPlacement(context.object)

    def set_distance_factor(self, eventType):
        """Adjust the speed for setting the distance depending on the
        currently pressed modifier keys.

        :param eventType: The current event type string.
        :type eventType: str
        """
        factor = 1.0
        speed = 0.05
        if self.shiftPressed:
            speed *= SPEED_SLOW
        elif self.ctrlPressed:
            speed *= SPEED_FAST

        if eventType == 'WHEELUPMOUSE':
            factor += speed
        elif eventType == 'WHEELDOWNMOUSE':
            factor -= speed

        if factor < 0:
            factor = 0

        self.dist *= factor

    def applyPlacement(self, obj):
        """Apply the position and rotation, based on the global
        settings.

        :param obj: The object.
        :type obj; bpy.types.Object
        """
        if self.location_value:
            self.set_position(obj)
        if self.rotation_value:
            self.set_rotation(obj)
        # Get the current distance for the redo panel.
        self.distance_value = self.dist

    def set_position(self, obj):
        """Set the resulting position of the selected object based on
        the current drag data.

        :param obj: The object to position.
        :type obj; bpy.types.Object
        """
        if self.reflVector is None:
            return

        # When adjusting the distance through the redo panel, therefore
        # the modal mode is not active, get the distance from the panel.
        if not self.isModal:
            self.dist = self.distance_value
        obj.location = self.reflVector * self.dist + self.dragPos

    def set_rotation(self, obj):
        """Set the resulting orientation of the selected object based on
        the current drag data.

        :param obj: The object to rotate.
        :type obj; bpy.types.Object
        """
        if self.reflVector is None:
            return

        upAxis = "Z"
        if self.axis_value in ["Z", "-Z"]:
            upAxis = "Y"
        # Build a quaternion based on the reflection vector and an up
        # axis to keep the aligned object somewhat oriented.
        quat = self.reflVector.to_track_quat(self.axis_value, upAxis)

        # Get the current rotation order/mode to be able to apply the
        # new rotation accordingly.
        order = obj.rotation_mode

        # If the rotation mode is axis-angle, set it to quaternion to
        # reduce the need for conversion.
        if order == 'AXIS_ANGLE':
            obj.rotation_mode = 'QUATERNION'

        if order == 'QUATERNION':
            obj.rotation_quaternion = quat
        else:
            obj.rotation_euler = quat.to_euler(order)


# ----------------------------------------------------------------------
# Math utilities
# ----------------------------------------------------------------------

def reflection_vector(viewVector, faceNormal):
    """Return the reflection vector based on the given view vector and
    normal at the reflection point.

    :param viewVector: The vector of the reflection source ray.
    :type viewVector: vector
    :param faceNormal: The vector of the normal at the reflection point.
    :type faceNormal: vector

    :return: The vector of the reflection.
    :rtype: vector
    """
    doublePerp = 2.0 * viewVector @ faceNormal
    return viewVector - (doublePerp * faceNormal)


def distance(point1, point2):
    """Return the distance between the two given points.

    :param point1: The first point.
    :type point1: vector
    :param point2: The second point.
    :type point2: vector

    :return: The distance between the points.
    :rtype: float
    """
    value = 0.0
    for i in range(3):
        value += math.pow(point1[i] - point2[i], 2)
    return math.sqrt(value)


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

def menu_item(self, context):
    """Draw the menu item and it's sub-menu.

    :param context: The current context.
    :type context: bpy.context
    """
    # Get the icon from the preview collection.
    pcoll = preview_collections["icons"]
    icon = pcoll["tool_icon"]

    self.layout.separator()
    self.layout.operator(OBJECT_OT_PlaceReflection.bl_idname,
                         text="Place Reflection",
                         icon_value=icon.icon_id)


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Main dictionary for storing the menu icons.
preview_collections = {}

# Collect all classes in a list for easier access.
classes = [OBJECT_OT_PlaceReflection]


def register():
    """Register the add-on.
    """
    # Setup the preview collection for giving access to the icon.
    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("tool_icon", os.path.join(icons_dir, "placeReflection.png"), 'IMAGE', True)
    preview_collections["icons"] = pcoll

    for cls in classes:
        bpy.utils.register_class(cls)
    # Add the menu items.
    bpy.types.VIEW3D_MT_object.append(menu_item)


def unregister():
    """Unregister the add-on.
    """
    # Remove the preview collection.
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)
    # Remove the menu items.
    bpy.types.VIEW3D_MT_object.remove(menu_item)


if __name__ == "__main__":
    register()
