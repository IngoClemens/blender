"""
pickWalk
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

PickWalk adds the ability to navigate a hierarchy with custom keymaps to
quickly select parent objects or children or switch to child siblings.
Current selections can be expanded and it's possible to jump to the same
object on the opposite side based on a side identifier.

Pickwalking also works in edit mode with mesh and curve objects to
quickly navigate to the next point connected to the current selection.

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
Ctrl + Alt + Left/Right Arrow: Select Opposite. When in mesh edit mode
                               cycle through connected vertices.

------------------------------------------------------------------------

Changelog:

0.6.0 - 2022-10-15
      - Moved the keymaps from 3d view generic to 3d view.
      - Included up/down arrow to also walk over curve points.
      - Improvements to querying the current selection.
      - Minor typo fixes and code cleanup.

0.5.0 - 2022-02-17
      - Improved walking order for top level objects of a collection.

0.4.0 - 2021-08-18
      - Added the period character as a side identifier separator.
      - Armatures are not selected when walking over top level siblings.
      - Fixed: Error when walking to a sibling when the root bone of an
        armature is selected in pose or edit mode.
      - Fixed: Cycling over multiple vertices in a complex mesh can
        cause an error.

0.3.0 - 2021-08-17
      - Stability improvements for vertex cycling.

0.2.0 - 2021-08-17
      - Added the ability to walk through the top level objects of the
        related collection by pickwalking right/left.
      - Added pickwalking for mesh and curve objects in edit mode to
        walk to connected vertices and points.

0.1.0 - 2021-08-10
      - First public release

------------------------------------------------------------------------
"""

bl_info = {"name": "PickWalk",
           "author": "Ingo Clemens",
           "version": (0, 6, 0),
           "blender": (2, 93, 0),
           "category": "Interface",
           "location": "3D View, Outliner, Graph Editor, Dope Sheet",
           "description": "Navigate through a hierarchy of objects, mesh vertices or curve points",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/PickWalk",
           "tracker_url": ""}

import bpy
import bmesh
from bpy_extras import view3d_utils

import math
from mathutils import Vector
import re


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

LEFT_IDENTIFIER = ["left", "lft", "lt", "lf", "l"]
RIGHT_IDENTIFIER = ["right", "rgt", "rt", "rg", "r"]


# ----------------------------------------------------------------------
# General
# ----------------------------------------------------------------------

def activeEditMesh():
    """Return a list of the current mesh objects and bmeshes.

    :return: A list with tuples with the current mesh object and bmesh.
    :rtype: list(tuple(bpy.context.obj, BMesh))
    """
    meshes = []
    for obj in bpy.context.objects_in_mode:
        if obj.type == 'MESH':
            bm = bmesh.from_edit_mesh(obj.data)
            meshes.append((obj, bm))
    return meshes


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
    if isArmature(obj) and bpy.context.object.mode != 'OBJECT':
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
    if bpy.context.object:
        if bpy.context.object.type == 'ARMATURE':
            if bpy.context.object.mode == 'POSE':
                return bpy.context.selected_pose_bones
            elif bpy.context.object.mode == 'EDIT':
                return bpy.context.selected_bones
            else:
                return bpy.context.selected_objects
        else:
            return bpy.context.selected_objects
    else:
        return bpy.context.selected_objects


