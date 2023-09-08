# <pep8 compliant>

from . import utils, weights

import bpy
import bmesh

import time


PROPERTY_NAME = "br_symmetry_map"

AXIS = "X"
AXIS_INDICES = {"X": 0, "Y": 1, "Z": 2}
DIRECTION = "POSITIVE"
DIRECTION_INDICES = {"POSITIVE": 1, "NEGATIVE": 0}
TOLERANCE = 0.0
VERBOSE = False

ANN_AXIS = "The axis which defines the symmetry. Also used as the mirror axis"
ANN_DIRECTION = "The direction to mirror values"
ANN_TOLERANCE = ("Value for finding symmetry points. Zero for automatic "
                 "tolerance based on average edge length")
ANN_VERBOSE = "Outputs the mapping result to the command line"

AXIS_LABEL = "Axis"
DIRECTION_LABEL = "Direction From"
TOLERANCE_LABEL = "Tolerance"
VERBOSE_LABEL = "Verbose"

WARNING_EDGE_NOT_CONNECTED = "The symmetry edge is not connected to any faces"
WARNING_EDGE_NEEDS_TWO_FACES = "The symmetry edge must be connected to two faces"
ERROR_TRAVERSE_COUNT = "Face count is different while traversing vertices: "
ERROR_PASS_COUNT_MISMATCH = "Mapping failed. The passes have a different vertex count. Vertices: "


# ----------------------------------------------------------------------
# Mesh Class
# ----------------------------------------------------------------------

class FaceSet(set):
    """Wrapper class for the set containing all face indices of an
    island.

    This is mainly used to have a string placeholder for representing
    the contained indices rather than showing the full content.
    """
    def __init__(self, iterable=()):
        """Initialize.
        """
        super().__init__(iterable)

    def __repr__(self):
        """The string representation of the face set.

        :return: The string representation.
        :rtype: str
        """
        return "FaceSet({})".format(len(self))

    def asList(self):
        """Return the contained set as a list.

        :return: The set as a list.
        :rtype: list()
        """
        return list(self)


