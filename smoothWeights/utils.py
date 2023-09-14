# <pep8 compliant>

from . import constants as const

import bpy
import bmesh

from mathutils import kdtree


def srgb_to_linear(value):
    """Convert the given sRGB value to a linear value.

    :param value: The sRGB value to convert.
    :type value: float

    :return: The linear value.
    :rtype: float
    """
    if value <= 0.0404482362771082:
        return value / 12.92
    else:
        return pow(((value + 0.055) / 1.055), 2.4)


def linear_to_srgb(value):
    """Convert the given linear value to a sRGB value.

    :param value: The linear value to convert.
    :type value: float

    :return: The sRGB value.
    :rtype: float
    """
    if value > 0.0031308:
        return 1.055 * (pow(value, (1.0 / 2.4))) - 0.055
    else:
        return 12.92 * value


def isEquivalent(vector1, vector2, tolerance=1e-6):
    """Return, if the given vectors are equivalent to each other.

    :param vector1: The first vector to compare.
    :type vector1: Vector
    :param vector2: The second vector to compare.
    :type vector2: Vector
    :param tolerance: The allowed tolerance between the vectors.
    :type tolerance: float

    :return: True, if the vectors are equivalent to each other.
    :rtype: bool
    """
    return (vector1 - vector2).length_squared <= tolerance * tolerance


def clamp(value, minVal, maxVal):
    """Clamp to given value to the min and max range.

    :param value: The value to clamp.
    :type value: float
    :param minVal: The minimum allowed value.
    :type minVal: float
    :param maxVal: The maximum allowed value.
    :type maxVal: float

    :return: The clamped value.
    :rtype: float
    """
    value = max(min(value, maxVal), minVal)
    return value


def isBackface(viewVector, faceNormal):
    """Return, if the given face normal is pointing away from the view.

    :param viewVector: The viewing vector.
    :type viewVector: Vector
    :param faceNormal: The normal of the face.
    :type faceNormal: Vector

    :return: True, if the face is pointing away.
    :rtype: bool
    """
    viewVector.normalize()
    faceNormal.normalize()
    return viewVector.dot(faceNormal) > 0


def replaceSideIdentifier(name):
    """Replace the side identifier in the given name with the opposite
    side identifier.

    :param name: The name to replace.
    :type name: str

    :return: The name with the replaced side identifier.
    :rtype: str
    """
    for delimiter in [".", "_", "-"]:
        words = name.split(delimiter)
        for index, word in sorted(enumerate(words), reverse=True):
            for label in const.SIDE_LABELS:
                for i in range(3):
                    left = label
                    right = const.SIDE_LABELS[label]
                    if i == 1:
                        left = label.capitalize()
                        right = const.SIDE_LABELS[label].capitalize()
                    elif i == 2:
                        left = label.upper()
                        right = const.SIDE_LABELS[label].upper()

                    if word == left:
                        words[index] = word.replace(left, right)
                        return delimiter.join(words)

                    if word == right:
                        words[index] = word.replace(right, left)
                        return delimiter.join(words)

    # Return the name if there is no side identifier.
    return name


def pluralize(count, string, prefix=""):
    """Pluralize the given string based on the given count.

    :param count: The item count or list of counts to compare.
    :type count: int or list(int)
    :param string: The string to pluralize.
    :type string: str
    :param prefix: The optional prefix string.
    :type prefix: str

    :return: The formatted string.
    :rtype: str
    """
    if isinstance(count, list):
        countStr = "/".join([str(i) for i in count])
        num = count[1]
    else:
        countStr = str(count)
        num = count

    if len(prefix):
        label = " ".join([prefix, string])
    else:
        label = string

    if num > 1:
        return "{} {}s".format(countStr, label)
    return "{} {}".format(countStr, label)


def kdTree(bm, size):
    """Build a KDTree for a fast volume search.

    :param bm: The bmesh object.
    :type bm: bmesh.types.BMesh
    :param size: The number of elements to store.
    :type size: int

    :return: The kdtree.
    :rtype: kdtree instance
    """
    kd = kdtree.KDTree(size)
    for i in range(size):
        pos = bm.verts[i].co
        kd.insert(pos, i)
    kd.balance()
    return kd


def getVertexSelection(obj):
    """Return the currently selected vertices in edit mode.

    :param obj: The mesh object.
    :type obj: bpy.types.Object

    :return: The set of selected vertex indices.
    :rtype: set
    """
    verts = set()

    # Create a bmesh to properly get the current vertex selection.
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    # Get the selection.
    for vert in bm.verts:
        if vert.select:
            verts.add(vert.index)
    # Free the memory.
    bm.free()

    return verts


def getSymmetryPointDelta(vert1, vert2, axisIndex):
    """Return the relative distance between two symmetry vertices.

    :param vert1: The first vertex.
    :type vert1: bmesh.types.Vert
    :param vert2: The second vertex.
    :type vert2: bmesh.types.Vert
    :param axisIndex: The 0-based axis index.
    :type axisIndex: int

    :return: The relative distance between the two points.
    :rtype: float
    """
    pos1 = vert1.co.copy()
    pos2 = vert2.co.copy()
    pos2[axisIndex] *= -1

    return (pos1 - pos2).length


def averageEdgeLength(vert):
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


def averageEdgeLengthTotal(obj):
    """Return the average edge length of the entire mesh.

    Only every fourth vertex will be considered.

    :param obj: The mesh object.
    :type obj: bpy.types.Object

    :return: The average mesh edge length.
    :rtype: float
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    length = 0.0
    count = 0
    for i, vert in enumerate(bm.verts):
        if i % 4 == 0:
            length += averageEdgeLength(vert)
            count += 1

    bm.free()

    return length / count


def sortDict(data, reverse=False, maxCount=None):
    """Sort the values in the given dictionary.

    :param data: The dictionary to sort.
    :type data: dict
    :param reverse: True, if the sorting should be reversed, from high
                    to low.
    :type reverse: bool
    :param maxCount: The maximum number of entries.
    :type maxCount: int or None

    :return: The sorted dictionary.
    :rtype: dict
    """
    if maxCount is None:
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=reverse))
    else:
        return dict(sorted(data.items(), key=lambda x: x[1], reverse=reverse)[:maxCount])