def deselectAll():
    """Remove the current selection.

    Object selection depends on the type of object and the current mode,
    armatures in particular.
    """
    if bpy.context.object:
        if bpy.context.object.type == 'ARMATURE':
            if bpy.context.object.mode == 'POSE':
                bpy.ops.pose.select_all(action='DESELECT')
            elif bpy.context.object.mode == 'EDIT':
                bpy.ops.armature.select_all(action='DESELECT')
            else:
                bpy.ops.object.select_all(action='DESELECT')
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

    # List of commonly used separators as tuples.
    # The first item is for prefix/suffix use, the second for use in a
    # regular expression, in case it's a special character which needs
    # escaping.
    separator = [(r"_", r"_"), (r".", r"\.")]

    for sep in separator:
        # First only the prefixes and suffixes get processed because
        # otherwise any embedded strings, which could appear to be
        # identifiers, can easily override the actual prefix or suffix.
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
                        Left = "{}{}".format(left, sep[0])
                        Right = "{}{}".format(right, sep[0])
                        if name.startswith(Left):
                            return Left, Right
                        elif name.startswith(Right):
                            return Right, Left

                    # suffix
                    elif k == 1:
                        Left = "{}{}".format(sep[0], left)
                        Right = "{}{}".format(sep[0], right)
                        if name.endswith(Left):
                            return Left, Right
                        elif name.endswith(Right):
                            return Right, Left

                    # embedded
                    elif k == 2:
                        Left = "{}{}{}".format(sep[1], left, sep[1])
                        Right = "{}{}{}".format(sep[1], right, sep[1])
                        # left
                        regex = re.compile(".{}.".format(Left))
                        if re.search(regex, name):
                            return Left, Right
                        # right
                        regex = re.compile(".{}.".format(Right))
                        if re.search(regex, name):
                            return Right, Left

    return "", ""


