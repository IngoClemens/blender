# <pep8 compliant>

from . import utils

import bpy
import bmesh


class Weights(object):
    """Class for accessing and processing vertex weights.
    """
    def __init__(self, obj):
        """Initialize.

        :param obj: The mesh object.
        :type obj: bpy.types.Object
        """
        self.obj = obj
        self.data = obj.data

        self.numGroups = len(self.obj.vertex_groups)

    def numVertices(self):
        """Return the number of vertices for the current mesh.

        :return: The number of vertices.
        :rtype: int
        """
        return len(self.data.vertices)

    def allVertexGroupNames(self):
        """Return a list with the names of all vertex groups.

        :return: A list with the vertex group names.
        :rtype: list(str)
        """
        return [i.name for i in self.obj.vertex_groups]

    def locks(self):
        """Return a list with the lock state of all vertex groups.

        :return: A list with the vertex group locks.
        :rtype: list(bool)
        """
        return [i.lock_weight for i in self.obj.vertex_groups]

    def isLocked(self, groupIndex, ignoreLock=False):
        """Return, if the group with the given index is locked, while
        considering to ignore locks.

        :param groupIndex: The vertex group index.
        :type groupIndex: int
        :param ignoreLock: True, if the lock should be ignored.
        :type ignoreLock: bool

        :return: True, if the group is considered to be locked.
        :rtype: bool
        """
        if groupIndex < self.numGroups:
            return self.locks()[groupIndex] and not ignoreLock
        return False

    def vertexGroup(self, groupId):
        """Return the vertex group at the given vertex.

        :param groupId: The vertex group index.
        :type groupId: int

        :return: The vertex group.
        :rtype: bpy.types.VertexGroup
        """
        names = self.allVertexGroupNames()
        return self.obj.vertex_groups.get(names[groupId])

    def vertexGroups(self, index):
        """Return a list with the vertex groups indices which influence
        the given vertex.

        :param index: The vertex index.
        :type index: int

        :return: A list with the vertex group indices for the vertex.
        :rtype: list(int)
        """
        indices = []
        for i, element in self.data.vertices[index].groups.items():
            indices.append(self.data.vertices[index].groups[i].group)
        return indices

    def vertexWeights(self, index, maxGroups=None):
        """Return a list with the vertex groups weights for the given
        vertex.

        Note:
        Replaced by weightsForVertexIndices() because if the mesh is in
        Edit mode and the order of the vertex groups change the group id
        assignment is not correct unless the mode is set to Object and
        back to Edit.
        Also, querying the deform layer for weight values appears to be
        faster than querying the group through the mesh data block.

        :param index: The vertex index.
        :type index: int
        :param maxGroups: Optional list argument to return and update
                          the maximum number of groups per vertex.
                          If the list is provided it only contains one
                          element.
        :type maxGroups: None or list(int)

        :return: A dictionary for the vertex storing the group indices
                 and weight values as key/value pairs.
        :rtype: dict
        """
        w = {}
        for i, element in self.data.vertices[index].groups.items():
            value = self.data.vertices[index].groups[i].weight
            groupId = self.data.vertices[index].groups[i].group
            w[groupId] = value

        # Update the current max number of vertex groups.
        if maxGroups is not None and len(maxGroups):
            if len(w) > maxGroups[0]:
                maxGroups[0] = len(w)

        return w

    def weightsForVertexIndices(self, indices, maxGroups=None, skipIndices=[]):
        """Return a list with the vertex groups weights for the given
        vertex or list of vertex indices.

        :param index: The vertex index or list of indices.
        :type index: int or list(int)
        :param maxGroups: Optional list argument to return and update
                          the maximum number of groups per vertex.
                          If the list is provided it only contains one
                          element.
        :type maxGroups: None or list(int)
        :param skipIndices: The list of group indices which don't match
                            the current group filter.
                            This is only used on conjunction with
                            maxGroups to identify what the current
                            number of maximum groups are.
        :type skipIndices: list(int)

        :return: A list of dictionaries for the vertices storing the
                 group indices and weight values as key/value pairs.
        :rtype: list(dict)
        """
        w = {}

        # Convert single indices to a list.
        if isinstance(indices, int):
            indices = [indices]

        # Create a bmesh from the mesh depending on the mode.
        if self.obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(self.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(self.data)

        bm.verts.ensure_lookup_table()

        # Get the current deform layer.
        layer = bm.verts.layers.deform.active
        if layer is None:
            bm.free()
            return

        # Get the weights for each vertex and convert the groupId/weight
        # tuple to a dictionary.
        for i in indices:
            items = {key: value for key, value in bm.verts[i][layer].items()}
            w[i] = items

            # Update the current max number of vertex groups.
            if maxGroups is not None and len(maxGroups):
                # Remove all invalid group indices.
                groupItems = [j for j in items if j not in skipIndices]
                if len(groupItems) > maxGroups[0]:
                    maxGroups[0] = len(groupItems)

        bm.free()

        return w

    def setWeightsForVertex(self, index, weightData, clear=True):
        """Set the weight for the given vertex for all vertex groups.

        :param index: The vertex index.
        :type index: int
        :param weightData: A dictionary for the vertex storing the group
                           indices and weight values as key/value pairs.
        :type weightData: dict
        :param clear: True, if the vertex group influence should be
                      removed before setting the new weight.
                      This is usually True, except when all influence
                      have been cleared beforehand when setting all new
                      weights.
        :type clear: bool
        """
        for groupId in weightData:
            # If the group index is the helper index for smoothing
            # border vertices of non-deformer groups, setting the weight
            # can be skipped.
            if groupId == self.numGroups:
                continue

            value = weightData[groupId]

            group = self.vertexGroup(groupId)
            if clear:
                group.remove([index])

            if value > 0:
                group.add([index], value, 'REPLACE')

    def setVertexWeights(self, weightData, editMode=False):
        """Set the weights for the given list of vertex indices.

        :param weightData: A dictionary which holds a dictionary for
                           each vertex storing the group indices and
                           weight values as key/value pairs.
        :type weightData: dict(dict)
        :param editMode: False, to set the weights only when not in
                         edit mode. Necessary because when using the
                         smoothing brush the modes cannot be changed.
                         True, when mirroring weights.
        :type editMode: bool

        :return: True, if setting the weights was successful. False if
                 the object is in edit mode.
        :rtype: bool
        """
        mode = self.obj.mode
        if mode not in ['OBJECT', 'WEIGHT_PAINT']:
            if not editMode:
                return False
            else:
                # Set the object mode, because vertex groups cannot be
                # edited while in edit mode.
                bpy.ops.object.mode_set(mode="OBJECT")

        # Remove any vertex group influence for all given vertices.
        self.clearVertexWeights(list(weightData.keys()))

        for index in weightData:
            weightList = weightData[index]
            # Since the group assignments already have been cleared,
            # clearing is not necessary.
            self.setWeightsForVertex(index, weightList, clear=False)

        if editMode:
            bpy.ops.object.mode_set(mode=mode)

        return True

    def setWeightsFromVertexList(self, indices, weightData):
        """Set the weights for the given list of vertex indices.

        When resetting to the previous weights when cancelling the
        weight data list contains all previous weights but the given
        indices are only from the processed vertices.

        :param indices: The list of vertex indices.
        :type indices: list(int)
        :param weightData: A dictionary which holds a dictionary for
                           each vertex storing the group indices and
                           weight values as key/value pairs.
        :type weightData: dict(dict)
        """
        mode = self.obj.mode
        if mode not in ['OBJECT', 'WEIGHT_PAINT']:
            bpy.ops.object.mode_set(mode="OBJECT")

        self.clearVertexWeights(indices)

        for i in indices:
            weightList = weightData[i]
            self.setWeightsForVertex(i, weightList)

        bpy.ops.object.mode_set(mode=mode)

    def clearVertexWeights(self, indices):
        """Delete the group influence for the given vertex or list of
        vertices.

        :param indices: The index or list of vertex indices.
        :type indices: int or list(int)
        """
        if isinstance(indices, int):
            indices = [indices]

        for group in self.obj.vertex_groups:
            group.remove(indices)

    def mirrorGroupAssignment(self, weightData, weightDataMirror, splitWeight=False,
                              skipIndices=[]):
        """Replace the group indices in the given weight data list with
        the indices of the opposite groups.

        :param weightData: A dictionary for the vertex storing the group
                           indices and weight values as key/value pairs.
        :type weightData: dict
        :param weightDataMirror: A dictionary for the opposite vertex
                                 storing the group indices and weight
                                 values as key/value pairs.
        :type weightDataMirror: dict
        :param splitWeight: True, if the weight should be equally split
                            between both sides.
        :type splitWeight: bool
        :param skipIndices: The list of group indices which should not
                            be considered.
        :type skipIndices: list(int)

        :return: The weight dictionary with the mirrored group indices.
        :rtype: dict
        """
        groupNames = self.allVertexGroupNames()

        vertWeights = {}
        processedIds = set()
        for groupId in weightData:
            # If the group index is the helper index for smoothing
            # border vertices of non-deformer groups, setting the weight
            # can be skipped.
            if groupId == self.numGroups:
                continue

            # Only limit vertex groups which match the filter mode.
            if groupId in skipIndices:
                continue

            # Rename the source vertex group name.
            oppositeName = utils.replaceSideIdentifier(groupNames[groupId])
            # Check if the mirrored name exists.
            if oppositeName in groupNames:
                # Get the according index for the mirrored name.
                oppositeId = groupNames.index(oppositeName)
                processedIds.add(oppositeId)
                if not splitWeight:
                    # Store the value for the group index.
                    vertWeights[oppositeId] = weightData[groupId]
                else:
                    # Split the weight between the two groups.
                    value = weightData[groupId] * 0.5
                    vertWeights[groupId] = value
                    vertWeights[oppositeId] = value

        # Keep all group assignments and weights of the target side
        # which haven't been object to mirroring.
        for groupId in weightDataMirror:

            # If the group index is the helper index for smoothing
            # border vertices of non-deformer groups, setting the weight
            # can be skipped.
            if groupId == self.numGroups:
                continue

            if groupId not in processedIds:
                vertWeights[groupId] = weightDataMirror[groupId]

        return vertWeights

    @classmethod
    def normalizeVertexGroup(cls, weightData, skipIndices=[]):
        """Normalize the weights of the given list of weights.

        :param weightData: A dictionary for the vertex storing the group
                           indices and weight values as key/value pairs.
        :type weightData: dict
        :param skipIndices: The list of group indices which should not
                            be considered.
        :type skipIndices: list(int)

        :return: The normalized dictionary of vertex weights.
        :rtype: dict
        """
        # Separate the weights into different data sets.
        normData = {}
        rawData = {}
        for item in weightData:
            if item in skipIndices:
                rawData[item] = weightData[item]
            else:
                normData[item] = weightData[item]

        sumWeight = sum(normData.values())

        normalizedData = {key: value / sumWeight for key, value in normData.items()}

        return {**normalizedData, **rawData}
