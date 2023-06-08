# <pep8 compliant>

import bpy

from . import nodeTree, plugs, utils
from .. import dev, var

import json
from mathutils import Quaternion


class EditMode(object):
    """Class for the edit mode state.
    """
    def __init__(self):
        self.state = False


editMode = EditMode()


def createPose(context):
    """Create a new pose node.

    :param context: The current context.
    :type context: bpy.context

    :return: None, or a tuple with the error type and message.
    :rtype: None or tuple(str, str)
    """
    nodeGroup = nodeTree.getNodeTree(context)
    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode:
        # Get the current pose data from the object properties.
        driverData = getPoseInputData(rbfNode)
        drivenData = getPoseOutputData(rbfNode)

        # If the second tuple item is a string an error has occurred.
        # In this case the driverData is the error type and the driven
        # data is the message.
        if len(driverData) > 1 and isinstance(driverData[1], str):
            return driverData
        if len(drivenData) > 1 and isinstance(drivenData[1], str):
            return drivenData

        # Check for valid data.
        if not driverData:
            return {'WARNING'}, "No driver object or properties defined"
        if not drivenData:
            return {'WARNING'}, "No driven object or properties defined"

        dev.log("Driver Data:")
        dev.log(driverData)
        dev.log("Driven Data:")
        dev.log(drivenData)

        # Get all pose nodes.
        poseNodes = nodeTree.getPoseNodes(rbfNode)
        # Create a pose index.
        index = lastPoseIndex(poseNodes)+1
        label = "Pose {}".format(index)

        if len(poseNodes):
            # Compare, if the number of driver properties matches.
            result = comparePoseSize(driverData, poseNodes[-1], isDriver=True)
            if result is not None:
                return result

            # Check for the difference in driven pose values.
            newPoseData = getPoseDataDifference(drivenData, poseNodes[-1])
            if len(newPoseData):
                # Add new shape key properties to existing poses.
                result = appendShapeKeyPoseData(newPoseData, poseNodes)
                if result is not None:
                    return result

        pos = nodeTree.sourceNodePosition(lastNode=None if not len(poseNodes) else poseNodes[-1],
                                          referenceNode=rbfNode,
                                          offset1=var.FIRST_POSE_OFFSET,
                                          offset2=var.POSE_OFFSET)

        # Create the node and link it.
        node = nodeGroup.nodes.new("RBFPoseNode")
        nodeGroup.links.new(node.outputs[0], rbfNode.inputs[2])
        if pos:
            node.location = pos

        # Set the pose data.
        node.label = label
        node.poseIndex = index
        node.driverData = json.dumps(driverData)
        node.drivenData = json.dumps(drivenData)
        node.driverSize = poseDataSize(driverData)
        node.drivenSize = poseDataSize(drivenData)
        dev.log("Pose Size: Driver - {} | Driven - {}".format(node.driverSize, node.drivenSize))

        if (len(poseNodes) + 1) * node.driverSize > var.MAX_SIZE:
            return {'WARNING'}, "Too many poses or input values"

        if len(poseNodes) * node.drivenSize > var.MAX_SIZE:
            return {'WARNING'}, "Too many poses or output values"

    else:
        return {'WARNING'}, "No RBF node to add pose to"


def poseDataSize(poseData):
    """Return the number of values contained in the given pose data for
    storing and comparing with new poses.

    :param poseData: The pose data of the driver or driven object.
    :type poseData: list

    :return: The number of driver or driven pose values.
    :rtype: int
    """
    count = 0
    for name, data in poseData:
        count += len(data)
    return count


def comparePoseSize(poseData, node, isDriver=True):
    """Compare the number of new pose values with the values on the
    given pose node. Return a warning if the numbers don't match.

    :param poseData: The new pose data.
    :type poseData: list
    :param node: The pose node to compare to.
    :type node: bpy.type.Nodes
    :param isDriver: True, if the data of the driver should be compared.
    :type isDriver: bool

    :return: A tuple with the warning message for the context or None.
    :rtype: tuple or None
    """
    newSize = poseDataSize(poseData)
    if isDriver:
        if node.driverSize != newSize:
            return {'WARNING'}, "The number of driver values differs from existing poses"
    else:
        if node.drivenSize != newSize:
            return {'WARNING'}, "The number of driven values differs from existing poses"