class SymmetryMap(object):
    """Class for creating the symmetry map.
    """
    def __init__(self, obj, axis, tolerance):
        """Initialize.

        :param obj: The object.
        :type obj: bpy.types.Object
        :param axis: The symmetry axis.
        :type axis: str
        :param tolerance: The tolerance for matching vertices.
        :type tolerance: float
        """
        self.obj = obj
        self.mat = obj.matrix_world

        if self.obj.mode == 'EDIT':
            self.bm = bmesh.from_edit_mesh(obj.data)
        else:
            self.bm = bmesh.new()
            self.bm.from_mesh(obj.data)

        self.bm.verts.ensure_lookup_table()
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        self.axis = AXIS_INDICES[axis]
        self.tolerance = tolerance

    def freeMesh(self):
        """Free the bmesh memory.
        """
        self.bm.free()

    def getTolerance(self, value):
        """Return the tolerance, based on the global tool setting.

        :param value: The custom tolerance value.
        :type value: float

        :return: The tolerance value.
        :rtype: float
        """
        return value / 100.0 if self.tolerance == 0 else self.tolerance

    def getIslandFromSelection(self, data={}):
        """Return the related island data from the current edge
        selection as a dictionary or update the given data.

        When creating a symmetry map for the entire mesh, all evaluated
        islands are provided via the given data list. If there is a
        current selection the existing data will get updated.

        When adding islands to the existing map no previously generated
        data exists and the island data will be returned.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)

        :return: The related edge selection data or None, when
                 initializing the symmetry map.
        :rtype: dict or None
        """
        islandData = []

        if self.obj.mode == 'EDIT':
            # Get the current edge selection.
            edges = [edge for edge in self.bm.edges if edge.select]

            # In case many elements are selected (because of an
            # accidental selection), limit the number of edges to two.
            if len(edges) > 2:
                edges = edges[:2]

            for edge in edges:
                # Get the edge faces.
                result = self.getEdgeFaces(edge)
                if isinstance(result, str):
                    return result

                # Check if the first face which belongs to the selected
                # edge has already been visited by a previous mesh
                # evaluation.
                # In this case the existing island index is returned.
                islandIndex = self.isVisitedIsland(data, result[0])
                if islandIndex:
                    # If the island has already been evaluated only the
                    # center edge index needs to get changed.
                    # Changing the edge index is sufficient and None can
                    # be returned because of the list and dictionary the
                    # original data will get mutated.
                    data[islandIndex]["centerEdge"] = edge.index
                    data[islandIndex]["selection"] = True
                else:
                    # If the island hasn't been processed before,
                    # evaluate the related island.
                    # When creating the complete order map this step
                    # isn't necessary since the island has been
                    # processed before and only the center edge index
                    # need to get updated.
                    # Evaluating the edge related island is only
                    # necessary when manually adding an island to the
                    # map.
                    selectedIsland = self.getIslandData(result[0],
                                                        visitedFaces=set(),
                                                        centerEdge=edge.index)
                    selectedIsland["selection"] = True
                    islandData.append(selectedIsland)

        return islandData

    def getIslands(self):
        """Get all island data for the entire mesh as a list of
        dictionaries.

        :return: A list with a dictionary for each mesh island.
        :rtype: list(dict)
        """
        visitedFaces = set()
        islandData = []

        count = 0

        for face in self.bm.faces:
            if face.index not in visitedFaces:
                data = self.getIslandData(face, visitedFaces=visitedFaces)
                data["id"] = count
                islandData.append(data)
                count += 1

        return islandData

    @classmethod
    def isVisitedIsland(cls, data, face):
        """Return the index of the island the given face belongs to.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)
        :param face: The face to search for.
        :type face: bmesh.types.Face

        :return: The index of the related island or None.
        :rtype: int or None
        """
        for i, island in enumerate(data):
            if face.index in island["faces"]:
                return i

    @classmethod
    def getEdgeFaces(cls, edge):
        """Return the faces connected to the given edge.

        :param edge: The edge to get the faces from.
        :type edge: bmesh.types.Edge

        :return: The list of connected faces or an error string.
        :rtype: list(bmesh.types.Face) or str
        """
        faces = edge.link_faces
        if not len(faces):
            return WARNING_EDGE_NOT_CONNECTED
        if len(faces) < 2:
            return WARNING_EDGE_NEEDS_TWO_FACES

        return [f for f in faces]

    def getIslandData(self, face, visitedFaces, centerEdge=None):
        """Return the data of the island connected to the given face.

        :param face: The face to get the island data from.
        :type face: bmesh.types.Face
        :param visitedFaces: The set of visited face indices.
        :type visitedFaces: set(int)
        :param centerEdge: The index of the center edge or None.
        :type centerEdge: int or None

        :return: The island data as a dictionary.
        :rtype: dict
        """
        # The set of face indices for the island.
        indices = set()
        # The list of faces to process. The island is finished when the
        # queue is empty.
        faceQueue = [face]

        # The average edge length.
        length = 0.0

        # The bounding box limits.
        bboxMin = [float("inf")] * 3
        bboxMax = [float("-inf")] * 3

        # The minimum absolute position of the island.
        minPos = float("inf")

        # The index for the vertex defining the absolute minimum
        # position.
        minVertex = None

        # The set of island vertex indices.
        visitedVerts = set()

        while faceQueue:
            # Process the next face in the list.
            currentFace = faceQueue.pop()
            indices.add(currentFace.index)
            visitedFaces.add(currentFace.index)

            vertData = self.getFaceVertexData(currentFace,
                                              bboxMin,
                                              bboxMax,
                                              centerEdge,
                                              minPos,
                                              minVertex,
                                              visitedVerts)
            centerEdge, minPos, minVertex, avgLength = vertData

            for edge in currentFace.edges:
                for linkFace in edge.link_faces:
                    if linkFace.index not in visitedFaces:
                        faceQueue.append(linkFace)

            length += avgLength

        boundingCenter = boundingBoxCenter(bboxMin, bboxMax)
        vertexCount = len(list(visitedVerts))
        faceCount = len(list(indices))

        data = {"vertexCount": vertexCount,
                "faceCount": faceCount,
                "faces": FaceSet(indices),
                "centerEdge": centerEdge,
                "bboxMin": bboxMin,
                "bboxMax": bboxMax,
                "bboxCenter": boundingCenter,
                "minVertex": minVertex,
                "meanEdge": length / faceCount}

        return data

    def getFaceVertexData(self, face, bboxMin, bboxMax, centerEdge, minPos,
                          minVertex, visitedVerts):
        """Return the vertex data of the given face.

        :param face: The face to get the data from.
        :type face: bmesh.types.Face
        :param bboxMin: The minimum bounding box values.
        :type bboxMin: list(float)
        :param bboxMax: The maximum bounding box values.
        :type bboxMax: list(float)
        :param centerEdge: The index of the center edge or None.
        :type centerEdge: int or None
        :param minPos: The smallest absolute position on the symmetry
                       axis of a vertex.
        :type minPos: float
        :param minVertex: The index of the vertex with the smallest
                          absolute position.
        :type minVertex: int
        :param visitedVerts: The set of visited vertices.
        :type visitedVerts: set(int)

        :return: A tuple with the center edge index, the min position,
                 the min vertex index and the average edge length.
        :rtype: tuple(int, float, int)
        """
        verts = face.verts

        # Get the average edge length.
        avgLength = self.averageEdgeLength(verts[0])

        for vert in verts:
            point = vert.co
            bboxMin[0] = min(bboxMin[0], point[0])
            bboxMin[1] = min(bboxMin[1], point[1])
            bboxMin[2] = min(bboxMin[2], point[2])

            bboxMax[0] = max(bboxMax[0], point[0])
            bboxMax[1] = max(bboxMax[1], point[1])
            bboxMax[2] = max(bboxMax[2], point[2])

            if centerEdge is None:
                centerEdge = self.getIslandCenterEdge(vert, self.getTolerance(avgLength))

            # Calculate or update the absolute minimum position and
            # according vertex index.
            pos = abs(vert.co[self.axis])
            if pos < minPos:
                minPos = pos
                minVertex = vert.index

            if vert.index not in visitedVerts:
                visitedVerts.add(vert.index)

        return centerEdge, minPos, minVertex, avgLength

    @classmethod
    def averageEdgeLength(cls, vert):
        """Return the average edge length of all edges connected to the
        given vertex.

        :param vert: The vertex to get the edges from.
        :type vert: bmesh.types.Vert

        :return: The average connected edge length.
        :rtype: float
        """
        length = 0.0
        edges = vert.link_edges
        for edge in edges:
            length += edge.calc_length()
        return length / len(edges)

    def getIslandCenterEdge(self, vertex, tolerance):
        """Return the center edge of the island, based on the given
        vertex.

        :param vertex: The vertex to get the center edge from.
        :type vertex: bmesh.types.Vert
        :param tolerance: The tolerance value for the position matching.
        :type tolerance: float

        :return: The center edge index or None.
        :rtype: int or None
        """
        if not self.isIslandCenterVertex(vertex, tolerance):
            return

        for edge in vertex.link_edges:
            otherVert = edge.other_vert(vertex)
            # Check that the othe redge vertex is also centered and that
            # there are two faces connected to the edge.
            if self.isIslandCenterVertex(otherVert, tolerance) and len(edge.link_faces) == 2:
                return edge.index

    def isIslandCenterVertex(self, vertex, tolerance):
        """Return if the given vertex is at the center of the symmetry.

        :param vertex: The vertex.
        :type vertex: bmesh.types.Vert
        :param tolerance: The tolerance value for the position matching.
        :type tolerance: float

        :return: True, if the vertex is located at the symmetry center.
        :rtype: bool
        """
        position = vertex.co[self.axis]
        if abs(position) < tolerance:
            return True
        return False

    def getSymmetryPoints(self, axis, tolerance):
        """Build an order map based on positional symmetry.

        :param axis: The symmetry axis.
        :type axis: str
        :param tolerance: The tolerance for matching vertices.
        :type tolerance: float

        :return: A tuple with the list of mapped vertex indices and the
                 auto tolerance message.
        :rtype: tuple(list(int), str)
        """
        autoInfo = ""

        # The object needs to be in edit mode to get the current island.
        if self.obj.mode != 'EDIT':
            return [], autoInfo

        axisIndex = AXIS_INDICES[axis]
        hasMap = hasMapProperty(self.obj)

        # Get the current selection.
        verts = []
        faces = []
        for vert in self.bm.verts:
            if vert.select:
                verts.append(vert)
                faces = vert.link_faces
                if len(verts) == 2:
                    break

        # Only continue of there are faces connected to the current
        # selection.
        if not len(faces):
            return [], autoInfo

        # If two vertices are selected calculate the tolerance value
        # based on the relative symmetrical distance.
        if len(verts) == 2 and tolerance == 0.0:
            tolerance = utils.getSymmetryPointDelta(verts[0], verts[1], axisIndex)
            autoInfo = "Used auto tolerance of {:.4f}".format(tolerance)

        # Getting the complete island data is mainly a workaround to
        # retrieve all faces from the island the selection belongs to.
        data = self.getIslandData(faces[0],
                                  visitedFaces=set(),
                                  centerEdge=None)

        # Build the kdtree.
        kdPoints = utils.kdTree(self.bm, len(self.bm.verts))

        symMap = [-1] * len(self.bm.verts)

        # Check every vertex of the island on the positive axis if it
        # has a sibling on the opposite side of the mesh.
        for vert in self.getIslandVertices(data["faces"].asList()):
            # Only process the positive side and those which haven't
            # been mapped.
            # Account for the case that a vertex can be very slighly on
            # the negative side and still be considered at the center.
            # Use the negative tolerance value to cover these vertices.
            if (vert.co[axisIndex] >= -tolerance and
                    (not hasMap or
                     (hasMap and self.obj.data[PROPERTY_NAME][vert.index] == -1))):
                pos = vert.co.copy()
                pos[axisIndex] *= -1
                rangeVerts = kdPoints.find_range(pos, tolerance)
                if len(rangeVerts) == 1:
                    pos, index, dist = rangeVerts[0]
                    symMap[vert.index] = index
                    symMap[index] = vert.index

        return symMap, autoInfo

    @classmethod
    def getIslandSizeMatches(cls, data):
        """Return as list of island dictionaries which appear to have a
        sibling based on their face count.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)

        :return: The list of dictionaries, which have a similar face
                 count.
        :rtype: list(dict)
        """
        counts = {}

        for island in data:
            faceCount = island["faceCount"]
            if faceCount in counts:
                counts[faceCount] += 1
            else:
                counts[faceCount] = 1

        result = []
        for d in data:
            # Include all islands which have a matching number of faces
            # but exclude all which have been defined by the selection.
            if counts[d.get("faceCount")] >= 2 and "selection" not in d:
                result.append(d)
        return result

    def getIslandPairs(self, data):
        """Return a list of tuples which indicate which islands appear
        to be mirrored version of each other, based on their general
        opposite position.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)

        :return: The list tuples, containing the matching island pair
                 indices and the island ids as a list.
        :rtype: list(tuple(int, int, list(int)))
        """
        pairs = []
        visited = set()

        # Match each island against all others in the list.
        for i, shellA in enumerate(data):
            # Don't compare to itself.
            for j, shellB in enumerate(data[i+1:], start=i+1):
                # Only match islands with the same face count.
                if shellA["faceCount"] == shellB["faceCount"]:
                    # Make sure that every island is only added to a
                    # pair one time.
                    if i not in visited and j not in visited:
                        # Check, if the bounding box center of one
                        # island is located within the bounding box of
                        # the sibling.
                        center = shellA["bboxCenter"].copy()
                        center[self.axis] *= -1
                        if isInsideBounds(center,
                                          shellB["bboxMin"],
                                          shellB["bboxMax"]):
                            # Add the pair to the list and mark them as
                            # visited.
                            pairs.append((i, j, [shellA["id"], shellB["id"]]))
                            visited.add(i)
                            visited.add(j)

        return pairs

    def getSelectedPairElements(self, data):
        """Create the traversal dictionary for the island pair defined
        by the edge selection.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)

        :return: The dictionary describing the traversal elements for
                 the edge pair and the according island ids.
        :rtype: tuple(dict, list(int)) or tuple(None, None)
        """
        # The elements for each pair.
        elements = {"vertex1": None,
                    "vertex2": None,
                    "vertex3": None,
                    "vertex4": None,
                    "face1": None,
                    "face2": None,
                    "faceCount": None}
        # The island ids referring to the given list of islands.
        islandIds = []

        faceCount = None

        # Get the selected center edges.
        edges = []
        for i, island in enumerate(data):
            if "selection" in island:
                edges.append(self.bm.edges[island["centerEdge"]])
                faceCount = island["faceCount"]
                islandIds.append(i)

        # If there are not two edges there is nothing else to do.
        # Single, spanning island, edges don't need processing and more
        # than two edges are not supported.
        if len(edges) != 2:
            return None, None

        # Collect all data from the selected edges.
        edgeA, edgeB = edges

        vertsA = edgeA.verts
        vertsB = edgeB.verts

        # Get the face which is located closer to the symmetry center.
        faceA = getInnerFace(edgeA, axisIndex=self.axis)
        faceB = getInnerFace(edgeB, axisIndex=self.axis)

        # The faces should never be None.
        if faceA is None or faceB is None:
            return None, None

        # Get the direction of the edge.
        dirA = getEdgeDirection(faceA, edgeA)
        dirB = getEdgeDirection(faceB, edgeB)

        # The directions should never be None.
        if dirA is None or dirB is None:
            return None, None

        elements["vertex1"] = vertsA[0].index
        elements["vertex2"] = vertsA[1].index

        # The direction of the opposite side should be reversed.
        if dirA == dirB:
            elements["vertex3"] = vertsB[1].index
            elements["vertex4"] = vertsB[0].index
        else:
            elements["vertex3"] = vertsB[0].index
            elements["vertex4"] = vertsB[1].index

        elements["face1"] = faceA.index
        elements["face2"] = faceB.index

        elements["faceCount"] = faceCount

        return elements, islandIds

    def getIslandPairElements(self, data, pairs):
        """Create the traversal dictionary for each island pair defined
        by the given index pair.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)
        :param pairs: The list of tuples, holding the island indices of
                      the pair and a list with the original island
                      indices.
        :type pairs: list(tuple(int, int, list(int)))

        :return: The list of dictionaries describing the traversal
                 elements for each pair and the according island ids.
        :rtype: tuple(list(dict), list(int))
        """
        # The list of elements for each pair.
        elements = []
        # The island ids referring to the given list of islands.
        islandIds = []

        for indexA, indexB, ids in pairs:
            islandA = data[indexA]
            islandB = data[indexB]

            visitedVertsA = set()

            # Get all vertices of the opposite island for position
            # matching.
            verticesB = self.getIslandVertices(islandB["faces"].asList())

            symVertsA = []
            symVertsB = []

            # Got through each face of the island on the one side and
            # compare the position of the face vertices with the
            # vertices on the opposite side.
            # To be able to match the island pair at least one face has
            # to match based on three vertex positions minimum.
            # Three vertices are required to find the according face
            # and edge.
            # The limitation of this approach is that this works best
            # with three and four sided faces. If multi-sided faces are
            # included the process might fail or produce unwanted
            # results.
            for faceIndex in islandA["faces"].asList():
                face = self.bm.faces[faceIndex]
                for vertA in face.verts:
                    if vertA.index not in visitedVertsA:
                        # Make sure that each vertex is only processed
                        # once, since faces share vertices.
                        visitedVertsA.add(vertA.index)
                        for vertB in verticesB:
                            posB = vertB.co.copy()
                            posB[self.axis] *= -1
                            if utils.isEquivalent(vertA.co,
                                                  posB,
                                                  tolerance=self.getTolerance(islandA["meanEdge"])):
                                symVertsA.append(vertA)
                                symVertsB.append(vertB)
                                break
                if len(symVertsB) > 2:
                    resultVerts = self.getEdgeFromVertexList(symVertsA)
                    resultFaceA = self.getFaceFromVertexList(symVertsA)
                    resultFaceB = self.getFaceFromVertexList(symVertsB)

                    if not resultVerts or not resultFaceA or not resultFaceB:
                        symVertsA.clear()
                        symVertsB.clear()
                    else:
                        edge, index1, index2 = resultVerts
                        elements.append({"vertex1": symVertsA[index1].index,
                                         "vertex2": symVertsA[index2].index,
                                         "vertex3": symVertsB[index1].index,
                                         "vertex4": symVertsB[index2].index,
                                         "face1": resultFaceA.index,
                                         "face2": resultFaceB.index,
                                         "faceCount": islandA["faceCount"]})
                        islandIds.extend(ids)
                        break
                else:
                    symVertsA.clear()
                    symVertsB.clear()

        return elements, islandIds

    def getIslandVertices(self, faces):
        """Return the list of vertices which belong to the island of the
        given list of face indices.

        :param faces: The list of face indices.
        :type faces: list(int)

        :return: The list of island vertices.
        :rtype: list(bm.types.Vert)
        """
        vertices = set()
        for faceIndex in faces:
            face = self.bm.faces[faceIndex]
            verts = [v for v in face.verts]
            vertices.update(verts)

        return vertices

    @classmethod
    def getEdgeFromVertexList(cls, verts):
        """Return the edge which connects two of the given list of
        vertices.
        Also returns, which indices of the given list are used.

        :param verts: The list of vertices.
        :type verts: list(bmesh.types.Vert)

        :return: A tuple with the edge and the used vertex indices.
        :rtype: tuple(bmesh.types.Edge, int, int)
        """
        for i, vert in enumerate(verts):
            for edge in vert.link_edges:
                for j, otherVert in enumerate(verts):
                    if edge.other_vert(vert) == otherVert:
                        return edge, i, j

    @classmethod
    def getFaceFromVertexList(cls, verts):
        """Return the face which connects the given list of vertices.

        :param verts: The list of vertices.
        :type verts: list(bmesh.types.Vert)

        :return: The connected face.
        :rtype: bmesh.types.Face
        """
        # Create a set for faster lookup.
        vertexSet = set(verts)

        for vert in vertexSet:
            for face in vert.link_faces:
                if all(v in vertexSet for v in face.verts):
                    return face

    @classmethod
    def filterIslandPairs(cls, data, filterIds):
        """Remove the given indices from the data list and return the
        reduces list.

        This removes all islands which have been defined as pairs and
        leaves only the islands which are supposedly single.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)
        :param filterIds: The list of indices to remove.
        :type filterIds: list(int)

        :return: The list of single island dictionaries.
        :rtype: list(dict)
        """
        return [d for d in data if d["id"] not in filterIds]

    @classmethod
    def filterInvalidIsland(cls, data):
        """Remove all islands from the list which have no center edge.

        :param data: The list of dictionaries, describing each island of
                     the mesh.
        :type data: list(dict)

        :return: The list of valid single island dictionaries.
        :rtype: list(dict)
        """
        return [d for d in data if d["centerEdge"] is not None]

    def getIslandSpanElements(self, data):
        """Based on the given data, return a dictionary for each island
        holding the necessary elements for the mesh traversal.

        :param data: The dictionary or list of dictionaries, describing
                     each island of the mesh.
        :type data: dict or list(dict)

        :return: The list of dictionaries describing the traversal
                 elements.
        :rtype: list(dict)
        """
        if isinstance(data, dict):
            data = [data]

        elements = []

        for island in data:
            if island["centerEdge"] is not None:
                edge = self.bm.edges[island["centerEdge"]]
                verts = edge.verts
                faces = edge.link_faces

                if len(verts) == 2 and len(faces) == 2:
                    elements.append({"vertex1": verts[0].index,
                                     "vertex2": verts[1].index,
                                     "vertex3": None,
                                     "vertex4": None,
                                     "face1": faces[0].index,
                                     "face2": faces[1].index,
                                     "faceCount": island["faceCount"]})

        return elements

    def createMapping(self, data):
        """Create the symmetry mapping for the given list of islands.

        :param data: The list of dictionaries describing the traversal
                     elements.
        :type data: list(dict)

        :return: The list of mapped vertex indices.
        :rtype: list(int)
        """
        symMap = [-1] * len(self.bm.verts)

        for island in data:
            if island["face1"] is not None and island["face2"] is not None:

                vertex1 = 0
                vertex2 = 0

                order1 = []
                order2 = []

                for i in range(2):
                    if i == 0:
                        face = island["face1"]
                        vertex1 = island["vertex1"]
                        vertex2 = island["vertex2"]
                        numFaces = island["faceCount"]
                    else:
                        face = island["face2"]
                        if not island["vertex3"]:
                            vertex1 = island["vertex1"]
                            vertex2 = island["vertex2"]
                        else:
                            vertex1 = island["vertex3"]
                            vertex2 = island["vertex4"]
                        numFaces = island["faceCount"]

                    result = traverseMesh(self.bm, face, vertex1, vertex2, numFaces)
                    mapOrder, numProcessFaces = result

                    if numFaces != numProcessFaces:
                        msg = "{}{} {}".format(ERROR_TRAVERSE_COUNT, vertex1, vertex2)
                        return msg

                    if i == 0:
                        order1 = mapOrder
                    else:
                        order2 = mapOrder

                if len(order1) != len(order2):
                    msg = "{}{} {}".format(ERROR_PASS_COUNT_MISMATCH, vertex1, vertex2)
                    return msg

                # Use the generated maps to build a new vertex list that
                # will remap the original topology.
                for i in range(len(order1)):
                    symMap[order1[i]] = order2[i]
                    symMap[order2[i]] = order1[i]

        return symMap


