"""
rapidSDK
Copyright (C) 2022, Ingo Clemens, brave rabbit, www.braverabbit.com

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

Rapid SDK provides a simple one-button workflow to quickly set up
driving relationships between one or more properties. It's aimed to help
simplify the steps needed to adjust relative ranges or even non-linear
behavior.
Obviously a one-button solution has limitations such as defining more
complex driving setups (multiple driving objects) or evaluating certain
properties such as colors or strings. But this is beyond the scope of
this add-on.

------------------------------------------------------------------------

Usage:

The Rapid SDK menu item is located in:
Object Mode: Main Menu > Object > Animation > Rapid SDK
Pose Mode: Main Menu > Pose > Animation > Rapid SDK


Rapid SDK is designed to be used on two modes: Creating a driving
relationship and editing an existing driver.
The current selection defines which mode is being used.

Create Mode:
1. Select two or more objects. The last and currently active object acts
as the driver. The state of the selected objects defines the starting
point of the relationship.
2. Run Rapid SDK. This stores the current values. All properties which
are not already driven or animated but change over the course of the
setup will be part of the relationship.
3. Select the driver and modify it to define the end range of the
relationship.
4. Select the driven object or objects and adjust these accordingly.
5. Run Rapid SDK again to finally setup the driver.

Edit Mode:
In contrast to the create mode only one driven object can be edited at a
time. This is a current limitation due to the one-button design of the
add-on.
1. Go to the position where the driven object needs adjustment.
2. Run Rapid SDK. This temporarily disables the drivers so that the
object can be manipulated.
3. Adjust the properties of the driven object.
4. Run Rapid SDK again. This either creates a new keyframe on the
driving curve in case the driving value has changed as well or
existing keyframes on the driver curve will be updated. Also, the driver
curves will get activated again.

If the selection changes while in Edit mode and Rapid SDK is run the
driver curves of the previous object will be activated and the new
object will be put into edit mode.

------------------------------------------------------------------------

Manual command:

from rapidSDK import rapidSDK
rapidSDK.execute()

------------------------------------------------------------------------

Changelog:

0.11.0 - 2023-10-17
       - Added compatibility with Blender 4.0.

0.10.0 - 2023-04-23
       - Fixed that driving armature properties are not correctly respected
         when updating a relationship.

0.9.0 - 2022-05-11
      - Added support for object modifiers.
      - Added a colored frame to clearly identify create or edit mode.
      - Improvements to object/bone selections in object mode.
      - Fixed that adding keys outside the defined range are created with
        in-between curve handles.
      - Fixed that multiple recorded properties create the same number of
        drivers per property.
      - Fixed that driver indices weren't correctly passed which leads to keys
        not getting created.

0.8.1 - 2022-04-05
      - Fixed an issue with IDPropertyGroups.

0.8.0 - 2022-04-05
      - Switched the stored objects to string representations because of a
        bone related undo bug which invalidates the object data and leads to
        a hard crash.

0.7.0 - 2022-04-05
      - Improvement to the selection detection so that an object can be the
        driver for a bone in object mode.
      - Fixed an error because custom string properties are not filtered.
      - Fixed that already driven shape keys are edited when creating new
        drivers.
      - Fixed a typo regarding custom properties.
      - Fixed an issue where custom properties weren't able to be driven.

0.6.0 - 2022-03-31
      - Added an on-screen message which displays the names of the currently
        affected objects in create mode.
      - The on-screen messages are now scaling correctly depending on the
        pixel-size of the display.
      - Fixed that the driven object's properties are left muted when leaving
        edit mode with nothing selected.

0.5.1 - 2022-03-30
      - Fixed an issue where a wrong object/armature/bone selection combo
        doesn't throw a warning.
      - Fixed that edit mode can be entered without any driven properties
        present.

0.5.0 - 2022-03-30
      - Added a separate preference setting for intermediate key handles.
      - Added a preference setting for choosing the position of the on-screen
        message.

0.4.0 - 2022-03-29
      - Added an on-screen message for create and edit mode.
      - Improved selection detection of hidden bones.
      - Possible bugfixes which can lead to random crashes (to be watched)

0.3.0 - 2022-03-29
      - Added shape keys on mesh and curve objects to be driven.
      - Added a menu item to the Object and Pose Animation submenu.
      - Added preferences for the extrapolation, tangent type and tolerance.

0.2.0 - 2022-03-26
      - Redesign to allow multiple objects to be driven in creation mode.

0.1.0 - 2022-03-24

------------------------------------------------------------------------
"""

bl_info = {"name": "Rapid SDK",
           "author": "Ingo Clemens",
           "version": (0, 11, 0),
           "blender": (2, 93, 0),
           "category": "Animation",
           "location": "Main Menu > Object/Pose > Animation > Rapid SDK",
           "description": "Quickly create driving relationships between properties",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/Rapid-SDK",
           "tracker_url": ""}

import blf
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import idprop

import copy
import math
from mathutils import Euler, Quaternion, Vector
import re


NAME = "rapidSDK"
EXTRAPOLATION = False
RANGE_KEY_HANDLES = 'VECTOR'
MID_KEY_HANDLES = 'AUTO_CLAMPED'
TOLERANCE = 0.000001
MESSAGE_POSITION = 'TOP'
MESSAGE_COLOR = (0.263, 0.723, 0.0)  # (0.545, 0.863, 0.0)
BORDER_WIDTH = 2

SEPARATOR = "::"
POSEBONE = "POSEBONE"
OBJECT = "OBJECT"
SHAPEKEY = "SHAPEKEY"

DEFAULT_PROPS = ["location", "rotation_euler", "rotation_quaternion", "rotation_axis_angle", "scale", "key_blocks", "modifiers"]


ANN_OUTSIDE = "Enable the extrapolation for the generated driver curves"
ANN_RANGE_HANDLES = "The default handle type for the driver's start and end keyframe points"
ANN_MID_HANDLES = "The default handle type for the driver's intermediate keyframe points"
ANN_TOLERANCE = "The minimum difference a value needs to be captured as a driver key. Default: {}".format(TOLERANCE)
ANN_MESSAGE_POSITION = "The position of the on-screen message when in create or edit mode"
ANN_MESSAGE_COLOR = "Display color for the on-screen message when in create or edit mode (not gamma corrected)"
ANN_BORDER_WIDTH = "The width of the colored frame when in create or edit mode."


# Version specific vars.
SHADER_TYPE = 'UNIFORM_COLOR'
if bpy.app.version < (3, 4, 0):
    SHADER_TYPE = '2D_UNIFORM_COLOR'


def getViewSize():
    """Return the size of the 3d view exclusive the header area.

    :return: The size of the 3d view in pixels.
    :rtype: tuple(int, int)
    """
    size = None
    header = 0
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    size = (region.width, region.height)
                elif region.type == 'HEADER':
                    header += region.height
                elif region.type == 'TOOL_HEADER':
                    header += region.height
    return size[0], size[1]-header


