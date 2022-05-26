# <pep8 compliant>

import bpy


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