def boundingBoxCenter(b1, b2):
    """Return the center point of the given bounding box ranges.

    :param b1: The minimum bounding box point.
    :type b1: list(float)
    :param b2: The maximum bounding box point.
    :type b2: list(float)

    :return: The center point.
    :rtype: list(float)
    """
    return [getCenter(b1[i], b2[i]) for i in range(len(b1))]


def getCenter(v1, v2):
    """Return the center between the two given values.

    :param v1: The first value.
    :type v1: float
    :param v2: The second value.
    :type v2: float

    :return: The center value.
    :rtype: float
    """
    return v1 + (v2 - v1) / 2.0


def isInsideBounds(point, bboxMin, bboxMax):
    """Return if the given point is located within the given bounding
    box range.

    :param point: The point.
    :type point: list(float)
    :param bboxMin: The minimum bounding box point.
    :type bboxMin: list(float)
    :param bboxMax: The maximum bounding box point.
    :type bboxMax: list(float)

    :return: True, if the point is located within the bounding box.
    :rtype: bool
    """
    for i in range(len(point)):
        if point[i] < bboxMin[i] or point[i] > bboxMax[i]:
            return False
    return True


def traverseMesh(bm, face, vertex1, vertex2, numFaces):
    """Traverse the mesh starting from the given face and vertex
    direction and return the list of vertices in the processed order.

    :param bm: The bmesh to evaluate.
    :type bm: bmesh
    :param face: The face index to start from.
    :type face: int
    :param vertex1: The index of the first vertex.
    :type vertex1: int
    :param vertex2: The index of the second vertex.
    :type vertex2: int
    :param numFaces: The number of faces of the island.
    :type numFaces: int

    :return: A tuple with the vertex order list and the number of
             processed faces.
    :rtype: tuple(list(int), int)
    """
    visitedVerts = [False] * len(bm.verts)
    visitedFaces = [False] * len(bm.faces)

    processFaces = []
    faceVtx1 = []
    faceVtx2 = []
    processFaces.append(face)
    faceVtx1.append(vertex1)
    faceVtx2.append(vertex2)

    visitedFaces[face] = True

    orderedVertices = []

    for i in range(numFaces):
        if i < len(processFaces):
            face = processFaces[i]
            vertex1 = faceVtx1[i]
            vertex2 = faceVtx2[i]

            faceEdges = [e.index for e in bm.faces[face].edges]

            edgeVertices = []
            for edges in bm.faces[face].edges:
                edgeVertices.extend([v.index for v in edges.verts])

            orderedEdges, orderedVertex1, orderedVertex2 = getOrderedFaceEdges(vertex1,
                                                                               vertex2,
                                                                               faceEdges,
                                                                               edgeVertices)

            for j in range(len(orderedEdges)):
                if not visitedVerts[orderedVertex1[j]]:
                    orderedVertices.append(orderedVertex1[j])
                    visitedVerts[orderedVertex1[j]] = True
                if not visitedVerts[orderedVertex2[j]]:
                    orderedVertices.append(orderedVertex2[j])
                    visitedVerts[orderedVertex2[j]] = True

                connectedFaces = [f.index for f in bm.edges[orderedEdges[j]].link_faces]
                connectedFace = getOppositeEdgeFace(face, connectedFaces)

                if connectedFace is not None and not visitedFaces[connectedFace]:
                    processFaces.append(connectedFace)
                    faceVtx1.append(orderedVertex1[j])
                    faceVtx2.append(orderedVertex2[j])
                    visitedFaces[connectedFace] = True
        else:
            break

    return orderedVertices, len(processFaces)