class DrawInfo3D(object):
    """Class for drawing the status info during create and edit.
    """
    def __init__(self):
        """Variable initialization.
        """
        self.msg = ""
        self.handle = None
        self.driver = None
        self.driven = None

    def drawCallback(self, context):
        """Callback for drawing the info message.

        :param context: The current context.
        :type context: bpy.context
        """
        fontId = 0
        # The font size and positioning depends on the system's pixel
        # size.
        pixelSize = bpy.context.preferences.system.pixel_size

        # Get the size of the 3d view to be able to place the text
        # correctly.
        viewWidth, viewHeight = getViewSize()

        color = getPreferences().message_color_value
        # Gamma-correct the color.
        color = [pow(c, 0.454) for c in color]

        pos = getPreferences().message_position_value
        textPos = viewHeight
        if pos == 'TOP':
            textPos = textPos - 20 * pixelSize
        else:
            textPos = 18 * pixelSize

        fontSize = 11 * pixelSize
        textWidth, textHeight = blf.dimensions(fontId, self.msg)

        # Draw the message in the center at the top or bottom of the
        # screen.
        blf.position(fontId, viewWidth / 2 - textWidth / 2, textPos, 0)
        blf.size(fontId, int(fontSize))
        blf.color(fontId, color[0], color[1], color[2], 1.0)
        blf.draw(fontId, self.msg)

        # Draw the name of the objects in the lower left corner of the
        # screen.
        if len(self.driven):
            lines = ["Driver:", self.driver, "", "Driven:"]
            lines.extend(self.driven)

            lineHeight = fontSize * 1.45
            xPos = 20 * pixelSize
            yPos = 20 * pixelSize
            for i in reversed(range(len(lines))):
                blf.position(fontId, xPos, yPos, 0)
                blf.draw(fontId, lines[i])
                yPos += lineHeight

        # Draw the frame.
        # https://docs.blender.org/api/blender2.8/gpu.html?highlight=gpu#module-gpu
        border = getPreferences().border_width_value * pixelSize
        viewWidth -= 20 * pixelSize

        vertices = ((1, 1), (viewWidth, 1), (viewWidth, 1+border), (1, 1+border),
                    (viewWidth, viewHeight), (viewWidth-border, viewHeight), (viewWidth-border, 1),
                    (1, viewHeight), (1, viewHeight-border), (viewWidth, viewHeight-border),
                    (1+border, 1), (1+border, viewHeight))
        indices = ((0, 1, 2), (0, 2, 3),
                   (1, 4, 5), (1, 5, 6),
                   (4, 7, 8), (4, 8, 9),
                   (7, 0, 10), (7, 10, 11))

        shader = gpu.shader.from_builtin(SHADER_TYPE)
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        shader.bind()
        shader.uniform_float("color", (color[0], color[1], color[2], 1.0))
        batch.draw(shader)

    def add(self, message="", driver="", driven=None):
        """Add the message to the 3d view and store the handler for
        later removal.

        :param message: The message to display on screen.
        :type message: str
        :param driver: The name of the driver to display.
        :type driver: str
        :param driven: The list of object names for the driven to
                       display.
        :type driven: str
        """
        if driven is None:
            driven = []
        self.msg = message
        self.driver = driver
        self.driven = driven

        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.drawCallback,
                                                             (bpy.context,),
                                                             'WINDOW',
                                                             'POST_PIXEL')

        self.updateView()

    def remove(self):
        """Remove the message from the 3d view.
        """
        if self.handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            self.handle = None
            self.updateView()

    def updateView(self):
        """Force a redraw of the current 3d view.
        """
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


# Global instance.
drawInfo3d = DrawInfo3D()


