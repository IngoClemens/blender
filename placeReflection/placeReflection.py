"""
placeReflection
Copyright (C) 2021, Ingo Clemens, brave rabbit, www.braverabbit.com

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
   or rotation through the operator panel at the bottom of the 3d view.

Tool Panel:

By default the tool panel to access the settings prior entering the tool
is hidden. To display the tool panel choose:
    3D Panel > Object > Place Reflection > Toggle Tool Panel
The panel will be displayed in the tool panels tool tab. If it's not
displayed directly you need to move the mouse over the tool panel to
force a refresh.

------------------------------------------------------------------------
"""

import bpy
from bpy_extras import view3d_utils

import math


# ----------------------------------------------------------------------
# Property Group
# ----------------------------------------------------------------------

class PlaceReflection_properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    axis_value: bpy.props.EnumProperty(name="Axis",
                                       description="The axis which is oriented towards the surface",
                                       items=(("-X", "X", ""),
                                              ("X", "-X", ""),
                                              ("-Y", "Y", ""),
                                              ("Y", "-Y", ""),
                                              ("-Z", "Z", ""),
                                              ("Z", "-Z", "")),
                                       default="Z")
    location_value: bpy.props.BoolProperty(name="Location",
                                           description="Affect the location of the selected object",
                                           default=True)
    rotation_value: bpy.props.BoolProperty(name="Rotation",
                                           description="Affect the rotation of the selected object",
                                           default=True)


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
                                       items=(("-X", "X", ""),
                                              ("X", "-X", ""),
                                              ("-Y", "Y", ""),
                                              ("Y", "-Y", ""),
                                              ("-Z", "Z", ""),
                                              ("Z", "-Z", "")),
                                       default="Z")
    location_value: bpy.props.BoolProperty(name="Location",
                                           description="Affect the location of the selected object",
                                           default=True)
    rotation_value: bpy.props.BoolProperty(name="Rotation",
                                           description="Affect the rotation of the selected object",
                                           default=True)

    startPos = None
    startRot = None
    isDragging = False
    dragPos = None
    dist = None
    reflVector = None
    distFactor = 1.0
    distIncrementFactor = 1.0
    shiftPressed = False
    ctrlPressed = False

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

        # Get the current distance to the object's intersection point
        # at the first drag and set this as the distance to use for the
        # entire cycle of the placement.
        if self.dist is None:
            self.dist = distance(self.dragPos, context.object.location)

        # Apply the new position and rotation.
        self.applyPlacement(context.object)

    def set_distance_factor(self, eventType):
        """Adjust the speed for setting the distance depending on the
        currently pressed modifier keys.

        :param eventType: The current event type string.
        :type eventType: str
        """
        speed = 0.05
        if self.shiftPressed:
            speed *= 0.1
        elif self.ctrlPressed:
            speed *= 10

        if eventType == 'WHEELUPMOUSE':
            self.distFactor += speed
        elif eventType == 'WHEELDOWNMOUSE':
            self.distFactor -= speed

        if self.distFactor < 0:
            self.distFactor = 0

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

    def set_position(self, obj):
        """Set the resulting position of the selected object based on
        the current drag data.

        :param obj: The object to position.
        :type obj; bpy.types.Object
        """
        if self.reflVector is None:
            return

        obj.location = self.reflVector * self.dist * self.distFactor + self.dragPos

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
# Tool Panel Switch
# ----------------------------------------------------------------------

class OptionPanel(object):
    """Class for setting the visibility of the of the tool panel.

    Acts as a global switch to be able to show and hide the panel on
    demand.
    """
    def __init__(self):
        """Disable the initial visibility of the panel.
        """
        self.show = False


optionPanel = OptionPanel()


class OBJECT_OT_PlaceReflection_options(bpy.types.Operator):
    """Operator class to set the visibility of the tool panel.

    The single function of this class is to be able to add a menu item
    which allows to show/hide the tool panel.
    Because it doesn't seem possible to attach simple commands to menu
    items a simple operator needs to be used.
    """
    bl_idname = "view3d.place_reflection_options"
    bl_label = "Place Reflection Options"
    bl_description = "Toggle the display of the Place Reflection tool panel"

    def execute(self, context):
        """Toggle the visibility status of the tool options.

        :param context: The current context.
        :type context: bpy.context
        """
        optionPanel.show = not optionPanel.show
        return {'FINISHED'}


# ----------------------------------------------------------------------
# Tool Panel
# ----------------------------------------------------------------------

class VIEW3D_PT_PlaceReflection(bpy.types.Panel):
    """Creates a Panel in the Tool properties window.
    """
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_label = "Place Reflection"

    @classmethod
    def poll(cls, context):
        """Returns, if the panel is visible.

        :param context: The current context.
        :type context: bpy.context

        :return: True, if the panel should be visible.
        :rtype: bool
        """
        return optionPanel.show

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        # Access the global properties.
        scene = context.scene
        place_reflection = scene.place_reflection

        layout = self.layout
        layout.prop(place_reflection, "axis_value")
        layout.prop(place_reflection, "location_value")
        layout.prop(place_reflection, "rotation_value")

        # Call the operator with the current settings.
        op = layout.operator("view3d.place_reflection")
        op.axis_value = place_reflection.axis_value
        op.location_value = place_reflection.location_value
        op.rotation_value = place_reflection.rotation_value


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