def selectSibling(toNext=True, extend=False, switchSide=False):
    """Select the next or previous sibling of the current object. If the
    object is the first or last child of it's parent the list order gets
    wrapped.

    :param toNext: True, if the next sibling in the list should be
                   selected.
    :type toNext: bool
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
    if not toNext:
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
                objects.extend(worldObject(obj, toNext=toNext))

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


def walkComponents(context, x=1, y=0, extend=False, cycle=False, toNext=True):
    """Walk over the connected components. The walking is based on
    vertices. If another selection mode is active the current selection
    will be converted.

    :param context: The current context.
    :type context: bpy.context
    :param x: The x direction to walk.  1: Right
                                       -1: Left
                                        0: Off
    :type x: int
    :param y: The y direction to walk.  1: Up
                                       -1: Down
                                        0: Off
    :type y: int
    :param extend: True, if the current selection should be kept and the
                   sibling should be added to the list.
    :type extend: bool
    :param cycle: True, to only cycle through connected vertices in case
                  a specific vertex cannot be reached.
    :type cycle: bool
    :param toNext: True, if the toNext connected vertex should be
                   selected.
    :type toNext: bool

    :return: True, if the next component could be selected. False, if
             the object is not a mesh in edit mode.
    :rtype: bool
    """
    if bpy.context.object.type == 'MESH' and bpy.context.object.mode == 'EDIT':
        walkMeshComponents(context, x, y, extend, cycle, toNext)
        return True
    elif bpy.context.object.type == 'CURVE' and bpy.context.object.mode == 'EDIT':
        walkCurveComponents(extend, toNext)
        return True
    else:
        return False


def walkCurveComponents(extend=False, toNext=True):
    """Walk over the curve components.

    :param extend: True, if the current selection should be kept and the
                   sibling should be added to the list.
    :type extend: bool
    :param toNext: True, if the toNext connected vertex should be
                   selected.
    :type toNext: bool
    """
    # Define the direction.
    direction = +1
    if not toNext:
        direction = -1

    for obj in bpy.context.objects_in_mode:
        pointData = None
        curveType = None

        # NURBS curve
        if len(obj.data.splines.active.points):
            pointData = obj.data.splines.active.points
            curveType = "nurbs"
        # Bezier curve
        elif len(obj.data.splines.active.bezier_points):
            pointData = obj.data.splines.active.bezier_points
            curveType = "bezier"

        if pointData is not None:
            indices = []
            if curveType == "nurbs":
                for i in range(len(pointData)):
                    if pointData[i].select:
                        indices.append((i + direction) % len(pointData))
                        if extend:
                            indices.append(i)
                        pointData[i].select = False
            else:
                for i in range(len(pointData)):
                    if pointData[i].select_control_point:
                        indices.append((i + direction) % len(pointData))
                        if extend:
                            indices.append(i)
                        pointData[i].select_control_point = False
                        pointData[i].select_left_handle = False
                        pointData[i].select_right_handle = False

            for index in indices:
                if curveType == "nurbs":
                    pointData[index].select = True
                else:
                    pointData[index].select_control_point = True
                    pointData[index].select_left_handle = True
                    pointData[index].select_right_handle = True


class Cycle(object):
    """Class to cycle through the connected vertices.
    """
    def __init__(self):
        # Dictionary for storing all the vertex data.
        self.obj = {}
        # Switch for walking to the next or previous vertex.
        self.increment = True
        # Status switch, which activates the cycling.
        self.active = False
        # Switch for starting at the first item of the connected
        # vertices.
        self.firstIndex = True

    def reset(self):
        """Reset everything.
        """
        self.obj = {}
        self.increment = True
        self.active = False
        self.firstIndex = True

    def isValid(self, obj):
        """Return, if the object is contained in the stored object list.

        Used to reset the cycling data when the object has been
        switched.

        :param obj: The current object.
        :type obj: bpy.object

        :return: True, if the object is listed.
        :rtype: bool
        """
        return obj in self.obj

    def setVertex(self, obj, vertices):
        """Set the vertex to get the connected vertices from.

        :param obj: The current object.
        :type obj: bpy.object
        :param vertices: The vertices to get the connected vertices
                         from.
        :type vertices: list(bpy.types.MeshVertices)
        """
        self.obj[obj] = {"vertex": [i.index for i in vertices]}
        self.obj[obj]["connected"] = []
        self.obj[obj]["current"] = []
        self.obj[obj]["connectedIndex"] = []
        # Collect all connected vertices.
        for vert in vertices:
            linked = []
            for edge in vert.link_edges:
                linked.append(edge.other_vert(vert).index)
            self.obj[obj]["connected"].append(linked)

    def update(self, obj, vertices):
        """Update the current vertex data based on the current
        selection.

        If cycling has been used as the last pickwalk action but the
        vertex selection has been changed by the user the data needs to
        be updated, otherwise cycling would still be based on the
        previous selection.

        :param obj: The current object.
        :type obj: bpy.object
        :param vertices: The vertices to get the connected vertices
                         from.
        :type vertices: list(bpy.types.MeshVertices)
        """
        # Create a status map to track which vertices are still in use
        # and which can be discarded.
        status = {}
        for i in range(len(self.obj[obj]["vertex"])):
            status[self.obj[obj]["vertex"][i]] = (i, False)

        # Compare, which of the currently selected vertices are already
        # part of a previous cycle.
        for vert in vertices:
            exists = False
            for i in range(len(self.obj[obj]["vertex"])):
                # Compare against the last selection.
                if self.obj[obj]["vertex"][i] == vert.index:
                    exists = True
                    # Flag the existing vertex as in use.
                    status[self.obj[obj]["vertex"][i]] = (i, True)
                # Compare against the connected vertices of the last
                # selection. Since a cycle walk changes the current
                # selection these need to be considered as well.
                for j in range(len(self.obj[obj]["connected"][i])):
                    if self.obj[obj]["connected"][i][j] == vert.index:
                        exists = True
                        # Flag the existing vertex as in use.
                        status[self.obj[obj]["vertex"][i]] = (i, True)

            # If the selected vertex isn't yet included add it to the
            # list and collect its data.
            if not exists:
                self.obj[obj]["vertex"].append(vert.index)
                linked = []
                for edge in vert.link_edges:
                    linked.append(edge.other_vert(vert).index)
                self.obj[obj]["connected"].append(linked)
                self.obj[obj]["current"].append(linked[0])
                self.obj[obj]["connectedIndex"].append(0)

        # Check, if any vertices form a previous cycle aren't used
        # anymore. Remove all unused vertices and their data.
        remove = []
        for key in status:
            if not status[key][1]:
                remove.append(status[key][0])
        remove.sort(reverse=True)
        for i in range(len(remove)):
            self.obj[obj]["vertex"].pop(remove[i])
            self.obj[obj]["connected"].pop(remove[i])
            self.obj[obj]["current"].pop(remove[i])
            self.obj[obj]["connectedIndex"].pop(remove[i])

    def toNext(self, obj):
        """Jump to the next vertex in the list of connected vertices.
        If the last/first vertex is reached jump tp the first/last
        vertex in the list.

        :param obj: The current object.
        :type obj: bpy.object
        """
        if self.active:
            if self.increment:
                direction = 1
            else:
                direction = -1

            for i in range(len(self.obj[obj]["connected"])):
                connected = self.obj[obj]["connected"][i]
                numConnected = len(connected)
                if self.firstIndex:
                    self.obj[obj]["current"].append(connected[0])
                    self.obj[obj]["connectedIndex"].append(0)
                else:
                    self.obj[obj]["connectedIndex"][i] = (self.obj[obj]["connectedIndex"][i] + direction) % numConnected
                    self.obj[obj]["current"][i] = connected[self.obj[obj]["connectedIndex"][i]]
            self.firstIndex = False

    def getCurrent(self, obj):
        """Return the indices of the current connected vertices.

        It's necessary to use the indices because the vertex objects
        change with every pickwalk because of the mesh updates.

        :param obj: The current object.
        :type obj: bpy.object

        :return: The indices of the current connected vertices.
        :rtype: list(int)
        """
        return self.obj[obj]["current"]


cycleConnected = Cycle()


def walkMeshComponents(context, x=1, y=0, extend=False, cycle=False, toNext=True):
    """Walk over the connected components. The walking is based on
    vertices. If another selection mode is active the current selection
    will be converted.

    :param context: The current context.
    :type context: bpy.context
    :param x: The x direction to walk.  1: Right
                                       -1: Left
                                        0: Off
    :type x: int
    :param y: The y direction to walk.  1: Up
                                       -1: Down
                                        0: Off
    :type y: int
    :param extend: True, if the current selection should be kept and the
                   sibling should be added to the list.
    :type extend: bool
    :param cycle: True, to only cycle through connected vertices in case
                  a specific vertex cannot be reached.
    :type cycle: bool
    :param toNext: True, if the next connected vertex should be
                   selected.
    :type toNext: bool
    """
    # Get all region data because component walking is performed in
    # screen space.
    region = context.region
    regionView3d = context.region_data

    # Go through all active edit meshes.
    for obj, bm in activeEditMesh():

        # Reset the cycling with a regular pickwalk so that cycling is
        # only active when used in succession.
        if not cycle:
            cycleConnected.reset()
        # Make sure that the current object is either known or reset
        # the cycling in case the object has been switched.
        if not cycleConnected.isValid(obj):
            cycleConnected.reset()

        # Get the object's matrix for calculating the screen position of
        # a vertex.
        mat = obj.matrix_world

        # Store the current component mode to be able to reset it later.
        # It's important to define the mode as a tuple or a direct
        # reference will be created which changes when the mode gets
        # changed.
        currentMode = tuple(bpy.context.tool_settings.mesh_select_mode)

        # If not in vertex selection mode convert the current selection.
        if 'EDGE' in bm.select_mode or 'FACE' in bm.select_mode:
            bm.select_flush_mode()
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)
            bmesh.update_edit_mesh(obj.data)

        # The list of vertices to select. The vertices cannot be
        # selected directly because the loop goes through the current
        # selection and changing the selection affects the loop.
        # Therefore, the vertices to select are stored and the resulting
        # selection is set afterwards.
        selection = []
        cycleSelection = []

        for vert in bm.verts:
            if vert.select:
                # Store the current vertex if the selection should be
                # expanded.
                if extend:
                    selection.append(vert)
                # Deselect the vertex so that the selection is not
                # expanded automatically.
                vert.select = False

                #
                # Cycle through connected vertices
                #
                # When cycling the selected vertices first get collected
                # and then cycled as a whole. This makes cycling more
                # predictable.
                if cycle:
                    cycleSelection.append(vert)

                #
                # Mesh curve
                #
                # Handle the special case where a vertex only connects
                # to two edges. Because of the limited direction the
                # walking can be performed by vertex index.
                elif len(vert.link_edges) < 3:
                    # Marker for the endpoint of the curve. It prevents
                    # that the first/last vertex gets deselected when
                    # walking.
                    endPoint = True
                    for edge in vert.link_edges:
                        connected = edge.other_vert(vert)
                        # Walking right or up goes to the connected
                        # higher index.
                        if x == 1 or y == 1:
                            if connected.index > vert.index:
                                selection.append(connected)
                                endPoint = False
                        # Walking left or down goes to the connected
                        # lower index.
                        elif x == -1 or y == -1:
                            if connected.index < vert.index:
                                selection.append(connected)
                                endPoint = False
                    # In case of the first/last vertex keep the
                    # selection.
                    if endPoint:
                        selection.append(vert)

                #
                # Standard mesh
                #
                # Walk through a regular mesh where a vertex is
                # connected to at least three edges. The direction is
                # based on the vector to the connected vertex.
                else:
                    # Get the screen position of the current vertex.
                    pos1 = vertex2DPosition(vert, mat, region, regionView3d)

                    inRange = []
                    for edge in vert.link_edges:
                        # Get the next connected vertex and it's screen
                        # position.
                        connected = edge.other_vert(vert)
                        pos2 = vertex2DPosition(connected, mat, region, regionView3d)

                        # Get the vector to the connected vertex and
                        # normalize it.
                        vec = pos2 - pos1
                        vec.normalize()
                        # Calculate the angle of the vector in relation
                        # to a reference vector pointing in screen x
                        # position.
                        dot = vec.dot(Vector((1, 0)))
                        angle = math.degrees(math.acos(dot))

                        # Decide if the vector matches the given walking
                        # direction and is within the angle limit of the
                        # direction.
                        if x == 1 and vec[0] > 0 and angle < 45:
                            inRange.append({"vertex": connected,
                                            "angle": angle,
                                            "orient": 0})
                        elif x == -1 and vec[0] < 0 and angle > 135:
                            inRange.append({"vertex": connected,
                                            "angle": angle,
                                            "orient": 180})
                        elif y == 1 and vec[1] > 0 and 45 < angle < 135:
                            inRange.append({"vertex": connected,
                                            "angle": angle,
                                            "orient": 90})
                        elif y == -1 and vec[1] < 0 and 45 < angle < 135:
                            inRange.append({"vertex": connected,
                                            "angle": angle,
                                            "orient": 90})

                    # If multiple vertices match the given direction
                    # check which one is closest to the provided
                    # reference angle.
                    nextVert = None
                    for vertex in inRange:
                        dirAngle = vertex["orient"]
                        if nextVert is None or abs(vertex["angle"] - dirAngle) < abs(nextVert["angle"] - dirAngle):
                            nextVert = vertex
                    # If a connected vertex is found add it to the list
                    # or just keep the current selection.
                    if nextVert:
                        selection.append(nextVert["vertex"])
                    else:
                        selection.append(vert)

        #
        # Cycle through connected vertices
        #
        if cycle:
            # When cycling is inactive because of a preceding regular
            # pickwalk initialize the cycling with the current object
            # and vertex selection.
            if not cycleConnected.active:
                cycleConnected.setVertex(obj, cycleSelection)
                # Activate the cycling so that it can be used
                # repeatedly.
                cycleConnected.active = True

            # Compare the stored vertices with the current selection.
            # New vertices will be added and unused vertices removed.
            cycleConnected.update(obj, cycleSelection)
            # Set, if the next or previous vertex should be selected.
            cycleConnected.increment = toNext
            # Jump to the next/previous vertex.
            cycleConnected.toNext(obj)
            # Add the resulting vertices based on their index.
            for i in cycleConnected.getCurrent(obj):
                selection.append(bm.verts[i])

        # Select all found vertices.
        bm.select_flush_mode()
        for vert in selection:
            vert.select = True

        # Switch the selection mode back to where it was.
        bm.select_flush_mode()
        bpy.context.tool_settings.mesh_select_mode = currentMode
        bmesh.update_edit_mesh(obj.data)


def vertex2DPosition(vertex, mat, region, regionView3d):
    """Return the screen position of the given vertex based on it's 3d
    position and the object's matrix.

    :param vertex: The vertex to find the screen position for.
    :type vertex: bpy.types.MeshVertices
    :param mat: The object's transform matrix.
    :type mat: float[]
    :param region: The region of the 3D view.
    :type region: bpy.types.Region
    :param regionView3d: The 3D region data.
    :type regionView3d: bpy.types.RegionView3D

    :return: The screen position.
    :rtype: tuple(float, float)
    """
    pos = vertex.co
    pos = mat @ pos
    return view3d_utils.location_3d_to_region_2d(region, regionView3d, pos)


def worldObject(obj, toNext=True):
    """Return the next or previous object/s at the top level of the
    collection/s the given object belongs to.

    :param obj: The object to get the world sibling from.
    :type obj: bpy.object
    :param toNext: True, if the next sibling in the list should be
                   selected.
    :type toNext: bool

    :return: A list with sibling objects. This can be more than one
             object if the given object belongs to more than one
             collection.
    :rtype: list(bpy.object)
    """
    # If the object belongs to an armature in edit or pose mode it's not
    # possible to pickwalk away form it. Return the object so that it
    # stays selected.
    if isArmature(obj) and bpy.context.object.mode != 'OBJECT':
        return [obj]

    # Define the direction.
    direction = +1
    if not toNext:
        direction = -1

    objects = []

    collections = obj.users_collection
    for collection in collections:
        topObjects = []
        for item in [i[1] for i in sorted(collection.all_objects.items())]:
            if not item.parent:
                topObjects.append(item)
        index = topObjects.index(obj)
        index = (index + direction) % len(topObjects)
        objects.append(topObjects[index])

    return objects


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
        if walkComponents(context,
                          x=0,
                          y=1,
                          extend=self.extend,
                          toNext=True):
            return {'FINISHED'}

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
        if walkComponents(context,
                          x=0,
                          y=-1,
                          extend=self.extend,
                          toNext=False):
            return {'FINISHED'}

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
        if walkComponents(context,
                          x=-1,
                          y=0,
                          extend=self.extend,
                          cycle=self.switchSide,
                          toNext=False):
            return {'FINISHED'}

        selectSibling(toNext=False,
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
        if walkComponents(context,
                          x=1,
                          y=0,
                          extend=self.extend,
                          cycle=self.switchSide,
                          toNext=True):
            return {'FINISHED'}

        selectSibling(toNext=True,
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

    uiArea = [{"name": '3D View', "space": 'VIEW_3D'},
              {"name": 'Outliner', "space": 'OUTLINER'},
              {"name": 'Graph Editor', "space": 'GRAPH_EDITOR'},
              {"name": 'Dopesheet', "space": 'DOPESHEET_EDITOR'}]

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for area in uiArea:
            km = kc.keymaps.new(name=area["name"], space_type=area["space"])
            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyUp.bl_idname,
                                      type='UP_ARROW',
                                      value='PRESS',
                                      ctrl=True)
            kmi.properties.extend = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyDown.bl_idname,
                                      type='DOWN_ARROW',
                                      value='PRESS',
                                      ctrl=True)
            kmi.properties.extend = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname,
                                      type='LEFT_ARROW',
                                      value='PRESS',
                                      ctrl=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname,
                                      type='RIGHT_ARROW',
                                      value='PRESS',
                                      ctrl=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyUp.bl_idname,
                                      type='UP_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      shift=True)
            kmi.properties.extend = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyDown.bl_idname,
                                      type='DOWN_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      shift=True)
            kmi.properties.extend = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname,
                                      type='LEFT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname,
                                      type='RIGHT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = False
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname,
                                      type='LEFT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      alt=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname,
                                      type='RIGHT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      alt=True)
            kmi.properties.extend = False
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyLeft.bl_idname,
                                      type='LEFT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      alt=True,
                                      shift=True)
            kmi.properties.extend = True
            kmi.properties.switchSide = True
            addon_keymaps.append((km, kmi))

            kmi = km.keymap_items.new(PICKWALK_OT_hierarchyRight.bl_idname,
                                      type='RIGHT_ARROW',
                                      value='PRESS',
                                      ctrl=True,
                                      alt=True,
                                      shift=True)
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
