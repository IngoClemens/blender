# <pep8 compliant>

from . import utils

import bpy


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
        return self.locks()[groupIndex] and not ignoreLock

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

    def vertexWeights(self, index, sparse=False, maxGroups=None):
        """Return a list with the vertex groups weights for the given
        vertex.

        :param index: The vertex index.
        :type index: int
        :param sparse: True, if the returned list should only contain
                       non-zero weights.
                       False, for all weights. The returned list will
                       have a size matching the number of vertex groups.
        :type sparse: bool
        :param maxGroups: Optional list argument to return and update
                          the maximum number of groups per vertex.
                          If the list is provided it only contains one
                          element.
        :type maxGroups: None or list(int)

        :return: A full list with the vertex weights and the group index
                 for all vertex groups.
        :rtype: list(tuple(float, int))
        """
        w = []
        for i, element in self.data.vertices[index].groups.items():
            value = self.data.vertices[index].groups[i].weight
            groupId = self.data.vertices[index].groups[i].group
            w.append((value, groupId))

        # Update the current max number of vertex groups.
        if maxGroups is not None and len(maxGroups):
            if len(w) > maxGroups[0]:
                maxGroups[0] = len(w)

        if sparse:
            return w

        numGroups = len(self.allVertexGroupNames())
        weightList = [(0.0, i) for i in range(numGroups)]

        for item in w:
            value, groupId = item
            weightList[groupId] = value, groupId

        return weightList

    def setWeightsForVertex(self, index, weightList, clear=True):
        """Set the weight for the given vertex for all vertex groups.

        :param index: The vertex index.
        :type index: int
        :param weightList: The list of vertex weight tuples, with the
                           weight and vertex group index.
        :type weightList: list(tuple(float, int))
        :param clear: True, if the vertex group influence should be
                      removed before setting the new weight.
                      This is usually True, except when all influence
                      have been cleared beforehand when setting all new
                      weights.
        :type clear: bool
        """
        for groupIndex in range(len(weightList)):
            value, groupId = weightList[groupIndex]

            group = self.vertexGroup(groupId)
            if clear:
                group.remove([index])

            if value > 0:
                group.add([index], value, 'REPLACE')

    def setVertexWeights(self, indices, weightData, clearAll=False, editMode=False):
        """Set the weights for the given list of vertex indices.

        :param indices: The list of vertex indices.
        :type indices: list(int)
        :param weightData: The list of vertex weight tuples, with the
                           weight and vertex group index for each given
                           vertex index.
        :type weightData: list(list(tuple(float, int)))
        :param clearAll: True, if all vertex group influence should be
                         reset before setting all new weights.
        :type clearAll: bool
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
        if mode != 'OBJECT':
            if not editMode:
                return False
            else:
                # Set the object mode, because vertex groups cannot be
                # edited while in edit mode.
                bpy.ops.object.mode_set(mode="OBJECT")

        # If all new weights should be set remove any vertex group
        # influence for all given vertices.
        if clearAll:
            self.clearVertexWeights(indices)

        for i in range(len(weightData)):
            weightList = weightData[i]
            self.setWeightsForVertex(indices[i], weightList, clear=not clearAll)

        if editMode:
            bpy.ops.object.mode_set(mode=mode)

        return True

    def setWeightsFromVertexList(self, indices, allWeightData):
        """Set the weights for the given list of vertex indices.

        This is used to reset the previous weights when cancelling.
        The weight data list contains all previous weights but the given
        indices are only from the processed vertices.

        :param indices: The list of vertex indices.
        :type indices: list(int)
        :param allWeightData: The list of all vertex weight tuples, with
                              the weight and vertex group index for
                              each vertex index.
        :type allWeightData: list(list(tuple(float, int)))

        :return: True, if setting the weights was successful. False if
                 the object is in edit mode.
        :rtype: bool
        """
        if self.obj.mode == 'EDIT':
            return False

        for i in range(len(indices)):
            weightList = allWeightData[indices[i]]
            self.setWeightsForVertex(indices[i], weightList)

        return True

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

    def mirrorGroupAssignment(self, weightList):
        """Replace the group indices in the given weight data list with
        the indices of the opposite groups.

        :param weightList: The list of vertex weight tuples, with the
                           weight and vertex group index.
        :type weightList: list(tuple(float, int))

        :return: The weight list with the mirrored group indices.
        :rtype: list(tuple(float, int))
        """
        groupNames = self.allVertexGroupNames()

        vertWeights = []
        for value, groupId in weightList:
            # Rename the source vertex group name.
            oppositeName = utils.replaceSideIdentifier(groupNames[groupId])
            # Check if the mirrored name exists.
            if oppositeName in groupNames:
                # Get the according index for the mirrored name.
                oppositeId = groupNames.index(oppositeName)
                # Store the value and group index.
                vertWeights.append((value, oppositeId))

        return vertWeights

    @classmethod
    def limitVertexGroups(cls, weightData, maxGroups):
        """Limit the number of entries in the given list of weights to
        the given max group count.

        The returned list only contains the highest weight values.

        :param weightData: The list of vertex weight tuples, with the
                           weight and vertex group index for each given
                           vertex index.
        :type weightData: list(list(tuple(float, int)))
        :param maxGroups: The number of allowed vertex group influences.
        :type maxGroups: int

        :return: The reduced list of vertex weight tuples.
        :rtype: list(list(tuple(float, int)))
        """
        # Sort by the weight value in descending order.
        sortedWeights = sorted(weightData, key=lambda x: x[0], reverse=True)
        return sortedWeights[:maxGroups]

    @classmethod
    def normalizeVertexGroup(cls, weightData):
        """Normalize the weights of the given list of weights.

        :param weightData: The list of vertex weight tuples, with the
                           weight and vertex group index for each given
                           vertex index.
        :type weightData: list(list(tuple(float, int)))

        :return: The normalized list of vertex weight tuples.
        :rtype: list(list(tuple(float, int)))
        """
        sumWeight = sum(value for value, groupId in weightData)

        normalizedData = [(value / sumWeight, groupId) for value, groupId in weightData]

        return normalizedData
