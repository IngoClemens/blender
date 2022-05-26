# <pep8 compliant>

import bpy

from ... core import plugs, properties, shapeKeys
from ... import var


# ----------------------------------------------------------------------
# Location
# ----------------------------------------------------------------------

def drawTransformProperties(node, layout):
    """Add the common location properties to the node.

    :param node: The location node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    row = layout.row(align=True)
    row.prop(node, "x_axis")
    row.prop(node, "y_axis")
    row.prop(node, "z_axis")


def getLocationProperties(node, obj):
    """Return the selected location properties for the given object.

    :param node: The location node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected location properties and their
             values as a tuple.
    :rtype: list(tuple(str, float))
    """
    result = []
    location = obj.location

    if node.x_axis:
        result.append(("location[0]", location[0]))
    if node.y_axis:
        result.append(("location[1]", location[1]))
    if node.z_axis:
        result.append(("location[2]", location[2]))

    return result


def getTransformOutputProperties(node):
    """Return the selected output properties.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with the selected output properties and their
             index as a tuple.
    :rtype: list(bpy.types.Node, int)
    """
    result = []

    if node.x_axis:
        result.append((node, 0))
    if node.y_axis:
        result.append((node, 1))
    if node.z_axis:
        result.append((node, 2))

    return result


# ----------------------------------------------------------------------
# Rotation
# ----------------------------------------------------------------------

def drawRotationProperties(node, layout):
    """Add the common rotation properties to the node.

    :param node: The rotation node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    layout.prop(node, "rotationMode")
    # if node.rotationMode == 'QUATERNION':
    #     layout.prop(node, "rotationType")

    row = layout.row(align=True)
    if node.rotationMode != 'EULER':
        row.prop(node, "w_axis")
    row.prop(node, "x_axis")
    row.prop(node, "y_axis")
    row.prop(node, "z_axis")


def getRotationProperties(node, obj):
    """Return the selected rotation properties for the given object.

    :param node: The rotation node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected rotation properties and their
             values as a tuple.
    :rtype: list(tuple(str, float))
    """
    result = []
    index = 0

    if node.rotationMode == 'EULER':
        rotation = obj.rotation_euler
    elif node.rotationMode == 'QUATERNION':
        rotation = obj.rotation_quaternion
    else:
        rotation = obj.rotation_axis_angle

    if node.rotationMode != 'EULER':
        if node.w_axis:
            result.append(("{}[{}]".format(var.ROTATIONS[node.rotationMode], index), rotation[index]))
        index = 1

    if node.x_axis:
        result.append(("{}[{}]".format(var.ROTATIONS[node.rotationMode], 0+index), rotation[0+index]))
    if node.y_axis:
        result.append(("{}[{}]".format(var.ROTATIONS[node.rotationMode], 1+index), rotation[1+index]))
    if node.z_axis:
        result.append(("{}[{}]".format(var.ROTATIONS[node.rotationMode], 2+index), rotation[2+index]))

    return result


# ----------------------------------------------------------------------
# Scale
# ----------------------------------------------------------------------

def getScaleProperties(node, obj):
    """Return the selected scale properties for the given object.

    :param node: The scale node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected scale properties and their values
             as a tuple.
    :rtype: list(tuple(str, float))
    """
    result = []
    scale = obj.scale

    if node.x_axis:
        result.append(("scale[0]", scale[0]))
    if node.y_axis:
        result.append(("scale[1]", scale[1]))
    if node.z_axis:
        result.append(("scale[2]", scale[2]))

    return result


# ----------------------------------------------------------------------
# Custom Property
# ----------------------------------------------------------------------

def getObjectProperties(node, source=True):
    """Return a list with all custom property names of the connected
    object.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all custom property names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return properties.customProperties(obj)

    return []


def customLabelCallback(node):
    """Callback for updating the node label based on the property
    selection.

    :param node: The custom property node.
    :type node: bpy.types.Node
    """
    if node.mode == 'LIST':
        node.label = node.propertyEnum
    else:
        node.label = node.propertyName


def customItemsCallback(node, source=True):
    """Callback for the property drop down menu to collect the names of
    all custom properties of the connected object.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', "––– Select –––", "")]

    for prop in getObjectProperties(node, source):
        props.append((prop, prop, ""))

    return props


def drawCustomProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The property node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    layout.prop(node, "mode", expand=True)
    if node.mode == 'LIST':
        layout.prop(node, "propertyEnum")
    else:
        layout.prop(node, "propertyName")


def getCustomProperties(node, obj):
    """Return the name of the selected custom property.

    :param node: The custom property node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: A list with the selected custom property and the value as a
             tuple.
    :rtype: list(tuple(str, float))
    """
    if node.mode == 'LIST':
        if node.propertyEnum != 'NONE':
            return properties.expandProperty(obj, node.propertyEnum)
    else:
        if len(node.propertyName):
            return properties.expandProperty(obj, node.propertyName)

    return []