def getOrderedFaceEdges(vertex1, vertex2, edgeList, edgeVertices):
    """Return the list of edges for the current face in the direction
    which is defined by the given vertices.

    :param vertex1: The index of the first vertex.
    :type vertex1: int
    :param vertex2: The index of the second vertex.
    :type vertex2: int
    :param edgeList: The list of all face edges.
    :type edgeList: list(int)
    :param edgeVertices: The list of all face edge vertices.
    :type edgeVertices: list(int)

    :return: A tuple with:
             orderedEdges: The face edges in order starting from the
                           edge between the two given vertices.
             orderedVertex1: The list of first vertices for every
                             ordered edge.
             orderedVertex2: The list of second vertices for every
                             ordered edge.
    :rtype: tuple(list(int), list(int), list(int))
    """
    edgeCount = len(edgeList)

    orderedEdges = []
    orderedVertex1 = []
    orderedVertex2 = []

    for i in range(edgeCount):
        remainingEdges = []
        remainingVertices = []

        nextVertex1 = -1
        nextVertex2 = -1

        for j in range(len(edgeList)):
            k = j * 2

            if ((edgeVertices[k] == vertex1 and edgeVertices[k + 1] == vertex2) or
                    (edgeVertices[k] == vertex2 and edgeVertices[k + 1] == vertex1)):
                orderedEdges.append(edgeList[j])
                orderedVertex1.append(vertex1)
                orderedVertex2.append(vertex2)
            else:
                if edgeVertices[k] == vertex2:
                    nextVertex1 = vertex2
                    nextVertex2 = edgeVertices[k + 1]
                elif edgeVertices[k + 1] == vertex2:
                    nextVertex1 = vertex2
                    nextVertex2 = edgeVertices[k]
                remainingEdges.append(edgeList[j])
                remainingVertices.append(edgeVertices[k])
                remainingVertices.append(edgeVertices[k + 1])

        vertex1 = nextVertex1
        vertex2 = nextVertex2
        edgeList = remainingEdges
        edgeVertices = remainingVertices

    return orderedEdges, orderedVertex1, orderedVertex2