def getPoseDataDifference(newData, node):
    """Return a list with the pose data differences between the new pose
    and the stored data of the given node.

    :param newData: The new pose data.
    :type newData: list
    :param node: The pose node to compare to.
    :type node: bpy.type.Nodes

    :return: A list with the driven name and properties in case the data
             sets are different.
    :rtype: list(tuple(str, list(tuple(str, float, float/None))))
    """
    lastData = json.loads(node.drivenData)
    diffData = []
    for newName, newProps in newData:
        for lastName, lastProps in lastData:
            if newName == lastName:
                diffProps = []
                for newProp in newProps:
                    if newProp[0] not in [p[0] for p in lastProps]:
                        diffProps.append(newProp)
                if len(diffProps):
                    diffData.append((newName, diffProps))
    return diffData


def isShapeKeyData(poseData):
    """Return, if the given pose data only contains shape keys.

    :param poseData: The new pose data.
    :type poseData: list

    :return: True, if the data set only contains shape keys.
    :rtype: bool
    """
    for name, data in poseData:
        for prop in data:
            if not prop[0].startswith("shapeKey"):
                return False
    return True


def appendShapeKeyPoseData(poseData, nodes):
    """Append the new shape key pose data to all existing poses.

    :param poseData: The new pose data.
    :type poseData: list
    :param nodes: The list of currently connected poses.
    :type nodes: list(bpy.type.Nodes)

    :return: A tuple with the warning message for the context or None.
    :rtype: tuple or None
    """
    # Check that the new pose data only contains shape keys.
    if isShapeKeyData(poseData):
        # Add the default shape key value to each node.
        for node in nodes:
            drivenData = json.loads(node.drivenData)
            for name, props in poseData:
                for drivenName, drivenProps in drivenData:
                    if name == drivenName:
                        # For every shape key build a new data tuple and
                        # append it to the existing driven data set.
                        for prop in props:
                            drivenProps.append((prop[0], 0.0, None))
                        node.drivenData = json.dumps(drivenData)
                        dev.log("Added new shape key to existing pose: {} ({})".format(node.label, node.name))
    else:
        return {'WARNING'}, "The number of driven values differs from existing poses"


def lastPoseIndex(nodes):
    """Return the last used pose index, which can be used to define the
    pose index for a new pose.

    :param nodes: The list of currently connected poses.
    :type nodes: list(bpy.type.Nodes)

    :return: The last unused pose index.
             Returns -1 if no index has been used yet so that it can be
             incremented for use.
    :rtype: int
    """
    if not len(nodes):
        return -1

    indices = []
    for n in nodes:
        indices.append(n.poseIndex)
    indices.sort()
    return indices[-1]


def recallPose(context, nodeName):
    """Read the properties from the selected pose and apply them.

    :param context: The current context.
    :type context: bpy.context
    :param nodeName: The name of the pose node to get the pose from.
    :type nodeName: str
    """
    nodeGroup = nodeTree.getNodeTree(context)
    node = nodeGroup.nodes[nodeName]
    recallPoseForObject(json.loads(node.driverData))
    recallPoseForObject(json.loads(node.drivenData))