class RapidSDK(object):
    """Class managing the set driven key creation.
    """
    def __init__(self):
        """Variable initialization.
        """
        self.driver = None
        self.driven = None

        self.driverBase = {}
        self.driverCurrent = {}
        self.drivenBase = {}
        self.drivenCurrent = {}

        self.createMode = False
        self.editMode = False

    def execute(self):
        """Store the state of the current selection or create the driver
        setup based on the number of selected objects.
        """
        # Get the current selection.
        objects = objectToString(selectedObjects())
        active = objectToString(selectedObjects(active=True))
        if len(objects) and not active:
            drawInfo3d.remove()
            return {'WARNING'}, "No driving object selected"

        # --------------------------------------------------------------
        # Initiate
        # --------------------------------------------------------------
        # With two or more objects selected a new process gets started.
        if len(objects) > 1 and not self.createMode:
            self.createMode = True

            # Remove the active object from the list, which then only
            # contains driven objects.
            objects.remove(active)
            self.driver = active
            self.driven = objects

            # Get and store the current values as the driving base.
            self.driverBase = getCurrentValues(self.driver)[self.driver]
            self.drivenBase = getCurrentValues(self.driven)

            # ----------------------------------------------------------
            # Messages
            # ----------------------------------------------------------
            drivenMsg = ""
            if len(self.driven) > 1:
                drivenMsg = " (+ {} more)".format(len(self.driven)-1)

            driverName = stringToObject(self.driver).name
            drivenNames = [d.name for d in stringToObject(self.driven)]

            drawInfo3d.add("Record SDK", driverName, drivenNames)

            return {'INFO'}, "Starting driver setup: {} -> {}{}".format(driverName,
                                                                        drivenNames[0],
                                                                        drivenMsg)

        # --------------------------------------------------------------
        # Create the driver
        # --------------------------------------------------------------
        # If only one object is selected setup the driver.
        elif self.createMode:
            self.createMode = False
            drawInfo3d.remove()

            # Get the modified values to compare with the original.
            self.driverCurrent = getCurrentValues(self.driver)[self.driver]
            self.drivenCurrent = getCurrentValues(self.driven)

            # Get the properties for the driver and driven object which
            # have been modified.
            driverData = self.getDrivingProperty()
            drivenData = self.getDrivenProperty(create=True)

            # Check what can be used for the driver setup.
            if not len(driverData):
                return {'WARNING'}, "No driving properties changed or are already driving the target"

            if not len(drivenData):
                return {'WARNING'}, "No driven properties changed or are already been driven by the target"

            # Create the driving relationship.
            setupDriver(stringToObject(self.driver), driverData, drivenData)

            msg = "object" if len(self.driven) == 1 else "objects"
            return {'INFO'}, "Created driver for {} {}".format(len(self.driven), msg)

        # --------------------------------------------------------------
        # Edit mode
        # --------------------------------------------------------------
        elif len(objects) == 1 and not self.createMode:

            # A special case of selection which mostly happens with mesh
            # and bone selections in object mode.
            # For example, the driving bone can be selected in the
            # outliner but it's icon is not highlighted. Though the
            # armature is selected and the icon highlighted.
            # As a result of the selection filter there's only the mesh
            # in the list of selected objects but the active selection
            # is the armature.
            # But when editing the driver the selection and active
            # object needs to match.
            if active not in objects:
                return {'WARNING'}, "Selection inconclusive. Please check your selection"

            # ----------------------------------------------------------
            # Enter edit
            # ----------------------------------------------------------
            if not self.editMode:
                message = self.initEdit(active)
                if not message:
                    name = active.split(SEPARATOR)[-1]
                    drawInfo3d.add("Edit SDK: {}".format(name))
                    return {'INFO'}, "Editing driver for {}".format(name)
                else:
                    return message

            # ----------------------------------------------------------
            # Exit edit
            # ----------------------------------------------------------
            elif self.editMode:
                drawInfo3d.remove()
                # Even if there's only one driven object in edit mode
                # the driven is still a list for consistency.
                if active == self.driven[0]:
                    self.editMode = False

                    # Get the modified values to compare with the
                    # original.
                    self.drivenCurrent = getCurrentValues(self.driven)

                    # Get the properties which have been modified.
                    drivenData = self.getDrivenProperty(create=False)

                    if drivenData:
                        insertKey(self.driven[0], drivenData[self.driven[0]])
                        obj = stringToObject(self.driven[0])
                        message = {'INFO'}, "Updating driver curves for {}".format(obj.name)
                    else:
                        message = {'INFO'}, "Editing cancelled without any changes"

                    # Enable the driver animation curves.
                    setAnimationCurvesState(stringToObject(self.driven[0]), True)

                    return message

                # If the current object is not the last edited driven
                # object reset the last driven and start a new edit.
                else:
                    return self.resetDriverState(self.driven)

        # --------------------------------------------------------------
        # Reset the last driven objects
        # --------------------------------------------------------------
        # If nothing is selected reset the muted driver state for the
        # last driven object.
        elif not len(objects):
            drawInfo3d.remove()
            if self.driven:
                return self.resetDriverState(self.driven)
            else:
                return {'WARNING'}, "No driven objects selected"

    def getDrivingProperty(self):
        """Find which properties have been changed for the driver and
        filter all which cannot be used because they are already driving
        other properties of the same object.

        :return: A list with a list of values which can be used for
                 driving. Each item contains a list with the property,
                 the index and a tuple with the start and end values.
        :rtype: list(list(str, int, tuple(float, float)))
        """
        result = []

        # Compare which values have been changed.
        for key in self.driverCurrent.keys():
            value = self.driverCurrent[key]
            # In case of list-type properties the values need to be
            # extracted individually.
            if isinstance(value, (Euler, Quaternion, Vector, list, tuple,
                                  idprop.types.IDPropertyArray)):
                for i in range(len(value)):
                    baseValue = self.driverBase[key][i]
                    if not isClose(value[i], baseValue):
                        result.append([key, i, (baseValue, value[i])])
            # Skip the rotation mode key.
            elif isinstance(value, str):
                pass
            # Single-value properties.
            elif key not in ["shapeKeys", "modifiers"]:
                baseValue = self.driverBase[key]
                if not isClose(value, baseValue):
                    result.append([key, -1, (baseValue, value)])
            # Shape keys.
            # Example:
            # {'shapeKeys': {'Key': {'Basis': 0.0, 'smile': 0.0}}}
            elif key == "shapeKeys" and value is not None:
                name = list(value.keys())[0]
                for k in value[name].keys():
                    val = value[name][k]
                    baseValue = self.driverBase["shapeKeys"][name][k]
                    if not isClose(val, baseValue):
                        keyId = bpy.data.shape_keys[name]
                        src = {"shapeKeys": {"keyId": keyId, "name": k, "prop": "value"}}
                        result.append([src, -1, (baseValue, val)])
            # Modifiers
            # Example:
            # {'GeometryNodes': {'Input_3': 0.1, 'Input_4': 180.0}}
            elif key == "modifiers" and value is not None:
                for mod in value.keys():
                    for attr in value[mod].keys():
                        val = value[mod][attr]
                        baseValue = self.driverBase["modifiers"][mod][attr]
                        if isinstance(val, (idprop.types.IDPropertyArray, list)):
                            for i in range(len(val)):
                                if not isClose(val[i], baseValue[i]):
                                    src = {"modifier": {"name": mod, "prop": attr}}
                                    result.append([src, i, (baseValue[i], val[i])])
                        else:
                            if not isClose(val, baseValue):
                                src = {"modifier": {"name": mod, "prop": attr}}
                                result.append([src, -1, (baseValue, val)])

        return result

    def getDrivenProperty(self, create=True):
        """Find which properties have been changed for the driven and
        filter all which cannot be used because they are already driven
        or have animation.

        :param create: True, if a new driver setup should be created and
                       therefore existing driven properties should be
                       excluded.
                       False, to include driven properties when editing.
        :type create: bool

        :return: A list with a list of values which can be used for
                 being driven. Each item contains a list with the
                 property, the index and a tuple with the start and end
                 values.
                 The list is stored as the value with the object as the
                 key.
        :rtype: dict(list(list(str, int, tuple(float, float))))
        """
        result = {}
        for obj in self.driven:
            result[obj] = self.getDrivenPropertyForObject(obj, create)
        return result

    def getDrivenPropertyForObject(self, obj, create):
        """Find which properties have been changed for the driven and
        filter all which cannot be used because they are already driven
        or have animation.

        :param obj: The name of the object to query.
        :type obj: str
        :param create: True, if a new driver setup should be created and
                       therefore existing driven properties should be
                       excluded.
                       False, to include driven properties when editing.
        :type create: bool

        :return: A list with a list of values which can be used for
                 being driven. Each item contains a list with the
                 property, the index and a tuple with the start and end
                 values.
        :rtype: list(list(str, int, tuple(float, float)))
        """
        drivenData = getDriver(obj)

        props = []

        # Compare which values have been changed.
        for key in self.drivenCurrent[obj].keys():
            value = self.drivenCurrent[obj][key]
            # In case of list-type properties the values need to be
            # extracted individually.
            if isinstance(value, (Euler, Quaternion, Vector, list, tuple,
                                  idprop.types.IDPropertyArray)):
                for i in range(len(value)):
                    baseValue = self.drivenBase[obj][key][i]
                    if not isClose(value[i], baseValue):
                        # Check, if the current value is already the
                        # target of a driving relationship.
                        if propertyIsAvailable(obj, drivenData, key, i, create):
                            props.append([key, i, (baseValue, value[i])])
            # Single-value properties.
            elif key not in ["shapeKeys", "modifiers"]:
                baseValue = self.drivenBase[obj][key]
                if not isClose(value, baseValue):
                    # Check, if the current value is already the target
                    # of a driving relationship.
                    if propertyIsAvailable(obj, drivenData, key, -1, create):
                        props.append([key, -1, (baseValue, value)])
            # Shape keys.
            # Example:
            # {'shapeKeys': {'Key': {'Basis': 0.0, 'smile': 0.0}}}
            elif key == "shapeKeys" and value is not None:
                name = list(value.keys())[0]
                for k in value[name].keys():
                    val = value[name][k]
                    baseValue = self.drivenBase[obj]["shapeKeys"][name][k]
                    if not isClose(val, baseValue):
                        # To query the availability of a shape key the
                        # shape key data block needs to be passed as the
                        # object.
                        if propertyIsAvailable(bpy.data.shape_keys[name],
                                               drivenData,
                                               k,
                                               -1,
                                               create):
                            keyId = bpy.data.shape_keys[name]
                            tgt = {"shapeKeys": {"keyId": keyId, "name": k, "prop": "value"}}
                            props.append([tgt, -1, (baseValue, val)])
            # Modifiers
            # Example:
            # {'GeometryNodes': {'Input_3': 0.1, 'Input_4': 180.0}}
            elif key == "modifiers" and value is not None:
                for mod in value.keys():
                    for attr in value[mod].keys():
                        val = value[mod][attr]
                        baseValue = self.drivenBase[obj]["modifiers"][mod][attr]
                        if isinstance(val, (idprop.types.IDPropertyArray, list)):
                            for i in range(len(val)):
                                if not isClose(val[i], baseValue[i]):
                                    # Check, if the current value is
                                    # already the target of a driving
                                    # relationship.
                                    if propertyIsAvailable(obj, drivenData, (mod, attr), i, create):
                                        tgt = {"modifier": {"name": mod, "prop": attr}}
                                        props.append([tgt, i, (baseValue[i], val[i])])
                        else:
                            if not isClose(val, baseValue):
                                if propertyIsAvailable(obj, drivenData, (mod, attr), -1, create):
                                    tgt = {"modifier": {"name": mod, "prop": attr}}
                                    props.append([tgt, -1, (baseValue, val)])

        return props

    def initEdit(self, obj):
        """Enter edit mode by disabling the driver curves and getting
        the current values of the driven object.

        :param obj: The name of the object to edit.
        :type obj: str

        :return: The info message about the reset.
        :rtype: tuple(str, str)
        """
        # Disable the driver animation curves.
        objInst = stringToObject(obj)
        if not setAnimationCurvesState(objInst, False):
            return {'INFO'}, "No drivers to edit for {}".format(objInst.name)

        self.editMode = True

        # The active object is the driven.
        self.driven = [obj]

        # Get and store the current values as the driving base.
        self.drivenBase = getCurrentValues(self.driven)

    def resetDriverState(self, objects):
        """Enable the driver animation curves for the driven objects.

        :param objects: The names of the objects to reset the driver
                        state for.
        :type objects: list(bpy.types.Object)

        :return: The info message about the reset.
        :rtype: tuple(str, str)
        """
        names = []
        for obj in objects:
            obj = stringToObject(obj)
            setAnimationCurvesState(obj, True)
            names.append(obj.name)
        self.driven = None
        self.editMode = False
        return {'INFO'}, "Reset driver curves for {}".format(", ".join(names))


# Global instance.
rapidSDK = RapidSDK()


def selectedObjects(active=False):
    """Return the currently selected objects. In case of an armature
    return the selected bones when in edit or pose mode.

    :param active: Return only the currently active object.
    :type active: bool

    :return: The list of selected objects.
    :rtype: bpy.data.objects
    """
    sel = []
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            if bpy.context.object.mode == 'POSE':
                if active:
                    activeBone = bpy.context.active_pose_bone
                    if not activeBone:
                        bones = selectedBones(obj)
                        poseBones = bpy.context.selected_pose_bones
                        for b in bones:
                            if b not in poseBones:
                                return b
                    else:
                        return bpy.context.active_pose_bone
                else:
                    sel.extend(selectedBones(obj))
            elif bpy.context.object.mode == 'EDIT':
                if active:
                    return bpy.context.active_bone
                else:
                    sel.extend(bpy.context.selected_bones)
            else:
                bones = selectedBones(obj)
                if active:
                    if bpy.context.active_object == obj:
                        if len(bones) and bpy.context.active_object == obj:
                            return bones[0]
                        else:
                            return obj
                else:
                    if len(bones):
                        sel.extend(selectedBones(obj))
                    else:
                        sel.append(obj)
        else:
            if active and obj == bpy.context.active_object:
                return obj
            else:
                sel.append(obj)
    return sel