def getOppositeEdgeFace(index, faces):
    """Return the index of the second face which is connected to the
    given edge. None, if the edge is a border edge.

    :param index: The index of the first face.
    :type index: int
    :param faces: The list of face indices connected to the edge.
    :type faces: list(int)

    :return: The other face index or None.
    :rtype: int or Nonw
    """
    for f in faces:
        if f != index:
            return f


def getInnerFace(edge, axisIndex=0):
    """Return the connected face which is closer to the given symmetry
    axis.

    :param edge: The edge to get the faces from.
    :type edge: bmesh.types.Edge
    :param axisIndex: The 0-based index of the symmetry axis.
    :type axisIndex: int

    :return: The face closest to the symmetry axis.
    :rtype: bmesh.types.Face
    """
    innerFace = (None, None)
    for face in edge.link_faces:
        value = abs(face.calc_center_median()[axisIndex])
        if innerFace[0] is None or value < innerFace[1]:
            innerFace = (face, value)
    return innerFace[0]


def modulateIndex(index, count):
    """Modulate the given index based on the given count.

    Returns 0..count-1, for any integer value.

    :param index: The index to modulate.
    :type index: int
    :param count: The count to modulate with.
    :type count: int

    :return: The modulated index.
    :rtype: int
    """
    return (index + count) % count


def getEdgeDirection(face, edge):
    """Return the edge direction based on the vertices of the given
    face.

    :param face: The face.
    :type face: bmesh.types.Face
    :param edge: The edge to get the direction from.
    :type edge: bmesh.types.Edge

    :return: True, for a positive and False for a negative direction.
    :rtype: bool or None
    """
    edgeVerts = edge.verts
    verts = face.verts
    vertsCount = len(verts)

    for i, vert in enumerate(verts):
        if vert.index == edgeVerts[0].index:
            if verts[modulateIndex(i + 1, vertsCount)].index == edgeVerts[1].index:
                return True
            elif verts[modulateIndex(i - 1, vertsCount)].index == edgeVerts[1].index:
                return False