def getPoseInputData(rbfNode, editable=True):
    """Return all input properties and their values which define the
    current pose.

    :param rbfNode: The RBF node to get the pose data for.
    :type rbfNode: bpy.types.Node
    :param editable: Defines the editable state of the input nodes.
                     The nodes are not editable when the RBF is active.
                     When creating a new pose the RBF is inactive and
                     the nodes can be editable.
    :type editable: bool

    :return: A list with the driver properties.
    :rtype: list
    """
    driver = []

    nodeTree.setInputNodesEditable(rbfNode, state=editable)

    nodeTypes = ["RBFObjectInputNode", "RBFNodeInputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getInputNodes(rbfNode.inputs[i], nodeId=nodeType):
            obj, values = getDriverData(node)
            if obj and values:
                driver.append((obj, values))
            else:
                if not obj:
                    return {'WARNING'}, "No driving object selected"
                else:
                    return {'WARNING'}, "No driving properties defined"

    return driver


def getPoseOutputData(rbfNode, editable=True):
    """Return all output properties and their values which define the
    current pose.

    :param rbfNode: The RBF node to get the pose data for.
    :type rbfNode: bpy.types.Node
    :param editable: Defines the editable state of the input nodes.
                     The nodes are not editable when the RBF is active.
                     When creating a new pose the RBF is inactive and
                     the nodes can be editable.
    :type editable: bool

    :return: A list with the driven properties.
    :rtype: list
    """
    driven = []

    nodeTree.setOutputNodesEditable(rbfNode, state=editable)

    nodeTypes = ["RBFObjectOutputNode", "RBFNodeOutputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getOutputNodes(rbfNode.outputs[i], nodeId=nodeType):
            obj, values = getDrivenData(node)
            if obj and values:
                driven.append((obj, values))
            else:
                if not obj:
                    return {'WARNING'}, "No driven object selected"
                else:
                    return {'WARNING'}, "No driven properties defined"

    return driven


def getDriverData(node):
    """Return all input values for the given object node.

    :param node: The object input node.
    :type node: bpy.types.Node

    :return: The driver object as a string and a list with all input
             values of the driver.
    :rtype: str, list
    """
    obj = None
    values = []

    if node.bl_idname == "RBFObjectInputNode":
        obj = node.getObject()
        if not obj:
            return obj, values

        for socket in node.inputs:
            for inNode in plugs.getInputNodes(socket):
                data = inNode.getProperties(obj)
                if data:
                    values.extend(data)

        obj = objectToString(obj)

    elif node.bl_idname == "RBFNodeInputNode":
        data = node.getProperties()
        for dataItem in data:
            # The first tuple item contains the full path to the node
            # and the property, separated by a colon.
            items = dataItem[0].split(":")
            # Return the full node path as the object.
            obj = items[0]
            # Make a tuple from the property path, value and pose.
            values.append((items[1], dataItem[1], dataItem[2]))

    return obj, values


def getDrivenData(node):
    """Return all output values for the given object node.

    :param node: The object output node.
    :type node: bpy.types.Node

    :return: The driven object as a string and a list with all output
             values of the driven.
    :rtype: str, list
    """
    obj = None
    values = []

    if node.bl_idname == "RBFObjectOutputNode":
        obj = node.getObject()
        if not obj:
            return obj, values

        for socket in node.outputs:
            for outNode in plugs.getOutputNodes(socket):
                data = outNode.getProperties(obj)
                if data:
                    values.extend(data)

        obj = objectToString(obj)

    elif node.bl_idname == "RBFNodeOutputNode":
        data = node.getProperties()
        for dataItem in data:
            # The first tuple item contains the full path to the node
            # and the property, separated by a colon.
            items = dataItem[0].split(":")
            # Return the full node path as the object.
            obj = items[0]
            # Make a tuple from the property path, value and pose.
            values.append((items[1], dataItem[1], dataItem[2]))

    return obj, values


def getDriverValues(rbfNode):
    """Return all input values for all object nodes for the runtime
    weight calculation.

    :param rbfNode: The RBF node to get the pose data for.
    :type rbfNode: bpy.types.Node

    :return: A list with all input values of the drivers.
    :rtype: list(float)
    """
    values = []

    nodeTypes = ["RBFObjectInputNode", "RBFNodeInputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getInputNodes(rbfNode.inputs[i], nodeId=nodeType):
            if node.bl_idname == "RBFObjectInputNode":
                obj = node.getObject()
                if obj:
                    for socket in node.inputs:
                        for inNode in plugs.getInputNodes(socket):
                            data = inNode.getProperties(obj)
                            if data:
                                values.extend([value for prop, value, poseValue in data])
            elif node.bl_idname == "RBFNodeInputNode":
                data = node.getProperties()
                if data:
                    values.extend([value for prop, value, poseValue in data])

    return values


def getOutputProperties(rbfNode):
    """Return all output values for all object nodes for the runtime
    weight calculation.

    :param rbfNode: The RBF node to get the pose data for.
    :type rbfNode: bpy.types.Node

    :return: A list with all output properties and their indices as a
             tuple.
    :rtype: list(tuple(bpy.type.Node, int))
    """
    values = []

    nodeTypes = ["RBFObjectOutputNode", "RBFNodeOutputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getOutputNodes(rbfNode.outputs[i], nodeId=nodeType):
            if node.bl_idname == "RBFObjectOutputNode":
                obj = node.getObject()
                if obj:
                    for socket in node.outputs:
                        for outNode in plugs.getOutputNodes(socket):
                            data = outNode.getOutputProperties()
                            if data:
                                values.extend(data)
            elif node.bl_idname == "RBFNodeOutputNode":
                data = node.getOutputProperties()
                if data:
                    values.extend(data)

    return values


def objectToString(obj):
    """Convert the given object to a string representation so that it
    can be stored in a property.

    :param obj: The object to convert.
    :type obj: bpy.types.Object

    :return: The string representation of the object. In case of a bone
             the armature and bone are colon separated.
    :rtype: str
    """
    # In case of a node input or output node the given object is the
    # bl_idname string.
    if isinstance(obj, str):
        return obj

    if isinstance(obj, bpy.types.PoseBone):
        armature = obj.id_data
        return ":".join([armature.name, obj.name])
    else:
        return obj.name


def getPropertyCount(data):
    """Return the number of properties contained in the given data set.

    :param data: The list of objects and their properties for either
                 the drivers or the driven.
    :type data: list

    :return: The number of contained properties.
    :rtype: int
    """
    count = 0
    for obj, props in data:
        count += len(props)
    return count


def recallPoseForObject(poseData, asString=False):
    """Read the properties from the selected pose for the contained
    object and apply them.

    :param poseData: The pose data of the driver or driven object.
    :type poseData: list
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: A list with command strings for recalling the pose.
    :rtype: list(str)
    """
    transforms = ["location", "rotation_euler", "rotation_axis_angle", "scale"]
    rotations = ["rotation_quaternion", "swing"]

    lines = []

    for name, data in poseData:
        isNode = False
        propArray = False
        nameItems = name.split(":")
        # Armatures
        if len(nameItems) == 2:
            obj = bpy.data.objects[nameItems[0]].pose.bones[nameItems[1]]
            objString = 'bpy.data.objects["{}"].pose.bones["{}"]'.format(nameItems[0], nameItems[1])
        # Nodes
        elif nameItems[0].startswith("bpy"):
            isNode = True
            propArray = True if len(data) > 1 else False
            objString = nameItems[0]
        # Objects
        else:
            obj = bpy.data.objects[nameItems[0]]
            objString = 'bpy.data.objects["{}"]'.format(nameItems[0])

        propArrayIndex = 0

        for prop, value, poseValue in data:

            # Transforms
            if any(i in prop for i in transforms):
                lines.append(recallTransform(obj, objString, prop, value, asString))

            # Quaternion
            elif any(i in prop for i in rotations):
                # Before version 1.0.0 stored quaternion poses have no
                # exponential map equivalent and therefore, the
                # poseValue is None.
                if prop.startswith("swing"):
                    prop = prop.replace("swing", "rotation_quaternion")
                if poseValue is None:
                    lines.append(recallTransform(obj, objString, prop, value, asString))
                else:
                    lines.append(recallTransform(obj, objString, prop, poseValue, asString))

            # Twist
            elif prop.startswith("twist_"):
                lines.append(recallTwist(obj, objString, poseValue, asString))

            # Object property
            elif prop.startswith("rna_property:"):
                lines.append(recallProperty(obj, objString, prop, value, asString))

            # Custom property
            elif prop.startswith("property:"):
                lines.append(recallCustom(obj, objString, prop, value, asString))

                # Setting the custom property value doesn't update
                # dependent drivers in the scene properly due to the
                # lack of propagated updates in the Blender dependency
                # graph when setting the values from python.
                # The issue is known and has been reported many times
                # (i.e. T74000).
                # A suggested workaround is to force Blender to refresh
                # by setting a common property.
                if not isinstance(obj, bpy.types.PoseBone):
                    obj.hide_render = obj.hide_render

            # Shape key
            elif prop.startswith("shapeKey:"):
                lines.append(recallShapeKey(obj, objString, prop, value, asString))

            # Modifier
            elif prop.startswith("modifier:"):
                lines.append(recallModifier(obj, objString, prop, value, asString))

            # Node
            elif isNode:
                lines.append(recallNode(prop, value, objString, propArray,
                                        propArrayIndex, asString))
                if propArray:
                    propArrayIndex += 1

    return lines


def recallTransform(obj, objString, prop, value, asString):
    """Set the transform value for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param prop: The property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    # Separate the property and index.
    # Example: location[0]
    items = prop[:-1].split("[")
    # Get the current values as a list.
    values = getattr(obj, items[0])
    # Replace the current value at the stored index.
    values[int(items[1])] = value
    # Set the property.
    if not asString:
        setattr(obj, items[0], values)
    return "{}.{}[{}] = {}".format(objString,
                                   items[0],
                                   items[1],
                                   round(value, 3))


def recallTwist(obj, objString, poseValue, asString):
    """Set the rotation for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param poseValue: The rotation value to recall.
    :type poseValue: list(float)
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The list of command strings for recalling the pose.
    :rtype: list(str)
    """
    if not asString:
        setattr(obj, "rotation_quaternion", poseValue)
    lines = []
    for j in range(len(poseValue)):
        lines.append("{}.rotation_quaternion[{}] = {}".format(objString,
                                                              j,
                                                              round(poseValue[j], 3)))
    return lines


def recallProperty(obj, objString, prop, value, asString):
    """Set the object property for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param prop: The property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    prop = prop[13:]
    indexString = ""
    if "[" in prop:
        # Separate the property and index.
        # Example: color[0]
        items = prop[:-1].split("[")
        # Get the current values as a list.
        values = getattr(obj, items[0])
        # Replace the current value at the stored index.
        values[int(items[1])] = value
        # Convert a mathutils.Color instance to a float array.
        vList = []
        for i in range(3):
            vList.append(values[i])
        value = vList.copy()
        prop = items[0]
        indexString = "[{}]".format(items[1])
    if not asString:
        setattr(obj.data, prop, value)
    return "{}.data.{}{} = {}".format(objString,
                                      prop,
                                      indexString,
                                      [round(v, 3) for v in value])


def recallCustom(obj, objString, prop, value, asString):
    """Set the custom property for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param prop: The property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    prop = prop[9:]
    # Separate the property and index.
    # Example: location[0]
    items = prop[:-1].split("][")
    # Single property: ["prop"]
    if len(items) == 1:
        # Remove the remaining start bracket and quotes to use just the
        # string.
        if not asString:
            obj[items[0][2:-1]] = value
        return '{}["{}"] = {}'.format(objString,
                                      items[0][2:-1],
                                      round(value, 3))
    # Array property: ["prop"][0]
    elif len(items) == 2:
        # Remove the remaining start bracket and quotes to use just the
        # string.
        if not asString:
            obj[items[0][2:-1]][int(items[1])] = value
        return '{}["{}"][{}] = {}'.format(objString,
                                          items[0][2:-1],
                                          items[1],
                                          round(value, 3))
    return ""


def recallShapeKey(obj, objString, prop, value, asString):
    """Set the shape key for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param prop: The property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    if not asString:
        obj.data.shape_keys.key_blocks[prop[9:]].value = value
    return '{}.data.shape_keys.key_blocks["{}"].value = {}'.format(objString,
                                                                   prop[9:],
                                                                   round(value, 3))


def recallModifier(obj, objString, prop, value, asString):
    """Set the modifier for the given object.

    :param obj: The object to recall.
    :type obj: bpy.types.Object
    :param objString: The object string for the return command.
    :type objString: str
    :param prop: The modifier and property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    # Separate the property and index.
    # Example: modifier:SimpleDeform:angle
    items = prop[9:].split(":")
    if not asString:
        setattr(obj.modifiers[items[0]], str(items[1]), value)
    return '{}.modifiers["{}"].{} = {}'.format(objString,
                                               items[0],
                                               items[1],
                                               round(value, 3))


def recallNode(prop, value, objString, propArray, propArrayIndex, asString):
    """Set the property for the given node.

    :param prop: The property to recall.
    :type prop: str
    :param value: The property value to set.
    :type value: float
    :param objString: The object's string representation.
    :type objString: str
    :param propArray: True, if the property is an array.
    :type propArray: bool
    :param propArrayIndex: The index of the property.
    :type propArrayIndex: int
    :param asString: False, if the values should get applied. True, to
                     only build the command strings.
    :type asString: bool

    :return: The command string for recalling the pose.
    :rtype: str
    """
    # In case of a node the complete path to the node is passed in the
    # object part and the property is the path of the socket.
    # Example:
    # bpy.data.materials["Material"].node_tree.nodes["Mix"]
    # and
    # inputs[1].default_value

    # Separate the socket from the value.
    plugItems = prop.split(".")
    # Make the complete path to the socket and object.
    plug = eval(".".join([objString, plugItems[0]]))
    if propArray:
        if not asString:
            plug.default_value[propArrayIndex] = value
        return "{}.default_value[{}] = {}".format(".".join([objString,
                                                            plugItems[0]]),
                                                  propArrayIndex,
                                                  round(value, 3))
    else:
        if not asString:
            plug.default_value = value
        return "{}.default_value = {}".format(".".join([objString,
                                                        plugItems[0]]),
                                              round(value, 3))


class EditMode(object):
    """Storage class for the edit mode.
    """
    def __init__(self):
        self.rbfNode = None
        self.poseNode = None


editCache = EditMode()


def editPose(context, node):
    """Switch to edit mode by disabling all connected drivers of the
    driven object for adjusting properties.

    :param context: The current context.
    :type context: bpy.context
    :param node: The pose node to edit.
    :type node: bpy.types.Node

    :return: True, if the selection is valid for editing.
    :rtype: bool
    """
    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode is None:
        return False

    outNodes = nodeTree.getRBFOutputNodes(rbfNode)
    for obj in outNodes:
        for outNode in outNodes[obj]:
            outNode.enableDriver(obj, False)

    editCache.rbfNode = rbfNode
    editCache.poseNode = node

    return True


def updatePose():
    """Exit edit mode by enabling all connected drivers of the driven
    object and update the pose values.
    """
    if editCache.rbfNode is None or editCache.poseNode is None:
        editCache.rbfNode = None
        editCache.poseNode = None
        return

    outNodes = nodeTree.getRBFOutputNodes(editCache.rbfNode)
    for obj in outNodes:
        for outNode in outNodes[obj]:
            outNode.enableDriver(obj, True)

    # Get the current pose data from the object properties.
    driverData = getPoseInputData(editCache.rbfNode, editable=not editCache.rbfNode.active)
    drivenData = getPoseOutputData(editCache.rbfNode, editable=not editCache.rbfNode.active)
    # If the second tuple item is a string an error has occurred.
    # In this case the driverData is the error type and the driven
    # data is the message.
    if isinstance(drivenData, str):
        return driverData, drivenData

    # Check for valid data.
    if not driverData or not drivenData:
        return

    dev.log("Driver Data:")
    dev.log(driverData)
    dev.log("Driven Data:")
    dev.log(drivenData)

    editCache.poseNode.driverData = json.dumps(driverData)
    editCache.poseNode.drivenData = json.dumps(drivenData)

    editCache.rbfNode = None
    editCache.poseNode = None


def upgradePoseNodes(rbfNode):
    """Upgrade all pose nodes from version 0.4.0 to the current version.

    The upgrade is called when resetting the RBF upon a version mismatch
    of the RBF node or resetting the setup in general.

    The upgrade is necessary because version 0.4.0 doesn't use the
    exponential map representation of a quaternion. The new pose data
    stores both the exponential map and the quaternion values to be able
    to restore the poses with the quaternion values.

    :param rbfNode: The RBF node to evaluate.
    :type rbfNode: bpy.types.Node
    """
    # Get the pose nodes of the current solver.
    poseNodes = nodeTree.getPoseNodes(rbfNode)
    if not len(poseNodes):
        return

    for i, node in enumerate(poseNodes):
        if not utils.verifyVersion(node):
            dev.log("Upgrading pose node: {} ({})".format(node.label, node.name))

            driverData = json.loads(node.driverData)
            convertQuaternionToExponentialMap(driverData)
            node.driverData = json.dumps(driverData)

            drivenData = json.loads(node.drivenData)
            convertQuaternionToExponentialMap(drivenData)
            node.drivenData = json.dumps(drivenData)

            dev.log("Pose data set: {} ({})".format(node.label, node.name))

            utils.setVersion(node)
            dev.log("Version: {}".format(utils.getVersion(node)))


def convertQuaternionToExponentialMap(poseData):
    """Evaluate the given pose data and convert the contained quaternion
    values to an exponential map.

    :param poseData: The pose data of the driver or driven object.
    :type poseData: list
    """
    quatBlockEnd = -1

    for i in range(len(poseData)):
        name, data = poseData[i]
        for j in range(len(data)):
            # Mark the end of the quaternion block.
            if j > quatBlockEnd:
                quatBlockEnd = -1

            if data[j][0].startswith("rotation_quaternion"):
                if quatBlockEnd == -1:
                    quat = Quaternion((data[j][1], data[j+1][1], data[j+2][1], data[j+3][1]))
                    expMap = list(quat.to_exponential_map()) + [0]
                    for k, v in enumerate(expMap):
                        data[j+k][2] = data[j+k][1]
                        data[j+k][1] = v
                    # Store, where the quaternion block ends.
                    quatBlockEnd = j + 3
                # If the current index is within the quaternion block
                # skip to the next index.
                else:
                    continue


def replaceData(context, searchString="", replaceString="", driver=True):
    """Evaluate the pose data in all poses and replace the search string
    with the replace string.

    :param context: The current context.
    :type context: bpy.context
    :param searchString: The string to search for.
    :type searchString: str
    :param replaceString: The string to replace with.
    :type replaceString: str
    :param driver: True, if the driver pose data should be edited.
    :type driver: bool
    """
    if not len(searchString):
        return {'INFO'}, "No string to search for"

    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode is None:
        return {'WARNING'}, "No RBF node found in node tree"

    # Get the pose nodes of the current solver.
    poseNodes = nodeTree.getPoseNodes(rbfNode)
    if not len(poseNodes):
        return {'WARNING'}, "No pose nodes found in node tree"

    for node in poseNodes:
        if driver:
            data = node.driverData
        else:
            data = node.drivenData

        count = data.count(searchString)
        data = data.replace(searchString, replaceString)

        if driver:
            node.driverData = data
        else:
            node.drivenData = data

    return {'INFO'}, "Replaced {} occurrences in {} pose nodes".format(count, len(poseNodes))