def selectedBones(armature):
    """Get a list of all selected pose bones from the given armature
    object even if they are hidden.

    :param armature: The armature object.
    :type armature: bpy.types.Object

    :return: A list with all selected bones.
    :rtype: list(bpy.types.PoseBone)
    """
    sel = []
    for bone in getArmatureData(armature).bones:
        if bone.select:
            sel.append(armature.pose.bones[bone.name])
    return sel


def objectToString(objects):
    """Convert the given object or list of objects to a name string.
    In case of a pose bone it's a delimited string of the armature name
    and the bone name.

    :param objects: The object or list of objects to convert.
    :type objects: bpy.types.Object or list(bpy.types.Object)

    :return: The name or list of names.
    :rtype: str or list(str)
    """
    isArray = True
    if not isinstance(objects, list):
        isArray = False
        objects = [objects]

    items = []
    for obj in objects:
        if isinstance(obj, bpy.types.PoseBone):
            items.append(SEPARATOR.join([POSEBONE, obj.id_data.name, obj.name]))
        elif isinstance(obj, bpy.types.Key):
            items.append(SEPARATOR.join([SHAPEKEY, obj.name]))
        else:
            items.append(SEPARATOR.join([OBJECT, obj.name]))

    if not isArray and len(items):
        return items[0]
    return items


def stringToObject(names):
    """Return the given name or list of names to objects.

    :param names: The name or list of object names.
    :type names: str or list(str)

    :return: The object or list of objects.
    :rtype: bpy.types.Object or list(bpy.types.Object)
    """
    isArray = True
    if not isinstance(names, list):
        isArray = False
        names = [names]

    items = []
    for name in names:
        elements = name.split(SEPARATOR)
        if len(elements):
            if len(elements) > 2:
                items.append(bpy.data.objects[elements[1]].pose.bones[elements[2]])
            else:
                if elements[0] == OBJECT:
                    items.append(bpy.data.objects[elements[1]])
                elif elements[0] == SHAPEKEY:
                    items.append(obj.data.shape_keys[elements[1]])

    if not isArray and len(items):
        return items[0]
    return items


def getArmatureData(obj):
    """Return the armature data block which is used by the given
    armature object.

    :param obj: The armature object.
    :type obj: bpy.types.Object

    :return: The armature data block.
    :rtype: bpy.data.Armature
    """
    for i in range(len(bpy.data.armatures)):
        if obj.user_of_id(bpy.data.armatures[i]):
            return bpy.data.armatures[i]


def getCurrentValues(objects):
    """Return a dictionary with all properties and their current values
    of the given object, wrapped in a dictionary with the object as the
    key and the data as its value.

    :param objects: The object names to get the data from.
    :type objects: str or list(str)

    :return: A dictionary with all properties as keys and their values
             for each object.
    :rtype: dict(dict())
    """
    if not isinstance(objects, list):
        objects = [objects]

    allData = {}

    for i in range(len(objects)):
        # Convert the name to an object.
        obj = stringToObject(objects[i])

        data = {}
        # --------------------------------------------------------------
        # bpy.types.Object
        # --------------------------------------------------------------
        if not isinstance(obj, bpy.types.Key):
            data["location"] = obj.location
            if obj.rotation_mode == 'AXIS_ANGLE':
                values = obj.rotation_axis_angle
                data["rotation_axis_angle"] = (values[0], values[1], values[2], values[3])
            elif obj.rotation_mode == 'QUATERNION':
                data["rotation_quaternion"] = obj.rotation_quaternion
            else:
                data["rotation_euler"] = obj.rotation_euler
            data["scale"] = obj.scale

            # Get the custom properties.
            for prop in customProperties(obj):
                value = obj.get(prop)
                if isinstance(value, idprop.types.IDPropertyArray):
                    data[prop] = [i for i in value]
                else:
                    data[prop] = value

            # Get the shape keys for meshes and curves.
            data["shapeKeys"] = getShapeKeys(obj)

            # Get the modifiers.
            data["modifiers"] = getModifierProperties(obj)[obj]

        # --------------------------------------------------------------
        # bpy.types.Key
        # --------------------------------------------------------------
        # If the given object is a shapes key only the shapes and their
        # values are of importance. This is only the case when querying
        # the current driver values for inserting a new key. Therefore
        # the result is different from getting the values upon
        # initializing.
        else:
            for block in obj.key_blocks:
                data[block.name] = block.value

        # The key for the data set is not the object but the string
        # representation.
        allData[objects[i]] = copy.deepcopy(data)

    return allData


def customProperties(obj):
    """Return a list with the custom properties of the given object.

    :param obj: The object to get the properties from.
    :type obj: bpy.types.Object

    :return: The list with the custom properties.
    :rtype: list(str)
    """
    props = []
    for prop in obj.keys():
        if prop not in '_RNA_UI' and isinstance(obj[prop], (int, float, list)):
            props.append(prop)
    return props


def hasShapeKeys(obj):
    """Return, if the given object has shape keys.

    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: True, if the object has shape keys.
    :rtype: bool
    """
    if obj.id_data.type in ['MESH', 'CURVE']:
        return True if obj.data.shape_keys else False
    else:
        return False


def shapeKeyName(obj):
    """Return the name of the shape key data block if the object has
    shape keys.

    :param obj: The mesh or curve object to query.
    :type obj: bpy.types.Object

    :return: The name of the shape key data block.
    :rtype: str
    """
    if hasShapeKeys(obj):
        return obj.data.shape_keys.name
    return ""


def shapeKeyProperties(obj):
    """Get the names of all shape key properties.

    :param obj: The mesh or curve object to query.
    :type obj: bpy.types.Object

    :return: A dictionary with all property names of the shape keys.
    :rtype: dict()
    """
    props = {}
    if hasShapeKeys(obj):
        for prop in obj.data.shape_keys.key_blocks:
            props[prop.name] = prop.value
    return props


def getShapeKeys(obj):
    """Get all shape key data from the given object.

    :param obj: The mesh or curve object to query.
    :type obj: bpy.types.Object

    :return: A dictionary with the object as the key and, if shape keys
             are present, as the value a dictionary with the name of the
             shape key data block and the properties and values.

             Example:
             {'Key': {'Basis': 0.0, 'smile': 0.0}}
    :rtype: dict(dict)
    """
    keys = None
    if hasShapeKeys(obj):
        keys = {shapeKeyName(obj): shapeKeyProperties(obj)}
    return keys


def getModifierProperties(obj):
    """Get all modifier properties from the given object.

    :param obj: The mesh or curve object to query.
    :type obj: bpy.types.Object

    :return: A dictionary with the object as the key and for each
             modifier a dictionary with the properties and values.
    :rtype: dict(dict)
    """
    modifier = {obj: None}
    if "modifiers" not in dir(obj):
        return modifier

    data = {}
    for mod in obj.modifiers:
        props = {}

        # The properties of a geometry nodes modifier are similar to
        # custom properties and need to be handled differently.
        if isinstance(mod, bpy.types.NodesModifier):
            for item in mod.keys():
                value = mod[item]
                # Each input  of a geometry nodes modifier
                # has three items:
                # Input_9
                # Input_9_use_attribute
                # Input_9_attribute_name
                # Only the actual input value, the first, is of
                # interest.
                skipItems = ["_use_attribute", "_attribute_name"]
                isInputOnly = not any(s in item for s in skipItems)
                if isinstance(value, (int, float, idprop.types.IDPropertyArray)) and isInputOnly:
                    if isinstance(value, idprop.types.IDPropertyArray):
                        props[item] = [i for i in value]
                    else:
                        props[item] = value
        else:
            for item in dir(mod):
                if not item.startswith("__") and item not in ["bl_rna", "rna_type"]:
                    value = eval("mod.{}".format(item))
                    if isinstance(value, (int, float)):
                        props[item] = value

        # Store the modifier with the name as the key and the property
        # dictionary as the value.
        data[mod.name] = props

    return {obj: data}