# ----------------------------------------------------------------------
# Shape Key
# ----------------------------------------------------------------------

def getObjectShapeKeys(node, source=True):
    """Return a list with all shape key names of the connected
    object.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with all shape key names.
    :rtype: list(str)
    """
    if source:
        plug = node.inputs[0]
    else:
        plug = node.outputs[0]

    obj = plugs.getObjectFromSocket(plug, source)
    if obj:
        return [k for k, v in shapeKeys.shapeKeyProperties(obj).items()]
    return []


def shapeKeyLabelCallback(node):
    """Callback for updating the node label based on the shape key
    selection.

    :param node: The shape key node.
    :type node: bpy.types.Node
    """
    if node.mode == 'LIST':
        node.label = node.shapeNameEnum
    else:
        node.label = node.shapeName


def shapeKeyItemsCallback(node, source=True):
    """Callback for the property drop down menu to collect the names
    of all shape keys of the connected object.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', "––– Select –––", "")]

    for prop in getObjectShapeKeys(node, source):
        props.append((prop, prop, ""))

    return props


def drawShapeKeyProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    layout.prop(node, "mode", expand=True)
    if node.mode == 'LIST':
        layout.prop(node, "shapeNameEnum")
    else:
        layout.prop(node, "shapeName")


def getShapeKeyProperties(node, obj):
    """Return the name of the selected shape key.

    :param node: The shape key node.
    :type node: bpy.types.Node
    :param obj: The object to query.
    :type obj: bpy.types.Object

    :return: The selected shape key name and the value as a tuple.
    :rtype: tuple(str, float)
    """
    if node.mode == 'LIST':
        if node.shapeNameEnum != 'NONE':
            name = "shapeKey:{}".format(node.shapeNameEnum)
            value = obj.data.shape_keys.key_blocks[node.shapeNameEnum].value
            return [(name, value)]
    else:
        if len(node.name):
            name = "shapeKey:{}".format(node.shapeName)
            value = obj.data.shape_keys.key_blocks[node.shapeName].value
            return [(name, value)]

    return []


# ----------------------------------------------------------------------
# Node
# ----------------------------------------------------------------------

def getTreeNodeProperties(node):
    """Return a list with all custom property names of the connected
    object.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with all custom property names.
    :rtype: list(str)
    """
    if len(node.parentName) and len(node.nodeName):
        if node.nodeParent == 'MATERIAL':
            node = bpy.data.materials[node.parentName].node_tree.nodes[node.nodeName]
        else:
            node = bpy.data.node_groups[node.parentName].nodes[node.nodeName]

        nodeProps = properties.nodeProperties(node, fromInput=True)
        if not nodeProps:
            nodeProps = properties.nodeProperties(node, fromInput=False)
        return nodeProps

    return []


def nodeItemsCallback(node, context):
    """Callback for the property drop down menu to collect the names
    of all custom properties of the connected object.

    :param node: The node.
    :type node: bpy.types.Node
    :param context: The current context.
    :type context: bpy.context

    :return: A list with tuple items for the enum property.
    :rtype: list(tuple(str))
    """
    props = [('NONE', "––– Select –––", "")]

    for prop, plug in getTreeNodeProperties(node):
        props.append((prop, prop, ""))
        node.propertyPlugs[prop] = plug

    return props


def setPropertyPlugName(node, context):
    """Set the property plug name depending on the current property
    selection.

    :param node: The node.
    :type node: bpy.types.Node
    :param context: The current context.
    :type context: bpy.context
    """
    if node.propertyEnum != 'NONE':
        node.plugName = node.propertyPlugs[node.propertyEnum]
    else:
        node.plugName = ""

    # Set the label
    node.label = ": ".join([node.nodeName, node.propertyEnum])


def drawNodeProperties(node, layout):
    """Add the common custom properties to the node.

    :param node: The node.
    :type node: bpy.types.Node
    :param layout: The current layout.
    :type layout: bpy.types.UILayout
    """
    layout.prop(node, "nodeParent")
    layout.prop(node, "parentName")
    layout.prop(node, "nodeName")
    layout.prop(node, "plugName")
    layout.prop(node, "propertyEnum")


def getNodeProperties(node):
    """Return the name of the selected node property.

    :param node: The node.
    :type node: bpy.types.Node

    :return: A list with the selected node property and the value
             as a tuple.
    :rtype: list(tuple(str, float))
    """
    if len(node.parentName) and len(node.nodeName) and len(node.plugName):
        if node.nodeParent == 'MATERIAL':
            nodeString = 'bpy.data.materials["{}"].node_tree.nodes["{}"]'.format(node.parentName, node.nodeName)
        else:
            nodeString = 'bpy.data.node_groups["{}"].nodes["{}"]'.format(node.parentName, node.nodeName)
        return properties.expandNodeProperty(nodeString, node.plugName)

    return []