# ----------------------------------------------------------------------
# Operator Functions
# ----------------------------------------------------------------------

def hasMapProperty(obj):
    """Return if the order map property exists in the object's data
    block.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: True, if the property exists.
    :rtype: bool
    """
    return PROPERTY_NAME in obj.data


def getOrderMap(obj):
    """Return the order map.

    This is for convenient access of the order map when needed in
    another module.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: The order map.
    :rtype: list(int)
    """
    return obj.data[PROPERTY_NAME]


def hasValidOrderMap(obj):
    """Return if the stored order map matches the number of mesh
    vertices.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: True, if the order map matches the number of mesh vertices.
    :rtype: bool
    """
    if hasMapProperty(obj):
        return len(obj.data[PROPERTY_NAME]) == len(obj.data.vertices)
    else:
        return False


def isComplete(obj):
    """Return if all vertices are mapped.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: True, if all vertices are mapped and there are no -1
             entries in the order map.
    :rtype: bool
    """
    if hasMapProperty(obj):
        return not any(item == -1 for item in obj.data[PROPERTY_NAME])
    else:
        return False


def getUnmappedNum(obj):
    """Return the number of unmapped vertices.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: The number of unmapped vertices.
    :rtype: int or None
    """
    if hasMapProperty(obj):
        return sum(1 for value in obj.data[PROPERTY_NAME] if value == -1)


def setMap(obj, indices):
    """Store the given order map on the object.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param indices: The list of mapping indices
    :type indices: list(int)
    """
    obj.data[PROPERTY_NAME] = indices


def extendMap(obj, indices):
    """Add the given order map to the existing map on the object.

    If the order map doesn't exist create a new one.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param indices: The list of mapping indices
    :type indices: list(int)
    """
    if not hasMapProperty(obj):
        setMap(obj, indices)
    else:
        for i, index in enumerate(indices):
            if index != -1:
                obj.data[PROPERTY_NAME][i] = index


def getMapInfo(obj):
    """Return the info about the mapping status and the according icon.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: The mapping status string, the icon and a boolean for
             displaying further UI elements.
    :rtype: tuple(str, str, bool)
    """
    # The property doesn't exist.
    if not hasMapProperty(obj):
        return "No mapping", 'INFO', False
    else:
        # Check if the vertex count matches.
        if hasValidOrderMap(obj):
            count = getUnmappedNum(obj)
            vtxCount = len(obj.data.vertices)
            if count == 0:
                return "Mapping complete", 'CHECKMARK', True
            elif count == vtxCount:
                return "Mapping not set", 'ERROR', False
            else:
                return "Partial mapping {}/{} vertices".format(vtxCount - count, vtxCount), 'ERROR', True

        # The vertex count differs.
        else:
            return "Vertex count mismatch", 'ERROR', False


def createMap(obj, axis, tolerance, verbose=False):
    """Create the order mapping.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param axis: The symmetry axis.
    :type axis: str
    :param tolerance: The tolerance for matching vertices.
    :type tolerance: float
    :param verbose: True, if the mapping process should be output to the
                    command line.
    :type verbose: bool

    :return: A message string.
    :rtype: str
    """
    # Initialize the symmetry mapping.
    symMap = SymmetryMap(obj, axis, tolerance)

    # Get all island data.
    data = symMap.getIslands()
    # Update the island data with the center edge, if one is selected.
    symMap.getIslandFromSelection(data=data)
    if verbose:
        msg = "Symmetry mapping found {}".format(utils.pluralize(len(data), "island"))
        outputVerbose(data, msg)

    # Get all islands which have a matching size.
    # All islands related to the current selection are removed from the
    # data list.
    sizeMatchData = symMap.getIslandSizeMatches(data)

    # Get all paired island indices.
    pairIndices = symMap.getIslandPairs(sizeMatchData)

    # Get the elements for the mesh traversal.
    pairElements, ids = symMap.getIslandPairElements(sizeMatchData, pairIndices)
    # Get the elements for the mesh traversal for the selected pair
    # only.
    pairElementsSelection, idsSelection = symMap.getSelectedPairElements(data)
    # Combine all pair elements.
    if idsSelection:
        pairElements.append(pairElementsSelection)
        ids.extend(idsSelection)

    if verbose:
        pairs = [(ids[i], ids[i + 1]) for i in range(0, len(ids), 2)]
        outputVerbose(pairs, "{} found".format(utils.pluralize(len(pairs), "pair", "island")))

    # Get all spanning islands.
    spanningIslands = symMap.filterIslandPairs(data, ids)
    # Remove islands without a center edge.
    spanningIslands = symMap.filterInvalidIsland(spanningIslands)
    if verbose:
        msg = "{} found".format(utils.pluralize(len(spanningIslands), "island", "spanning"))
        outputVerbose(spanningIslands, msg)

    # Get the elements for the mesh traversal.
    spanElements = symMap.getIslandSpanElements(spanningIslands)

    # Combine all found traversal elements.
    elements = spanElements + pairElements
    if verbose:
        msg = "{} used for mapping".format(utils.pluralize(len(elements), "element"))
        outputVerbose(elements, msg)
        print()

    # Perform the order mapping.
    orderMap = symMap.createMapping(elements)

    # Finish processing the mesh.
    symMap.freeMesh()

    # Set the order map property.
    setMap(obj, orderMap)

    # Prepare the operator info output.
    mappedIslandCount = len(spanElements) + len(pairElements) * 2
    info = "Mapped {}".format(utils.pluralize([mappedIslandCount, len(data)], "island"))

    return info


def addToMap(obj, axis, tolerance, verbose=False):
    """Add the island of the current selection to the order mapping.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param axis: The symmetry axis.
    :type axis: str
    :param tolerance: The tolerance for matching vertices.
    :type tolerance: float
    :param verbose: True, if the mapping process should be output to the
                    command line.
    :type verbose: bool

    :return: A message string.
    :rtype: str
    """
    # Initialize the symmetry mapping.
    symMap = SymmetryMap(obj, axis, tolerance)

    data = symMap.getIslandFromSelection()
    if verbose:
        msg = "Symmetry mapping found {}".format(utils.pluralize(len(data), "island"))
        outputVerbose(data, msg)

    # Get the elements for the mesh traversal.
    # Spanning island with center edge.
    if len(data) == 1:
        elements = symMap.getIslandSpanElements(data)
    # Island pair or spanning island with no center edge.
    elif len(data) == 2:
        elements, ids = symMap.getSelectedPairElements(data)
        elements = [elements]
    else:
        return "No valid edge selection found for symmetry mapping"

    if verbose:
        msg = "{} used for mapping".format(utils.pluralize(len(elements), "element"))
        outputVerbose(elements, msg)
        print()

    # Perform the order mapping.
    orderMap = symMap.createMapping(elements)

    # Finish processing the mesh.
    symMap.freeMesh()

    # Set the order map property.
    extendMap(obj, orderMap)

    info = "Mapped {}".format(utils.pluralize(len(data), "island"))

    return info


