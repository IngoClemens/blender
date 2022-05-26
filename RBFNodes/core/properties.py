# <pep8 compliant>

import bpy
import idprop


def customProperties(obj):
    """Return a list with the custom properties of the given object.

    :param obj: The object to get the properties from.
    :type obj: bpy.types.Object

    :return: The list with the custom properties.
    :rtype: list(str)
    """
    props = []
    for prop in obj.keys():
        if prop not in '_RNA_UI' and isinstance(obj[prop], (int, float, list, idprop.types.IDPropertyArray)):
            props.append(prop)
    return props


def nodeProperties(node, fromInput=True):
    """Return a list with the node properties of the given object.

    :param node: The node to get the properties from.
    :type node: bpy.types.Node or bpy.types.NodeGroup
    :param fromInput: True, if the input properties should be returned.
    :type fromInput: bool

    :return: The list with the node properties and the socket string as
             a tuple.
    :rtype: list(tuple(str, str))
    """
    if fromInput:
        plugs = node.inputs
        name = "inputs"
    else:
        plugs = node.outputs
        name = "outputs"

    props = []
    for i, plug in enumerate(plugs):
        value = plug.default_value
        if isinstance(value, (int, float, list, bpy.types.bpy_prop_array)):
            props.append((plug.name, "{}[{}]".format(name, i)))
    return props


def expandProperty(obj, name):
    """Return the name of the property or names in case of an array
    property.

    :param obj: The object the property belongs to.
    :type obj: bpy.types.Object
    :param name: The name of the property
    :type name: str

    :return: A list with the property or property items.
    :rtype: list(str)
    """
    if name in customProperties(obj):
        value = eval("obj['{}']".format(name))
        if isinstance(value, idprop.types.IDPropertyArray):
            return [('property:["{}"][{}]'.format(name, i), value[i]) for i in range(len(value))]
        else:
            return [('property:["{}"]'.format(name), value)]
    else:
        return []


def expandNodeProperty(nodeString, plugString):
    """Return the name of the property or names in case of an array
    property.

    :param nodeString: The node as a string.
    :type nodeString: str
    :param plugString: The string representing the input or output
                       including the index.
    :type plugString: str

    :return: A list with the property or property items.
    :rtype: list(str)
    """
    plug = eval(".".join((nodeString, plugString)))
    value = plug.default_value
    if isinstance(value, bpy.types.bpy_prop_array):
        # In general an array property would include the index ([j]) at
        # the end but this causes issues when creating or removing
        # drivers, since the index needs to be passed separately.
        # Therefore, adding the index would be mainly for readability
        # when exposing the data but wouldn't have any practical use.
        return [('{}:{}.default_value'.format(nodeString, plugString), value[j])
                for j in range(len(value))]
    else:
        return [('{}:{}.default_value'.format(nodeString, plugString), value)]
