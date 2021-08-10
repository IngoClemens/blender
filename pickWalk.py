"""
pickWalk
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

PickWalk adds the ability to navigate a hierarchy with custom keymaps to
quickly select parent objects or children or switch to child siblings.
Current selections can be expanded and it's possible to jump to the same
object on the opposite side based on a side identifier.

Keymaps are registered for the 3D view, Outliner, Graph Editor and
Dope Sheet.

------------------------------------------------------------------------

Usage:

Ctrl + Up Arrow: Select parent
Ctrl + Down Arrow: Select Child
Ctrl + Right Arrow: Select Next Child Sibling
Ctrl + Left Arrow: Select Previous Child Sibling

Ctrl + Shift + Arrow Key: Keep the current selection and add the parent
                          or child.
Ctrl + Alt + Left/Right Arrow: Select Opposite

------------------------------------------------------------------------

Changelog:

0.1.0 - 2021-08-10
      - First public release

------------------------------------------------------------------------
"""

bl_info = {"name": "PickWalk",
           "author": "Ingo Clemens",
           "version": (0, 1, 0),
           "blender": (2, 93, 0),
           "category": "Interface",
           "location": "3D View, Outliner, Graph Editor, Dope Sheet",
           "description": "Navigate through a hierarchy of objects",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/PickWalk",
           "tracker_url": ""}

import bpy

import re


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

LEFT_IDENTIFIER = ["left", "lft", "lt", "lf", "l"]
RIGHT_IDENTIFIER = ["right", "rgt", "rt", "rg", "r"]


# ----------------------------------------------------------------------
# General
# ----------------------------------------------------------------------

def isArmature(obj):
    """Return, if the given object is or belongs to an armature.

    :param obj: The object to test for armature relations.
    :type obj: bpy.object

    :return: True, if the object is or belongs to an armature.
    :rtype: bool
    """
    # Get the object of the current datablock.
    # In case of a non-armature object it basically returns the same
    # object but in case of a bone the armature object gets returned.
    data = obj.id_data
    # Get the BlendData object based on the objects name.
    dataObj = bpy.data.objects[data.name]
    return True if dataObj.type == 'ARMATURE' else False


def getDataObject(obj):
    """Return the given object as a BlendData object. In case of an
    armature the object gets converted accordingly.

    :param obj: The object to test for armature relations.
    :type obj: bpy.object

    :return: The BlendData object.
    :rtype: bpy.data.objects
    """
    if isArmature(obj):
        return bpy.data.objects[obj.id_data.name]
    return obj


def selectObject(obj):
    """Select the given object and make it active.

    Object selection depends on the type of object and the current mode,
    armatures in particular.

    :param obj: The object to select.
    :type obj: bpy.object
    """
    if isArmature(obj):
        dataObj = getDataObject(obj)
        if dataObj.mode == 'POSE':
            dataObj.data.bones[obj.name].select = True
        elif dataObj.mode == 'EDIT':
            obj.select = True
    else:
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active = obj


def currentSelection():
    """Return the currently selected objects. In case of an armature
    return the selected bones when in edit or pose mode.

    :return: The list of selected objects.
    :rtype: bpy.data.objects
    """
    if bpy.context.object.type == 'ARMATURE':
        if bpy.context.object.mode == 'POSE':
            return bpy.context.selected_pose_bones
        elif bpy.context.object.mode == 'EDIT':
            return bpy.context.selected_bones
        else:
            return bpy.context.selected_objects
    else:
        return bpy.context.selected_objects


def deselectAll():
    """Remove the current selection.

    Object selection depends on the type of object and the current mode,
    armatures in particular.
    """
    if bpy.context.object.type == 'ARMATURE':
        if bpy.context.object.mode == 'POSE':
            bpy.ops.pose.select_all(action='DESELECT')
        elif bpy.context.object.mode == 'EDIT':
            bpy.ops.armature.select_all(action='DESELECT')
        else:
            bpy.ops.object.select_all(action='DESELECT')
    else:
        bpy.ops.object.select_all(action='DESELECT')