def addPartialToMap(obj, axis, tolerance):
    """Add the partial symmetry of the current island selection to the
    order mapping.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param axis: The symmetry axis.
    :type axis: str
    :param tolerance: The tolerance for matching vertices.
    :type tolerance: float

    :return: A message string.
    :rtype: str
    """
    # Initialize the symmetry mapping.
    symMap = SymmetryMap(obj, axis, tolerance)

    orderMap, autoInfo = symMap.getSymmetryPoints(axis, tolerance)
    if not orderMap:
        return "No selection or no symmetrical points found"

    # Finish processing the mesh.
    symMap.freeMesh()

    # Set the order map property.
    extendMap(obj, orderMap)

    items = [i for i in orderMap if i != -1]
    info = "Mapped {} vertices".format(len(items))
    if len(autoInfo):
        info += ". " + autoInfo

    return info


def deleteMap(obj):
    """Delete the order mapping property.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: A tuple with the report type and string.
    :rtype: tuple(set, str)
    """
    if hasMapProperty(obj):
        del obj.data[PROPERTY_NAME]
    else:
        return {'WARNING'}, "The object has no symmetry mapping"

    return {'INFO'}, "Symmetry map removed"


def selectMapped(obj):
    """Select all mapped vertices.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: A tuple with the report type and string.
    :rtype: tuple(set, str)
    """
    return selectVertices(obj, mapped=True)


def selectUnmapped(obj):
    """Select all unmapped vertices.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: A tuple with the report type and string.
    :rtype: tuple(set, str)
    """
    return selectVertices(obj, mapped=False)


def selectVertices(obj, mapped=True):
    """Select all mapped or unmapped vertices.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param mapped: True, to select only mapped vertices.
    :type mapped: bool

    :return: A tuple with the report type and string.
    :rtype: tuple(set, str)
    """
    if not hasMapProperty(obj):
        return {'WARNING'}, "The object has no symmetry mapping"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    count = 0
    orderMap = obj.data[PROPERTY_NAME]
    for i, item in enumerate(orderMap):
        if (item != -1 and mapped) or (item == -1 and not mapped):
            obj.data.vertices[i].select = True
            count += 1

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')

    return {'INFO'}, "{} vertices selected".format(count)


def selectSibling(obj):
    """Select all sibling vertices based on the current selection.

    :param obj: The object.
    :type obj: bpy.types.Object

    :return: A tuple with the report type and string.
    :rtype: tuple(set, str)
    """
    if not hasMapProperty(obj):
        return {'WARNING'}, "The object has no symmetry mapping"
    bpy.ops.object.mode_set(mode='OBJECT')

    count = 0
    orderMap = obj.data[PROPERTY_NAME]
    for vert in obj.data.vertices:
        if vert.select:
            otherVert = orderMap[vert.index]
            if otherVert != -1:
                obj.data.vertices[otherVert].select = True
                count += 1

    bpy.ops.object.mode_set(mode='EDIT')

    if count:
        return {'INFO'}, "{} selected".format(utils.pluralize(count, "sibling"))
    else:
        return {'WARNING'}, "No sibling/s found"


def outputVerbose(items, header):
    """Output the verbose mapping process to the command line.

    :param items: The list of data items to output.
    :type items: list()
    :param header: The header string for describing the list.
    :type header: str
    """
    exclude = ['faces', 'bboxMin', 'bboxMax', 'bboxCenter', 'minVertex', 'id']

    print()
    print(header)

    for i, item in enumerate(items):
        if isinstance(item, dict):
            data = {key: value for key, value in item.items() if key not in exclude}
            index = i
            title = "Partial map"
            if "id" in item:
                index = item["id"]
                title = "Island"
            print("{} {} :".format(title, index), data)
        else:
            print(item)


def mirrorWeights(obj, axis, direction, tolerance):
    """Mirror the weights of all or only selected vertices.

    :param obj: The object.
    :type obj: bpy.types.Object
    :param axis: The symmetry axis.
    :type axis: str
    :param direction: The direction of the mirror.
    :type direction: int
    :param tolerance: The tolerance for matching vertices.
    :type tolerance: float

    :return: A message string.
    :rtype: str
    """
    weightObj = weights.Weights(obj)

    axisIndex = AXIS_INDICES[axis]
    directionIndex = DIRECTION_INDICES[direction]

    verts = set()
    if obj.mode == 'EDIT':
        verts = utils.getVertexSelection(obj)
    else:
        # Get all vertices on one side of the symmetry axis.
        for vert in obj.data.vertices:
            if ((directionIndex and vert.co[axisIndex] >= -tolerance) or
                    (not directionIndex and vert.co[axisIndex] <= tolerance)):
                verts.add(vert.index)

    indices = []
    weightData = []

    orderMap = obj.data[PROPERTY_NAME]

    for index in verts:
        weightList = weightObj.vertexWeights(index, sparse=True)
        vertWeights = weightObj.mirrorGroupAssignment(weightList)

        # Only mirror the weights if there are weight values to set and
        # if the target index is known.
        if len(vertWeights) and orderMap[index] != -1:
            indices.append(orderMap[index])
            weightData.append(vertWeights)

    weightObj.setVertexWeights(indices, weightData, clearAll=True, editMode=True)

    return "Mirrored {}".format(utils.pluralize(len(verts), "weight", "vertex"))


# ----------------------------------------------------------------------
# Properties
# ----------------------------------------------------------------------

class SymmetryMap_Properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    axis: bpy.props.EnumProperty(name="Axis",
                                 items=(('X', "X", "Symmetry on the x axis"),
                                        ('Y', "Y", "Symmetry on the y axis"),
                                        ('Z', "Z", "Symmetry on the z axis")),
                                 default=AXIS,
                                 description=ANN_AXIS)

    direction: bpy.props.EnumProperty(name="Direction",
                                      items=(('POSITIVE', "Positive", "Mirror positive to negative", 'TRIA_LEFT', 0),
                                             ('NEGATIVE', "Negative", "Mirror negative to positive", 'TRIA_RIGHT', 1)),
                                      default=DIRECTION,
                                      description=ANN_DIRECTION)

    tolerance: bpy.props.FloatProperty(default=TOLERANCE,
                                       min=0,
                                       precision=4,
                                       description=ANN_TOLERANCE)

    verbose: bpy.props.BoolProperty(default=VERBOSE,
                                    description=ANN_VERBOSE)


# ----------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------