def propertyIsAvailable(obj, drivenData, prop, index, create=True):
    """Return True, if the property of the given object is available for
    creating a driver in create mode or editing an existing driver.

    :param obj: The object or name of the object to evaluate.
    :type obj: bpy.types.Object or str
    :param drivenData: A list of dictionaries containing all driving data.
    :type drivenData: list(dict)
    :param prop: The name of the property.
    :type prop: str
    :param index: The index of the property.
    :type index: int
    :param create: True, if checking for the create mode.
    :type create: bool

    :return: True, if the property is available for the given mode.
    :rtype: bool
    """
    if isinstance(obj, str):
        obj = stringToObject(obj)

    isDriven = propertyIsDriven(obj, prop, index, drivenData)
    isAnimated = propertyIsAnimated(obj, prop, index)

    if create:
        return not (isDriven or isAnimated)
    else:
        # In edit mode the animated state is not of interest because a
        # property can only either be driven or animated. And if it's
        # not driven it's not relevant for edit mode.
        return isDriven


def propertyIsDriven(obj, prop, index, drivenData):
    """Return, if the given property is driven.

    :param obj: The object to evaluate.
    :type obj: bpy.types.Object
    :param prop: The name of the property.
    :type prop: str
    :param index: The index of the property.
    :type index: int
    :param drivenData: A list of dictionaries containing all driven
                       data.
    :type drivenData: list(dict)

    :return: True, if the given property is already driven.
    :rtype: bool
    """
    for item in drivenData:
        if isinstance(obj, bpy.types.Key):
            if item["driven"]["object"] == obj.key_blocks[prop]:
                return True
        else:
            # Standard and custom properties.
            if not isinstance(prop, tuple):
                propName = prop
            # Modifier properties.
            else:
                propName = buildPropertyString(obj, prop[0], prop[1])

            if (item["driven"]["prop"] == propName and
                    item["driven"]["index"] == index and
                    item["driven"]["object"] == obj):
                return True

    return False


def setAnimationCurvesState(obj, enable=True):
    """Set the muted state for all driver fCurves for the given object.

    :param obj: The object to set the mute state for.
    :type obj: bpy.types.Object
    :param enable: True, if the driver fCurves should be unmuted.
    :type enable: bool

    :return: True, if animation curves have been toggled.
    :rtype: bool
    """
    result = False

    for driver in getDriver(obj):
        if driver["driven"]["object"] == obj:
            driver["driven"]["fCurve"].mute = not enable
            result = True

    if hasShapeKeys(obj):
        for driver in getDriver(bpy.data.shape_keys[shapeKeyName(obj)]):
            driver["driven"]["fCurve"].mute = not enable
            result = True

    return result


def animationCurves(obj):
    """Return a list of properties which are animated by an animation
    curve.

    :param obj: The object to get the properties from.
    :type obj: bpy.types.Object

    :return: A list of dictionaries which contain the name of the
             animated property and the index.
    :rtype: list(dict)
    """
    obj = obj.id_data
    data = []
    if obj.animation_data and obj.animation_data.action:
        for curve in obj.animation_data.action.fcurves:
            data.append({"prop": curve.data_path, "index": curve.array_index})
    return data


def propertyIsAnimated(obj, prop, index):
    """Return, if the given property on the given object is animated.

    :param obj: The object to get the animation from.
    :type obj: bpy.types.Object
    :param prop: The name of the property.
    :type prop: str
    :param index: The index of the property.
    :type index: int

    :return: True, if the given property is animated.
    :rtype: bool
    """
    for anim in animationCurves(obj):
        if isinstance(obj, bpy.types.Key):
            if anim["prop"] == obj.key_blocks[prop].value:
                return True
        else:
            if not isinstance(prop, tuple):
                if anim["prop"] in [prop, '["{}"]'.format(prop)]:
                    if index == -1 or anim["index"] == index:
                        return True
            # Modifier
            else:
                propName = buildPropertyString(obj, prop[0], prop[1])
                if anim["prop"] == propName:
                    if index == -1 or anim["index"] == index:
                        return True

    return False


def getDriverIndex(obj, prop, index):
    """Return the animation data block and driver index the property is
    driven by.

    :param obj: The object to get the data from.
    :type obj: bpy.types.Object
    :param prop: The name of the property.
    :type prop: str
    :param index: The index of the property.
    :type index: int

    Example:
    bpy.types.Object location 0
    bpy.types.Object {'shapeKeys': {'keyId': bpy.data.shape_keys['Key'], 'name': 'taper', 'prop': 'value'}} -1

    :return: The basic data block and index of the driver.
             Since objects and key shapes have a different path to the
             animation data the related data block is passed along with
             the index.
    :rtype: tuple(bpy.types.Object/Key, int) or None
    """
    # In case of a shape key the driver isn't located on the object but
    # the shape keys data block.
    if isinstance(prop, dict):
        if "shapeKeys" in prop:
            data = getDriver(prop["shapeKeys"]["keyId"])
            for d in data:
                # Check, if the current shape name matches the name of the
                # key block.
                if prop["shapeKeys"]["name"] == d["driven"]["object"].name:
                    return prop["shapeKeys"]["keyId"], d["driverIndex"]
        elif "modifier" in prop:
            data = getDriver(obj)

            propName = buildPropertyString(obj,
                                           prop["modifier"]["name"],
                                           prop["modifier"]["prop"])

            for d in data:
                if (d["driven"]["object"] == obj and
                        d["driven"]["index"] == index and
                        d["driven"]["prop"] == propName):
                    return obj.id_data, d["driverIndex"]

    # In case of an armature the given object is the pose bone. To get
    # the driver data the actual armature object needs to get passed.
    # Edit: The armature object gets extracted when querying the data
    # because otherwise there wouldn't be a way to compare the object
    # and target object in getDriver().
    else:
        data = getDriver(obj)
        for d in data:
            # Custom properties are contained in the data set as
            # '["open"]'. Therefore simply find if the name is
            # contained.
            if (d["driven"]["object"] == obj and
                    prop in d["driven"]["prop"] and
                    d["driven"]["index"] == index):
                return obj.id_data, d["driverIndex"]


def buildPropertyString(obj, name, prop):
    """Create and return a property string which includes the modifier
    and property depending on the type of modifier.

    The formatting of modifier property strings for drivers depends on
    the type of modifier. Standard modifiers have their properties
    dot-separated, whereas geometry node modifiers have custom-like
    bracketed properties. Therefore it's necessary to check if the
    property is tied to the modifier by checking all included properties
    with dir().

    :param obj: The object to get the data from.
    :type obj: bpy.types.Object
    :param name: The name of the modifier.
    :type name: str
    :param prop: The name of the property.
    :type prop: str

    :return: The complete string representing the property.
    :rtype: str
    """
    mod = eval('obj.modifiers["{}"]'.format(name))
    if prop not in dir(mod):
        return 'modifiers["{}"]["{}"]'.format(name, prop)
    else:
        return 'modifiers["{}"].{}'.format(name, prop)


def getDriver(obj):
    """Return all necessary driving data for the given object.

    :param obj: The object or name of the object to get the data from.
    :type obj: bpy.types.Object or str

    :return: A list of dictionaries containing all driving data.
    :rtype: list(dict)
    """
    if isinstance(obj, str):
        obj = stringToObject(obj)

    baseObj = obj.id_data
    driver = []
    if isinstance(baseObj, bpy.types.Object):
        # Try, in case an object has no driver data.
        try:
            for index, drv in enumerate(baseObj.animation_data.drivers):
                target = getDrivenObject(baseObj, drv)
                if target == obj:
                    data = getDriverData(drv, target)
                    data["driverIndex"] = index
                    driver.append(data)
        except AttributeError:
            pass

        # Check for any shape key data.
        name = shapeKeyName(baseObj)
        if name:
            if bpy.data.shape_keys[name].animation_data:
                for index, drv in enumerate(bpy.data.shape_keys[name].animation_data.drivers):
                    target = getDrivenObject(bpy.data.shape_keys[name], drv)
                    data = getDriverData(drv, target)
                    data["driverIndex"] = index
                    driver.append(data)

    elif isinstance(baseObj, bpy.types.Key):
        if baseObj.animation_data:
            for index, drv in enumerate(baseObj.animation_data.drivers):
                target = getDrivenObject(baseObj, drv)
                data = getDriverData(drv, target)
                data["driverIndex"] = index
                driver.append(data)

    return driver