def editBoneFromName(obj, name):
    """Return the editBone of the given armature object from the given
    name.

    :param obj: The armature object the bone belongs to.
    :type obj: bpy.object
    :param name: The name of the bone to return.
    :type name: str

    :return: The bone object or None:
    :rtype: bpy.object or None
    """
    # Get the BlendData object of the given armature or bone.
    dataObj = getDataObject(obj)
    # Based on the armature name, build a proper armature object to be
    # able to query the contained editBones.
    # EditBones are special because they cannot be accessed by their
    # name but rather by their indes.
    # Therefore it's necessary to go through the list of editBones and
    # compare their names until the right one is found.
    armature = bpy.data.armatures[dataObj.name]
    for bone in armature.edit_bones:
        if bone.name == name:
            return bone


def replaceSideIdentifier(name):
    """Replace the side identifier of the name with the opposite side.

    :param name: The name of the node.
    :type name: str

    :return: The node name with the replaced side identifier.
    :rtype: str
    """
    if not len(name):
        return name
    identifier = sideIdentifier(name)
    return name.replace(identifier[0], identifier[1])


def sideIdentifier(name):
    """Return side identifier of the given name.

    :param name: The name of the node.
    :type name: str

    :return: The side identifier and the opposite identifier.
    :rtype: tuple(str, str)
    """
    leftItems = LEFT_IDENTIFIER[:]
    rightItems = RIGHT_IDENTIFIER[:]

    # First only the prefixes and suffixes get processed because
    # otherwise any embedded strings, which could appear to be
    # identifiers can easily override the actual prefix or suffix.
    for i in range(len(leftItems)):

        # Loop through different capitalization cases.
        for j in range(3):
            left = leftItems[i]
            right = rightItems[i]
            if j == 1:
                left = left.capitalize()
                right = right.capitalize()
            elif j == 2:
                left = left.upper()
                right = right.upper()

            # Loop through prefix, suffix and embedding.
            for k in range(3):
                # prefix
                if k == 0:
                    Left = "{}_".format(left)
                    Right = "{}_".format(right)
                    if name.startswith(Left):
                        return Left, Right
                    elif name.startswith(Right):
                        return Right, Left

                # suffix
                elif k == 1:
                    Left = "_{}".format(left)
                    Right = "_{}".format(right)
                    if name.endswith(Left):
                        return Left, Right
                    elif name.endswith(Right):
                        return Right, Left

                # embedded
                elif k == 2:
                    Left = "_{}_".format(left)
                    Right = "_{}_".format(right)
                    # left
                    regex = re.compile(".{}.".format(Left))
                    if re.search(regex, name):
                        return Left, Right
                    # right
                    regex = re.compile(".{}.".format(Right))
                    if re.search(regex, name):
                        return Right, Left

    return "", ""


def selectSibling(next=True, extend=False, switchSide=False):
    """Select the next or previous sibling of the current object. If the
    object is the first or last child of it's parent the list order gets
    wrapped.

    :param next: True, if the next sibling in the list should be
                 selected.
    :type next: bool
    :param extend: True, if the current selection should be kept and the
                   sibling should be added to the list.
    :type extend: bool
    :param switchSide: True, if a side identifier should be used to
                       select an object on the other side.
    :type switchSide: bool
    """
    selection = currentSelection()
    deselectAll()

    # Define the direction.
    direction = +1
    if not next:
        direction = -1

    objects = []
    for obj in selection:
        if extend:
            objects.append(obj)

        # Without a side identifier.
        if not switchSide:
            parent = obj.parent
            if parent:
                children = parent.children
                # Find the current object in the list of children and
                # get the index of the next or previous child.
                index = children.index(obj)
                index = (index + direction) % len(children)
                objects.append(children[index])
            else:
                objects.append(obj)

        # With a side identifier.
        else:
            # Replace the side identifier and select the object if it
            # exists.
            oppositeName = replaceSideIdentifier(obj.name)
            if isArmature(obj):
                dataObj = getDataObject(obj)
                oppositeObj = None
                if dataObj.mode == 'POSE':
                    try:
                        oppositeObj = dataObj.data.bones[oppositeName]
                    except KeyError:
                        pass
                else:
                    oppositeObj = editBoneFromName(dataObj, oppositeName)
            else:
                oppositeObj = bpy.data.objects[oppositeName]
            if oppositeObj:
                objects.append(oppositeObj)
            else:
                objects.append(obj)

    for obj in objects:
        selectObject(obj)


# ----------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------