class SYMMETRYMAP_OT_createMap(bpy.types.Operator):
    """Operator class for creating the symmetry map.
    """
    bl_idname = "symmetrymap.create_map"
    bl_label = "Create Map"
    bl_description = "Create a new symmetry map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        sm = context.object.data.symmetry_map

        # Get the mapping settings.
        axis = sm.axis
        tolerance = sm.tolerance
        verbose = sm.verbose

        start = time.time()
        info = createMap(context.object, axis, tolerance, verbose)
        duration = time.time() - start

        self.report({'INFO'}, "Mapping finished in {:.3f} seconds. {}".format(duration, info))

        return {'FINISHED'}


class SYMMETRYMAP_OT_deleteMap(bpy.types.Operator):
    """Operator class for deleting the symmetry map.
    """
    bl_idname = "symmetrymap.delete_map"
    bl_label = "Delete Map"
    bl_description = "Delete the symmetry map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = deleteMap(context.object)
        self.report(result[0], result[1])
        return {'FINISHED'}


class SYMMETRYMAP_OT_addToMap(bpy.types.Operator):
    """Operator class for adding one or more islands to the map.
    """
    bl_idname = "symmetrymap.add_to_map"
    bl_label = "Add To Map"
    bl_description = "Add a single island or island pair to the map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        sm = context.object.data.symmetry_map

        # Get the mapping settings.
        axis = sm.axis
        tolerance = sm.tolerance
        verbose = sm.verbose

        start = time.time()
        info = addToMap(context.object, axis, tolerance, verbose)
        duration = time.time() - start

        self.report({'INFO'}, "Mapping finished in {:.3f} seconds. {}".format(duration, info))

        return {'FINISHED'}


class SYMMETRYMAP_OT_addPartialToMap(bpy.types.Operator):
    """Operator class for adding partial symmetry to the map.
    """
    bl_idname = "symmetrymap.add_partial"
    bl_label = "Add Partial Symmetry"
    bl_description = "Add partial symmetry to the map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        sm = context.object.data.symmetry_map

        # Get the mapping settings.
        axis = sm.axis
        tolerance = sm.tolerance

        start = time.time()
        info = addPartialToMap(context.object, axis, tolerance)
        duration = time.time() - start

        self.report({'INFO'}, "Partial mapping finished in {:.3f} seconds. {}".format(duration, info))

        return {'FINISHED'}


class SYMMETRYMAP_OT_selectMapped(bpy.types.Operator):
    """Operator class for selecting mapped vertices.
    """
    bl_idname = "symmetrymap.select_mapped"
    bl_label = "Select Mapped"
    bl_description = "Select mapped vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = selectMapped(context.object)
        self.report(result[0], result[1])
        return {'FINISHED'}


class SYMMETRYMAP_OT_selectUnmapped(bpy.types.Operator):
    """Operator class for selecting unmapped vertices.
    """
    bl_idname = "symmetrymap.select_unmapped"
    bl_label = "Select Unmapped"
    bl_description = "Select unmapped vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = selectUnmapped(context.object)
        self.report(result[0], result[1])
        return {'FINISHED'}


class SYMMETRYMAP_OT_selectSibling(bpy.types.Operator):
    """Operator class for selecting sibling vertices.
    """
    bl_idname = "symmetrymap.select_sibling"
    bl_label = "Select Sibling"
    bl_description = "Select sibling vertices based on the current selection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = selectSibling(context.object)
        self.report(result[0], result[1])
        return {'FINISHED'}


class SYMMETRYMAP_OT_mirrorWeights(bpy.types.Operator):
    """Operator class for mirroring vertex weights.
    """
    bl_idname = "symmetrymap.mirror_weights"
    bl_label = "Mirror Weights"
    bl_description = "Mirror the weights of all or only selected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        sm = context.object.data.symmetry_map

        # Get the mapping settings.
        axis = sm.axis
        direction = sm.direction
        tolerance = sm.tolerance

        start = time.time()
        info = mirrorWeights(context.object, axis, direction, tolerance)
        duration = time.time() - start

        self.report({'INFO'}, "Mirror weights finished in {:.3f} seconds. {}".format(duration, info))

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Panel
# ----------------------------------------------------------------------

class SYMMETRYMAP_PT_settings(bpy.types.Panel):
    """Panel class.
    """
    bl_label = "Symmetry Map"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        """Returns, if the panel is visible.

        :param context: The current context.
        :type context: bpy.context

        :return: True, if the panel should be visible.
        :rtype: bool
        """
        return isinstance(context.object.data, bpy.types.Mesh)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        sm = context.object.data.symmetry_map

        info, icon, isValid = getMapInfo(context.object)

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.label(text="Mapping")

        box = layout.box()
        col = box.column(align=True)
        if info:
            infoBox = col.box()
            infoCol = infoBox.column(align=True)
            infoCol.label(text=info, icon=icon)
            col.separator()
        row = col.row()
        row.prop(sm, "axis", text=AXIS_LABEL, expand=True)
        col.prop(sm, "tolerance", text=TOLERANCE_LABEL)
        col.prop(sm, "verbose", text=VERBOSE_LABEL)
        col.separator()
        col.operator("symmetrymap.create_map", icon='PRESET_NEW')
        col.separator()
        col.operator("symmetrymap.add_to_map", icon='ADD')
        col.operator("symmetrymap.add_partial")
        col.separator()
        col.operator("symmetrymap.select_mapped", icon='RESTRICT_SELECT_OFF')
        col.operator("symmetrymap.select_unmapped", icon='RESTRICT_SELECT_ON')
        col.operator("symmetrymap.select_sibling", icon='UV_SYNC_SELECT')
        col.separator()
        col.operator("symmetrymap.delete_map", icon='TRASH')
        col.separator()

        if isValid:
            row = layout.row()
            row.label(text="Mirroring")

            box = layout.box()
            col = box.column(align=True)
            row = col.row()
            row.prop(sm, "direction", text=DIRECTION_LABEL, expand=True)
            col.separator()
            col.operator("symmetrymap.mirror_weights", icon='MOD_MIRROR')


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [SymmetryMap_Properties,
           SYMMETRYMAP_OT_createMap,
           SYMMETRYMAP_OT_deleteMap,
           SYMMETRYMAP_OT_addToMap,
           SYMMETRYMAP_OT_addPartialToMap,
           SYMMETRYMAP_OT_selectMapped,
           SYMMETRYMAP_OT_selectUnmapped,
           SYMMETRYMAP_OT_selectSibling,
           SYMMETRYMAP_OT_mirrorWeights,
           SYMMETRYMAP_PT_settings]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Mesh.symmetry_map = bpy.props.PointerProperty(type=SymmetryMap_Properties)


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Mesh.symmetry_map
