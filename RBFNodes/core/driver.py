# <pep8 compliant>

import bpy

from . import nodeTree
from .. import dev


def generateDrivers(nodeGroup, rbfNode):
    """Create new driving relationships between the output properties
    and the driven objects.

    :param nodeGroup: The node group (node tree) of the current RBF
                      setup.
    :type nodeGroup: bpy.types.NodeGroup
    :param rbfNode: The RBF node to get the pose data for.
    :type rbfNode: bpy.types.Node

    :return: None, or a tuple with the error type and message.
    :rtype: None or tuple(str, str)
    """
    outNodes = nodeTree.getRBFOutputNodes(rbfNode)
    for obj in outNodes:
        for outNode in outNodes[obj]:
            outNode.createDriver(nodeGroup, obj, rbfNode)
            # Hide the node if the output has been connected to a driver.
            # outNode.hide = outNode.isDriver

            if outNode.isDriver:
                dev.log("Driver Indices for {}:".format(outNode.name))
                dev.log([i for i in outNode.driverIndex])


def createNodeGroupDriver(nodeGroup, node, driverProp, drivenProp, index=-1):
    """Create a driver on the given node.

    :param nodeGroup: The node tree of the node which is the source of the
                      driver.
    :type nodeGroup: bpy.types.NodeGroup
    :param node: The driven node.
    :type node: bpy.types.Node
    :param driverProp: The driver node and property.
    :type driverProp: str
    :param drivenProp: The property to be driven.
    :type drivenProp: str
    :param index: The index of the driven property.
    :type index: int

    Example:
    createNodeGroupDriver(nodeGroup, outputObj, 'nodes["Scale"].output[0]', 'scale', 0)
    """
    drv = node.driver_add(drivenProp, index).driver
    drv.type = 'AVERAGE'
    newVar = drv.variables.new()
    newVar.name = "var"
    newVar.type = 'SINGLE_PROP'
    newVar.targets[0].id_type = 'NODETREE'
    newVar.targets[0].id = nodeGroup
    newVar.targets[0].data_path = driverProp


def getTransformDriverIndex(obj, driverPath, drivenProp, propertyIndex):
    """Return the index of the driver for the given object which matches
    the given driver data path and driven property and index.

    :param obj: The object to query.
    :type obj: bpy.types.Object
    :param driverPath: The data path of the driver as displayed in the
                       driver window.
    :type driverPath: str
    :param drivenProp: The driven transform property.
    :type drivenProp: str
    :param propertyIndex: The index of the driven property.
    :type propertyIndex: int

    :return: The index of the driver in the data block.
    :rtype: int
    """
    return getDriverIndex(obj, driverPath, drivenProp, propertyIndex)


def getDriverIndex(obj, driverPath, drivenProp, propertyIndex):
    """Return the index of the driver for the given object which matches
    the given driver data path and driven property and index.

    :param obj: The object to query.
    :type obj: bpy.types.Object
    :param driverPath: The data path of the driver as displayed in the
                       driver window.
    :type driverPath: str
    :param drivenProp: The driven transform property.
    :type drivenProp: str
    :param propertyIndex: The index of the driven property.
    :type propertyIndex: int

    :return: The index of the driver in the data block.
    :rtype: int
    """
    if isinstance(obj, bpy.types.PoseBone):
        # For a regular object drivenProp contains the name of the
        # property, i.e. location or rotation_euler.
        # A pose bone needs a pose bone prefix with the name of the
        # bone.

        # In case of a transform property a dot separator is required.
        if not drivenProp.startswith("["):
            drivenProp = ".{}".format(drivenProp)

        drivenProp = "".join(['pose.bones["{}"]'.format(obj.name), drivenProp])
        obj = obj.id_data
        driverBlock = obj.animation_data.drivers
    elif isinstance(obj, bpy.types.ShaderNodeTree):
        driverBlock = obj.animation_data.drivers
    else:
        driverBlock = obj.animation_data.drivers

    for i, drv in enumerate(driverBlock):
        # When setting single properties the array index has to be -1.
        # But then querying the array index it only returns 0.
        # Therefore, the given property index needs to be transformed.
        propertyIndex = 0 if propertyIndex == -1 else propertyIndex
        if drv.data_path == drivenProp and drv.array_index == propertyIndex:
            for v in drv.driver.variables:
                for target in v.targets:
                    if target.data_path == driverPath:
                        return i
    return -1


def getShapeKeyDriverIndex(driverPath):
    """Return the index of the driver for the given object which matches
    the given driver data path and driven property and index.

    :param driverPath: The data path of the driver as displayed in the
                       driver window.
    :type driverPath: str

    :return: The index of the driver in the data block.
    :rtype: int
    """
    for i, drv in enumerate(bpy.data.shape_keys["Key"].animation_data.drivers):
        for v in drv.driver.variables:
            for target in v.targets:
                if target.data_path == driverPath:
                    return i


# ----------------------------------------------------------------------
# Common node methods
# ----------------------------------------------------------------------

def createTransformDriver(node, nodeGroup, driven, transform, rbfNode):
    """Create a driver for each selected axis of the driven object.

    :param node: The node.
    :type node: bpy.types.Node
    :param nodeGroup: The node tree of the current RBF setup.
    :type nodeGroup: bpy.types.NodeGroup
    :param driven: The driven object.
    :type driven: bpy.types.Object
    :param transform: The transform type string. (i.e. location, scale)
    :type transform: str
    :param rbfNode: The current RBF node.
    :type rbfNode: bpy.types.Node
    """
    # Clear the driver indices.
    node.driverIndex = [-1, -1, -1]
    # Delete any existing driver.
    if rbfNode.active:
        deleteTransformDriver(node, driven, transform)

    axes = [(node.x_axis, 0), (node.y_axis, 1), (node.z_axis, 2)]
    for axis, index in axes:
        if axis:
            dataPath = 'nodes["{}"].output[{}]'.format(node.name, str(index))
            createNodeGroupDriver(nodeGroup, driven, dataPath, transform, index)
            # Get the index of the created driver.
            node.driverIndex[index] = getDriverIndex(driven, dataPath, transform, index)
            node.isDriver = True


def deleteTransformDriver(node, obj, transform):
    """Delete the driver for the given object.

    :param node: The node.
    :type node: bpy.types.Node
    :param obj: The driven object.
    :type obj: bpy.types.Object
    :param transform: The transform type string. (i.e. location, scale)
    :type transform: str
    """
    axes = [(node.x_axis, 0), (node.y_axis, 1), (node.z_axis, 2)]
    for axis, index in axes:
        if axis:
            result = obj.driver_remove(transform, index)
            dev.log("Delete driver: {} {}[{}] : {}".format(obj, transform, index, result))

    # Clear the driver indices.
    node.driverIndex = [-1, -1, -1]


def enableDriver(node, obj, enable):
    """Enable or disable the driver FCurves for the given object.

    :param node: The node.
    :type node: bpy.types.Node
    :param obj: The driven object.
    :type obj: bpy.types.Object
    :param enable: The enabled state of the driver FCurves.
    :type enable: bool
    """
    if isinstance(obj, bpy.types.PoseBone):
        obj = obj.id_data
    elif isinstance(obj, bpy.types.Object):
        obj = obj.data

    for i in range(len(node.driverIndex)):
        index = node.driverIndex[i]
        if index != -1:
            try:
                obj.animation_data.drivers[index].mute = not enable
            except IndexError:
                pass