def getDrivenObject(obj, animDriver):
    """Get the object which is affected by the given animation driver.

    :param obj: The driving object.
    :type obj: bpy.types.Object
    :param animDriver: The animation driver to query the affected object
                       from.
    :type animDriver: bpy.types.FCurve

    :return: The affected object.
    :rtype: bpy.types.Object
    """
    items = animDriver.data_path.split("\"")
    if getattr(obj, "type", "") == 'ARMATURE':
        return bpy.data.objects[obj.name].pose.bones[items[1]]
    elif isinstance(obj, bpy.types.Key):
        # For a shape key the data path is: key_blocks["smile"].value
        return bpy.data.shape_keys[obj.name].key_blocks[items[1]]
    else:
        return obj


def getDriverData(driver, targetObj):
    """Return a list with all driver related data for the given
    AnimDataDriver of the related object.
    Each set of data is wrapped in a dictionary containing info about
    the driven property and the diving variables, properties and
    objects.

    :param driver: The driving fCurve.
    :type driver: bpy.types.FCurve
    :param targetObj: The affected object.
    :type targetObj: bpy.types.Object

    :return: A list of dictionaries containing all data for the driver.
    :rtype: list(dict)

    Return example:
    [
        {
            'driven': {'prop': 'location', 'index': 0, 'fCurve': bpy.types.FCurve},
            'keys':
                [
                    {'time': 0.0, 'value': 0.0},
                    {'time': 1.0, 'value': -1.0}
                ],
            'driver':
                [
                    {'variable': 'location',
                     'source':
                         [
                            {'prop': 'location',
                             'index': 2,
                             'object': bpy.data.objects['Empty']}
                         ]}
                ]
        }
    ]
    """
    keys = []
    for key in driver.keyframe_points:
        time, value = key.co
        keys.append({"time": time, "value": value})

    data = []
    for var in driver.driver.variables:
        name = var.name
        varData = []
        for target in var.targets:
            # In case of a pose bone remove the bone part of the
            # property name.
            # Example: pose.bones["Bone.001"].rotation_quaternion[0]
            #          pose.bones["main_ctrl"]["FK"]
            attr = target.data_path.replace("'", "\"")
            bone = ""
            if attr.startswith("pose.bones") and getattr(target.id, "type", "") == 'ARMATURE':
                # Remove the leading pose bone part and the possible
                # period separator.
                attr = attr[attr.find("]")+1:]
                attr = re.sub(r"^\.", "", attr)
                # Extract the name of the bone.
                pathItems = target.data_path.split("\"")
                if len(pathItems) > 1:
                    bone = target.data_path.split("\"")[1]

            # In case the driver is a shape key the attribute needs
            # some cleanup: key_blocks["Key 1"].value
            # Remove everything except the property name which makes it
            # appear like a single custom property.
            if isinstance(target.id, bpy.types.Key):
                attr = attr.replace("key_blocks", "").split(".")[0]

            # Cleanup the property from a modifier.
            # modifiers["GeometryNodes"]["Input_2"]
            modName = ""
            if attr.startswith("modifiers"):
                parts = attr.split("][")
                # The modifier name is needed for editing the driver
                # curves to match against the list of drivers.
                modName = parts[0].replace("modifiers[", "").replace("\"", "")
                parts = parts[1:]
                attr = "".join("[{}]".format(p.replace("[", "").replace("]", "")) for p in parts)

            # Default property:
            #   location[2]
            # Custom Property:
            #   Single: ["expand"]
            #   Array: ["size"][1]

            # If it's a simple property put it in a list.
            attrItems = [attr]

            # A custom array property has two brackets.
            if "][" in attr:
                attrItems = attr.split("][")
            # A transform property has no quotes.
            elif "\"" not in attr:
                attrItems = attr.split("[")
            attrItems = [cleanVariable(i) for i in attrItems]

            index = -1
            if len(attrItems) == 2:
                index = int(attrItems[1])

            obj = target.id

            # Build the target dictionary.
            targetData = {"prop": attrItems[0],
                          "index": index,
                          "object": obj,
                          "bone": bone,
                          "modifier": modName}
            varData.append(targetData)

        data.append({"variable": name, "source": varData})

    # The array index represents the index of an array property, though
    # in case of a custom property it's 0. This interferes with the
    # fact that single property indices are usually -1. Therefore the
    # index needs to be corrected when it's a custom property.
    separator = ""
    if any(s in driver.data_path for s in DEFAULT_PROPS):
        separator = "."
    arrayIndex = driver.array_index

    # In case the target is a shape key it's necessary to get the parent
    # data block (bpy.types.Key) because the driver's data path contains
    # the key_blocks attribute which needs to be combined with the key
    # and not the shape key.
    objData = targetObj
    if isinstance(objData, (bpy.types.ShapeKey, bpy.types.PoseBone)):
        objData = targetObj.id_data

    # Query the property type in order to set the array index.
    # It's possible that some properties are not accounted for and
    # therefore it's unknown if the property is dot separated or not.
    # Because of this first try to with/without the separator and if it
    # fails try the reverse.
    # If both fail assume that it's a int/float type property.
    try:
        dataType = eval("objData{}{}".format(separator, driver.data_path))
    except NameError:
        try:
            if not len(separator):
                separator = "."
            else:
                separator = ""
            dataType = eval("objData{}{}".format(separator, driver.data_path))
        except NameError:
            dataType = 0
    if isinstance(dataType, (int, float)):
        arrayIndex = -1

    # To get the driven property it can be retrieved from the data path
    # by splitting with a period.
    # In case of a standard modifier the full data path is needed,
    # because it contains the modifier: modifiers["Bevel"].width
    dataPath = driver.data_path
    if not dataPath.startswith("modifiers"):
        dataPath = driver.data_path.split(".")[-1]

    channelData = {"driven": {"prop": dataPath,
                              "index": arrayIndex,
                              "fCurve": driver,
                              "object": targetObj},
                   "keys": keys,
                   "driver": data}

    return channelData


def cleanVariable(var):
    """Remove all quotes and brackets from the given variable name.

    :param var: The variable name to clean.
    :type var: str

    :return: The plain variable name.
    :rtype: str
    """
    for c in ["[", "]", "\""]:
        if c in var:
            var = var.replace(c, "")
    return var


def setupDriver(driver, driverData, drivenData):
    """Create the driver for each property which has changed.

    :param driver: The driving object.
    :type driver: bpy.types.Object
    :param driverData: A list of lists with the property, index and
                       tuple of start and end values.
    :type driverData: list(list(str, int, tuple(float, float)))
    :param drivenData: A list of lists with the property, index and
                       tuple of start and end values.
    :type drivenData: dict(list(str, int, tuple(float, float)))
    """
    for obj in drivenData:
        for prop in drivenData[obj]:
            addDriver(driver, driverData, stringToObject(obj), prop)