class PICKWALK_OT_hierarchyUp(bpy.types.Operator):
    """Operator class for walking up the hierarchy.

    Selects the parent of the current object.
    """
    bl_idname = "pickwalk.hierarchy_up"
    bl_label = "Pickwalk up"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Extend",
                                   description="Extend the selection")

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        selection = currentSelection()
        deselectAll()

        objects = []
        for obj in selection:
            if self.extend:
                objects.append(obj)

            parent = obj.parent
            if parent:
                objects.append(parent)
            else:
                objects.append(obj)

        for obj in objects:
            selectObject(obj)

        return {'FINISHED'}


class PICKWALK_OT_hierarchyDown(bpy.types.Operator):
    """Operator class for walking down the hierarchy.

    Selects the first child of the current object.
    """
    bl_idname = "pickwalk.hierarchy_down"
    bl_label = "Pickwalk down"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Extend",
                                   description="Extend the selection")

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        selection = currentSelection()
        deselectAll()

        objects = []
        for obj in selection:
            if self.extend:
                objects.append(obj)

            children = obj.children
            if len(children):
                objects.append(children[0])
            else:
                objects.append(obj)

        for obj in objects:
            selectObject(obj)

        return {'FINISHED'}


class PICKWALK_OT_hierarchyLeft(bpy.types.Operator):
    """Operator class for walking left the hierarchy.

    Selects the previous sibling of the current object. If the object is
    the first child the selection jumps to the last child of the parent.
    """
    bl_idname = "pickwalk.hierarchy_left"
    bl_label = "Pickwalk left"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Extend",
                                   description="Extend the selection")
    switchSide: bpy.props.BoolProperty(name="Switch Side",
                                       description="Switch to the opposite side")

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        selectSibling(next=False,
                      extend=self.extend,
                      switchSide=self.switchSide)

        return {'FINISHED'}


class PICKWALK_OT_hierarchyRight(bpy.types.Operator):
    """Operator class for walking right the hierarchy.

    Selects the next sibling of the current object. If the object is
    the last child the selection jumps to the first child of the parent.
    """
    bl_idname = "pickwalk.hierarchy_right"
    bl_label = "Pickwalk right"
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(name="Extend",
                                   description="Extend the selection")
    switchSide: bpy.props.BoolProperty(name="Switch Side",
                                       description="Switch to the opposite side")

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        selectSibling(next=True,
                      extend=self.extend,
                      switchSide=self.switchSide)

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [PICKWALK_OT_hierarchyUp,
           PICKWALK_OT_hierarchyDown,
           PICKWALK_OT_hierarchyLeft,
           PICKWALK_OT_hierarchyRight]

addon_keymaps = []


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    uiArea = [{"name": '3D View Generic', "space": 'VIEW_3D'},
              {"name": 'Outliner', "space": 'OUTLINER'},
              {"name": 'Graph Editor', "space": 'GRAPH_EDITOR'},
              {"name": 'Dopesheet', "space": 'DOPESHEET_EDITOR'}]

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for area in uiArea:
            km = kc.keymaps.new(name=area["name"], space_type=area["space"])
            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyUp.bl_idname, type='UP_ARROW', value='PRESS', ctrl=True)
            kmi.properties.extend = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyDown.bl_idname, type='DOWN_ARROW', value='PRESS', ctrl=True)
            kmi.properties.extend = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname, type='LEFT_ARROW', value='PRESS', ctrl=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname, type='RIGHT_ARROW', value='PRESS', ctrl=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyUp.bl_idname, type='UP_ARROW', value='PRESS', ctrl=True, shift=True)
            kmi.properties.extend = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyDown.bl_idname, type='DOWN_ARROW', value='PRESS', ctrl=True, shift=True)
            kmi.properties.extend = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname, type='LEFT_ARROW', value='PRESS', ctrl=True, shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname, type='RIGHT_ARROW', value='PRESS', ctrl=True, shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname, type='LEFT_ARROW', value='PRESS', ctrl=True, alt=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname, type='RIGHT_ARROW', value='PRESS', ctrl=True, alt=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname, type='LEFT_ARROW', value='PRESS', ctrl=True, alt=True, shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname, type='RIGHT_ARROW', value='PRESS', ctrl=True, alt=True, shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