def addDriver(driver, driverData, driven, drivenData):
    """Create the driver and set up the fCurve.

    :param driver: The driving object.
    :type driver: bpy.types.Object
    :param driverData: A list of lists with the property, index and
                       tuple of start and end values.
    :type driverData: list(list(str, int, tuple(float, float)))
    :param driven: The driven object.
    :type driven: bpy.types.Object
    :param drivenData: A list with the property, index and tuple of
                       start and end values.
    :type drivenData: list(str, int, tuple(float, float))

    Based on:
    https://blender.stackexchange.com/questions/39127/how-to-put-together-a-driver-with-python
    """
    # Add the driver and set the type.
    # Multiple drivers require the type to be set to sum.
    drv = createDriver(driven, drivenData)
    drv.type = 'AVERAGE'
    if len(driverData) > 1:
        drv.type = 'SUM'

    # If the driver is a pose bone the driver id needs to be the
    # armature object.
    driver, bonePrefix = filterPoseBone(driver)

    # Create the variable/s for the driver/s.
    varName = "var"
    varIndex = 0
    minValue = 0
    maxValue = 0
    for driverItem in driverData:
        var = drv.variables.new()
        varIndex += 1
        var.name = "{}{}".format(varName, varIndex)

        # Process shape keys for the driver.
        driverString = ""
        if "shapeKeys" in driverItem[0]:
            driver, driverString = filterShapeKey(driver, driverItem)
        # Process the modifier for the driver.
        elif "modifier" in driverItem[0]:
            driverString = buildPropertyString(driver,
                                               driverItem[0]["modifier"]["name"],
                                               driverItem[0]["modifier"]["prop"])

        # Set the driving object.
        # If the driver is a shape key itself the driver type needs to
        # be set accordingly.
        if isinstance(driver, bpy.types.Key):
            var.targets[0].id_type = 'KEY'
        var.targets[0].id = driver

        # Set the property path.
        # It's important to differentiate between single and array
        # properties as well as custom properties.
        # Default property: location[2]
        # Custom Property:
        #   Single: ["expand"]
        #   Array: ["size"][1]
        # Shape key: key_blocks["Key 1"].value
        if driverItem[0] in DEFAULT_PROPS:
            prop = driverItem[0]
        else:
            prop = '["{}"]'.format(driverItem[0])

        idString = ""
        if driverItem[1] != -1:
            idString = "[{}]".format(driverItem[1])

        # Array
        if idString and not driverString:
            var.targets[0].data_path = "{}{}{}".format(bonePrefix, prop, idString)
        # Shape Key or Modifier
        elif driverString:
            var.targets[0].data_path = "{}{}".format(driverString, idString)
        # Single
        else:
            var.targets[0].data_path = "{}{}".format(bonePrefix, prop)

        # Get the min/max value for the driver curve points.
        # Add the values in case there are multiple drivers for the
        # property.
        minValue += driverItem[2][0]
        maxValue += driverItem[2][1]

    # Since all drivers have their individual indices by which they can
    # be addressed it's necessary to find the driver index which just
    # has been created.
    # It's necessary to clean up the property name because in case of a
    # pose bone the property name contains the pose bone as a prefix.
    # Example: pose.bones["Bone.002"].location
    driverBlock, driverId = getDriverIndex(driven,
                                           prop=drivenData[0],
                                           index=drivenData[1])
    if driverId is None:
        return

    # Delete the default modifier so that the fCurve can be edited.
    for mod in driverBlock.animation_data.drivers[driverId].modifiers:
        driverBlock.animation_data.drivers[driverId].modifiers.remove(mod)

    # Set the extrapolation.
    if getPreferences().outside_value:
        driverBlock.animation_data.drivers[driverId].extrapolation = 'LINEAR'

    # Create the keyframes and set the values.
    keyPoints = driverBlock.animation_data.drivers[driverId].keyframe_points

    handle = getPreferences().range_handle_value

    keyPoints.add(2)
    keyPoints[0].co = (minValue, drivenData[2][0])
    keyPoints[0].handle_left_type = handle
    keyPoints[0].handle_right_type = handle

    keyPoints[1].co = (maxValue, drivenData[2][1])
    keyPoints[1].handle_left_type = handle
    keyPoints[1].handle_right_type = handle

    # Update the keyframe data to reflect new keys.
    driverBlock.animation_data.drivers[driverId].update()


def filterPoseBone(obj):
    """Filter any pose bones and return the armature object since any
    driver relevant data is based on the armature and not the pose bone.

    For drivers a pose bone prefix gets generated which is used as the
    string for the driver source.

    :param obj: The driver or driven object.
    :type obj: bpy.types.Object

    :return: The armature object in case of a pose bone. For any other
             objects the data is simply passed through. Also, the bone
             prefix for the driver source as a string.
    :rtype: tuple(bpy.types.Object, str)
    """
    if isinstance(obj, bpy.types.PoseBone):
        # Add the pose bone prefix in case of a pose bone.
        bonePrefix = 'pose.bones["{}"].'.format(obj.name)
        # Get the armature object.
        armature = obj.id_data
        return armature, bonePrefix
    return obj, ""


def filterShapeKey(obj, data):
    """If the given driver is a shape key return it's data block and a
    string for the driver path. In all other cases return the object.

    :param obj: The driver object.
    :type obj: bpy.types.Object
    :param data: A list of lists with the property, index and
                 tuple of start and end values.
    :type data: list(list(str, int, tuple(float, float)))

    :return: The shape key data block and the string for the driver's
             data path.
    :rtype: tuple(bpy.types.Key, str)
    """
    if isinstance(data[0], dict):
        keyId = data[0]["shapeKeys"]["keyId"]
        name = data[0]["shapeKeys"]["name"]
        value = data[0]["shapeKeys"]["prop"]
        pathData = 'key_blocks["{}"].{}'.format(name, value)
        return keyId, pathData
    return obj, ""


def createDriver(obj, data):
    """Add a driver to the given property of the given object.

    :param obj: The driven object.
    :type obj: bpy.types.Object
    :param data: A list with the property, index and tuple of start and
                 end values.
                 Example:
                 [position, -1, (0.0, 0.5)]
                 ["shapeKeys": {"keyId": keyId, "name": blockName, "prop": "value"}}, -1, (0.0, 0.5)
                 ["modifier": {"name": "GeometryNodes", "prop": "Input_4"}}, -1, (180.0, 20.0)]
    :type data: list(str, int, tuple(float, float))

    :return: The created driver.
    :rtype: bpy.types.Driver
    """
    # If the property item (data[0]) is delivered as a dict the driver
    # gets created for a shape key.
    if isinstance(data[0], dict):
        if "shapeKeys" in data[0]:
            # Shape key example:
            # bpy.data.shape_keys['Key'].key_blocks["smile"].driver_add("value", -1).driver
            name = data[0]["shapeKeys"]["name"]
            block = data[0]["shapeKeys"]["keyId"].key_blocks[name]
            prop = data[0]["shapeKeys"]["prop"]
            return block.driver_add(prop, -1).driver
        elif "modifier" in data[0]:
            # Modifier example:
            # bpy.data.objects[""].modifiers[""].driver_add("levels", -1).driver
            name = data[0]["modifier"]["name"]
            prop = data[0]["modifier"]["prop"]
            mod = obj.modifiers[name]
            if mod.type == 'NODES':
                prop = '["{}"]'.format(prop)
            return obj.modifiers[name].driver_add(prop, data[1]).driver
    # Default and custom properties.
    else:
        if data[0] in ["location", "rotation_euler", "rotation_quaternion",
                       "rotation_axis_angle", "scale"]:
            return obj.driver_add(data[0], data[1]).driver
        # Custom property.
        else:
            return obj.driver_add('["{}"]'.format(data[0]), data[1]).driver


def insertKey(driven, drivenData):
    """Add a new keyframe to the driver curve based on the modified
    values of the driven object.
    If the driver values haven't changed the existing keyframe gets
    updated.

    :param driven: The name of the driven object.
    :type driven: str
    :param drivenData: A list with the property, index and tuple of
                       start and end values.
    :type drivenData: list(str, int, tuple(float, float))
    """
    drivenObj = stringToObject(driven)

    # Get the armature object from the pose bone.
    obj = drivenObj.id_data

    # Get all driving data from the armature.
    # Each driver is represented through a dictionary.
    driverData = getDriver(drivenObj)

    # Add the driving data from any shape keys.
    if hasShapeKeys(obj):
        driverData.extend(getDriver(bpy.data.shape_keys[shapeKeyName(obj)]))

    # From all driving data filter only the drivers which match the
    # current driven object and it's modified properties.
    filteredItems = {}
    for data in driverData:
        for prop in drivenData:
            if driverContainsDriven(drivenObj, prop, data):
                # Get the name of the armature object.
                driverObj = data["driver"][0]["source"][0]["object"]
                bone = data["driver"][0]["source"][0]["bone"]
                # If a bone name is defined get the name of the
                # armature and define the bone as the driver.
                if len(bone):
                    driverObj = bpy.data.objects[driverObj.name].pose.bones[bone]

                if driverObj not in filteredItems:
                    filteredItems[driverObj] = [data]
                else:
                    filteredItems[driverObj].append(data)

    # The driverData is now a dictionary sorted by the driving objects.
    # Since an object can be driven by multiple objects it's important
    # to get the sum of driving values before being able to set the
    # driven properties.
    driverData = filteredItems

    # Go through every driver of the changed properties.
    for driverObj in driverData:
        driverName = objectToString(driverObj)
        # Get the current property values of the driver.
        driverValues = getCurrentValues(driverName)[driverName]

        # Go through every driver of the driven object.
        for data in driverData[driverObj]:
            for prop in drivenData:
                # For every changed property value check if the property
                # is being driven by a driver and if the property
                # indices match.
                if driverContainsDriven(drivenObj, prop, data):
                    # Find the index of the driver for the property.
                    # The index is necessary for getting the keyframe
                    # data from the driving curve.
                    driverBlock, driverId = getDriverIndex(drivenObj,
                                                           prop=prop[0],
                                                           index=prop[1])

                    # Get the keyframe data for adding and editing the
                    # keys.
                    keyPoints = driverBlock.animation_data.drivers[driverId].keyframe_points

                    # To get the current value of the driving property
                    # go through the list of drivers and find the
                    # driving property and index in the list of driver
                    # sources.
                    dVal = 0
                    for d in data["driver"]:
                        for s in d["source"]:
                            # Object drivers.
                            if not isinstance(s["object"], bpy.types.Key):
                                # Use the property and index to get the
                                # current value from the driver.
                                if s["modifier"]:
                                    driverValues = driverValues["modifiers"][s["modifier"]]

                                if s["index"] == -1:
                                    dVal += driverValues[s["prop"]]
                                else:
                                    dVal += driverValues[s["prop"]][s["index"]]
                            # Shape key drivers.
                            else:
                                dVal += driverValues[s["prop"]]

                    # If the driving value hasn't changed the existing
                    # key needs to be updated.
                    update = False
                    minVal = None
                    maxVal = None
                    for i in range(len(keyPoints)):
                        pos = keyPoints[i].co
                        if isClose(pos[0], dVal):
                            update = True
                            keyPoints[i].co = (pos[0], prop[2][1])

                        # Get the min/max values:
                        minVal, maxVal = minMax(minVal, maxVal, pos[0], pos[0])

                    # If a driving value has been changed add a new key.
                    if not update:
                        # Add a new keyframe. It's added as a new entry
                        # at the end of the data set.
                        keyPoints.add(1)
                        index = len(keyPoints) - 1

                        keyPoints[index].co = (dVal, prop[2][1])
                        # If the new driver value is outside the current
                        # range use the start/end range handle type and
                        # not the mid handle type.
                        if minVal < dVal < maxVal:
                            handle = getPreferences().mid_handle_value
                        else:
                            handle = getPreferences().range_handle_value
                        keyPoints[index].handle_left_type = handle
                        keyPoints[index].handle_right_type = handle

                    # Update the keyframe data to reflect new keys.
                    data["driven"]["fCurve"].update()


def minMax(minVal, maxVal, v1, v2):
    """Update the given min/max values if the given new values are
    smaller/larger respectively.

    :param minVal: The current min value.
    :type minVal: float
    :param maxVal: The current max value.
    :type maxVal: float
    :param v1: The new min value.
    :type v1: float
    :param v2: The new max value.
    :type v2: float

    :return. A tuple with the updated min/max values.
    :rtype: tuple(float, float)
    """
    if not minVal:
        minVal = v1
    elif v1 < minVal:
        minVal = v1

    if not maxVal:
        maxVal = v2
    elif v2 > maxVal:
        maxVal = v2

    return minVal, maxVal


def driverContainsDriven(driven, prop, driverData):
    """Return, if the given changed driven property is contained in the
    given data set of the driver.

    :param driven: The driven object.
    :type driven: bpy.types.Object
    :param prop: A list with the property, index and tuple of start and
                 end values.
    :type prop: list(str, int, tuple(float, float))
    :param driverData: A list with all driving data of the object.
    :type driverData: list
    """
    # If the property is a shape key check if the key blocks match.
    if isinstance(prop[0], dict) and "shapeKeys" in prop[0]:
        shapeKey = prop[0]["shapeKeys"]["keyId"]
        name = prop[0]["shapeKeys"]["name"]

        if shapeKey.key_blocks[name] == driverData["driven"]["object"]:
            return True

    # Check if any default or custom property and index match with the
    # driver.
    else:
        if isinstance(prop[0], dict) and "modifier" in prop[0]:
            propName = buildPropertyString(driven,
                                           prop[0]["modifier"]["name"],
                                           prop[0]["modifier"]["prop"])
        else:
            propName = prop[0]

        if (driverData["driven"]["prop"] == propName and
                driverData["driven"]["index"] == prop[1] and
                driverData["driven"]["object"] == driven):
            return True

    return False


def isClose(v1, v2):
    """Return True, if the given values are the same within a tolerance
    value.

    :param v1: The first value to compare.
    :type v1: float
    :param v2: The second value to compare.
    :type v2: float

    :return: True, if the values are the same.
    :rtype: bool
    """
    return math.isclose(v1, v2, abs_tol=getPreferences().tolerance_value)


# ----------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------

class RAPIDSDK_OT_setup(bpy.types.Operator):
    """Operator class for running rapid SDK.
    """
    bl_idname = "rapidsdk.setup"
    bl_label = "Rapid SDK"
    bl_description = "Quickly create driving relationships between properties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = rapidSDK.execute()
        if result:
            self.report(result[0], result[1])

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

def animation_menu_item(self, context):
    """Draw the menu item.

    :param context: The current context.
    :type context: bpy.context
    """
    self.layout.separator()
    self.layout.operator(RAPIDSDK_OT_setup.bl_idname, text="Rapid SDK", icon='ANIM')


# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------

def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons[NAME].preferences
    return prefs


class RAPIDSDKPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = NAME

    handles = [('FREE', "Free", ""),
               ('ALIGNED', "Aligned", ""),
               ('VECTOR', "Vector", ""),
               ('AUTO', "Auto", ""),
               ('AUTO_CLAMPED', "Auto Clamped", "")]

    position = [('TOP', "Top", ""),
                ('BOTTOM', "Bottom", "")]

    outside_value: bpy.props.BoolProperty(name="Extrapolate Driver Curves",
                                          description=ANN_OUTSIDE,
                                          default=EXTRAPOLATION)
    range_handle_value: bpy.props.EnumProperty(name="Start/End Key Handles",
                                               description=ANN_RANGE_HANDLES,
                                               items=handles,
                                               default=RANGE_KEY_HANDLES)
    mid_handle_value: bpy.props.EnumProperty(name="Intermediate Key Handles",
                                             description=ANN_MID_HANDLES,
                                             items=handles,
                                             default=MID_KEY_HANDLES)
    tolerance_value: bpy.props.FloatProperty(name="Value Tolerance",
                                             description=ANN_TOLERANCE,
                                             default=TOLERANCE)
    message_position_value: bpy.props.EnumProperty(name="Message Position",
                                                   description=ANN_MESSAGE_POSITION,
                                                   items=position,
                                                   default=MESSAGE_POSITION)
    message_color_value: bpy.props.FloatVectorProperty(name="Message Color",
                                                       description=ANN_MESSAGE_COLOR,
                                                       subtype='COLOR',
                                                       default=MESSAGE_COLOR)
    border_width_value: bpy.props.IntProperty(name="Border Width",
                                              description=ANN_BORDER_WIDTH,
                                              default=BORDER_WIDTH)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "outside_value")
        col.prop(self, "range_handle_value")
        col.prop(self, "mid_handle_value")
        col.prop(self, "tolerance_value")
        col.prop(self, "message_position_value")
        col.prop(self, "message_color_value")
        col.prop(self, "border_width_value")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [RAPIDSDK_OT_setup,
           RAPIDSDKPreferences]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add the menu items.
    bpy.types.VIEW3D_MT_object_animation.append(animation_menu_item)


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Remove the message in the 3d view if any.
    drawInfo3d.remove()

    # Remove the menu items.
    bpy.types.VIEW3D_MT_object_animation.remove(animation_menu_item)


if __name__ == "__main__":
    register()
