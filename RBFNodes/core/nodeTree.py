# <pep8 compliant>

import bpy

from . import plugs, utils
from .. import var

from operator import itemgetter


def setNodeTree(context):
    """Set the editor area to the RBF editor.

    :param context: The current context.
    :type context: bpy.context
    """
    context.area.ui_type = var.NODE_TREE_TYPE


def getNodeTree(context):
    """Return the node group of the RBF tree.

    :param context: The current context.
    :type context: bpy.context

    :return: The node group.
    :rtype: bpy.types.NodeGroup or None
    """
    tree = context.space_data.node_tree
    if tree is not None:
        return bpy.data.node_groups[tree.name]


def getSceneTrees():
    """Return all node trees of the scene which are of type
    RBFNodesNodeTree.

    :return: The list of RBF node trees.
    :rtype: RBFNodesNodeTree
    """
    trees = []
    for group in bpy.data.node_groups:
        if group.bl_idname == var.NODE_TREE_TYPE:
            trees.append(group)
    return trees


def createNodeTree(context):
    """Create a new node tree and switch the editor to it.

    :param context: The current context.
    :type context: bpy.context
    """
    bpy.ops.node.new_node_tree(type=var.NODE_TREE_TYPE, name="RBF Nodes")
    # Switch the editor to display the new node tree.
    # Because creating a new node tree only displays the new name but
    # actually doesn't update the editor.
    nodeTree = getNodeTree(context)
    context.space_data.path.append(nodeTree)
    nodeTree.use_fake_user = True


def createDefaultNodes(context):
    """Create the basic nodes for an RBF nodes setup, which includes the
    RBF node and the driver and driven object nodes.

    :param context: The current context.
    :type context: bpy.context
    """
    nodeGroup = getNodeTree(context)
    rbfNode = nodeGroup.nodes.new("RBFSolverNode")
    utils.setVersion(rbfNode)
    rbfNode.location = (0, 0)
    rbfNode.width *= 1.3

    driver = nodeGroup.nodes.new("RBFObjectInputNode")
    driver.location = var.INPUT_OBJECT_OFFSET

    nodeGroup.links.new(driver.outputs[0], rbfNode.inputs[0])

    driven = nodeGroup.nodes.new("RBFObjectOutputNode")
    driven.location = var.OUTPUT_OBJECT_OFFSET

    nodeGroup.links.new(rbfNode.outputs[0], driven.inputs[0])


def createRBF(context):
    """Create a new RBF node tree with the default nodes.

    :param context: The current context.
    :type context: bpy.context
    """
    # Switch to the RBF node tree.
    setNodeTree(context)
    # Create a new RBF tree.
    createNodeTree(context)
    # Create the default nodes.
    createDefaultNodes(context)


def getRBFNode(context):
    """Return the RBF node of the current node tree.

    Returns the selected RBF node or the one which is connected to the
    currently selected node.
    If nothing is selected, return the RBF node of the tree.
    If more than one RBF nodes exist in the tree nothing is returned.

    :param context: The current context.
    :type context: bpy.context

    :return: The RBF node.
    :rtype: bpy.types.Node or None
    """
    rbfNodes = findConnectedNode(context, "RBFSolverNode")
    if rbfNodes:
        return rbfNodes[0]
    else:
        nodeGroup = getNodeTree(context)
        if nodeGroup is not None:
            nodes = getRBFFromTree(nodeGroup)
            if len(nodes) == 1:
                return nodes[0]


def getRBFFromTree(nodeGroup):
    """Return the RBF node from the given node group.

    :param nodeGroup: The node group to query.
    :type nodeGroup: bpy.types.NodeGroup

    :return: The list of RBF nodes of the node group.
    :rtype: list(RBFSolverNode)
    """
    nodes = []
    for node in nodeGroup.nodes:
        if node.bl_idname == "RBFSolverNode":
            nodes.append(node)
    return nodes


def findConnectedNode(context, nodeId):
    """Find the nodes of the given node id by traversing the graph of
    the currently selected node.

    :param context: The current context.
    :type context: bpy.context
    :param nodeId: The bl_idname string of the node to search for.
    :type nodeId: str

    :return: A list with the found RBF nodes.
    :rtype: list
    """
    node = context.active_node
    if not node:
        return

    if node.bl_idname == nodeId:
        return [node]

    nodes = []

    for plug in node.inputs:
        nodes.extend(plugs.getInputNodes(plug,
                                         "RBFSolverNode",
                                         allNodes=True))
    for plug in node.outputs:
        nodes.extend(plugs.getOutputNodes(plug,
                                          "RBFSolverNode",
                                          allNodes=True))

    if len(nodes):
        return nodes


def getPoseNodes(rbfNode):
    """Return all pose nodes connected to the RBF node.

    The returned list is sorted by pose index.

    :param rbfNode: The RBF node of the current node tree.
    :type rbfNode: bpy.types.Node

    :return: The list of connected pose nodes.
    :rtype: list(bpy.types.Nodes)
    """
    nodes = plugs.getInputNodes(rbfNode.inputs[2], "RBFPoseNode")

    # To sort the poses by index create a list of tuples with the index
    # and the node.
    temp = []
    for node in nodes:
        temp.append((node.poseIndex, node))
    # Sort the tuples and create a new list.
    temp.sort(key=itemgetter(0))

    nodes = []
    for item in temp:
        nodes.append(item[1])

    return nodes


def sourceNodePosition(lastNode=None, referenceNode=None, offset1=(0, 0), offset2=(0, 0),
                       useHeight=False, left=True):
    """Return the position of a new input node depening on whether it's
    the first or an additional node.

    :param lastNode: The last node which defines the postion of a new
                     node. None, if the position for the first node
                     should be returned.
    :type lastNode: bpy.types.Node
    :param referenceNode: The target node the new node gets connected to.
                          This node defines the initial position for the
                          first connected node.
    :type referenceNode: bpy.types.Node
    :param offset1: The offset position for the first node.
    :type offset1: tuple(int, int)
    :param offset2: The offset position for a subsequent node.
    :type offset2: tuple(int, int)
    :param useHeight: True, if the height of the previous node should be
                      respected.
    :type useHeight: bool
    :param left: True, if the offset should be to the left.
    :type left: bool

    :return: The node position as a tuple of floats.
    :rtype: tuple(float, float) or None
    """
    side = 1
    if not left:
        side = -1

    if referenceNode:
        # For the first node get an offset position based on the
        # destination node.
        if not lastNode:
            x, y = referenceNode.location
            ox, oy = offset1
            return x + (ox * side), y + oy
        # For any additional node get an offset position based on the
        # last node.
        else:
            x, y = lastNode.location
            ox, oy = offset2
            if useHeight:
                oy = oy * 2 - lastNode.height
            return x + (ox * side), y + oy


def createInputNode(context):
    """Create a new input node from the current node graph selection.

    :param context: The current context.
    :type context: bpy.context
    """
    nodeItems = getSelectedShadingNode()
    if not nodeItems:
        return

    # Create the node and link it.
    nodeGroup = getNodeTree(context)
    node = nodeGroup.nodes.new("RBFNodeInputNode")
    node.nodeParent = nodeItems[0]
    node.parentName = nodeItems[1]
    node.nodeName = nodeItems[2]

    # Position the new node and connect it.
    rbfNode = getRBFNode(context)
    if rbfNode:
        inputNodes = plugs.getInputNodes(rbfNode.inputs[1], "RBFNodeInputNode")
        pos = sourceNodePosition(lastNode=None if not len(inputNodes) else inputNodes[-1],
                                 referenceNode=rbfNode,
                                 offset1=var.FIRST_NODE_OFFSET,
                                 offset2=var.NODE_OFFSET,
                                 useHeight=True)
        # Connect the node.
        nodeGroup.links.new(node.outputs[0], rbfNode.inputs[1])
        if pos:
            node.location = pos


def createOutputNode(context):
    """Create a new output node from the current node graph selection.

    :param context: The current context.
    :type context: bpy.context
    """
    nodeItems = getSelectedShadingNode()
    if not nodeItems:
        return

    # Create the node and link it.
    nodeGroup = getNodeTree(context)
    node = nodeGroup.nodes.new("RBFNodeOutputNode")
    node.nodeParent = nodeItems[0]
    node.parentName = nodeItems[1]
    node.nodeName = nodeItems[2]

    # Position the new node and connect it.
    rbfNode = getRBFNode(context)
    if rbfNode:
        outputNodes = plugs.getOutputNodes(rbfNode.outputs[1], "RBFNodeOutputNode")
        pos = sourceNodePosition(lastNode=None if not len(outputNodes) else outputNodes[-1],
                                 referenceNode=rbfNode,
                                 offset1=var.FIRST_NODE_OFFSET,
                                 offset2=var.NODE_OFFSET,
                                 useHeight=True,
                                 left=False)
        # Connect the node.
        nodeGroup.links.new(rbfNode.outputs[1], node.inputs[0])
        if pos:
            node.location = pos


def getSelectedShadingNode():
    """Return the path string to the selected node in the node editor.

    :return: A tuple with the node parent type, the parent name and node
             name.
    :rtype: tuple(str, str, str) or None
    """
    nodeSpace = getNodeEditor()
    if not nodeSpace or not hasNodes(nodeSpace):
        return

    for node in nodeSpace.edit_tree.nodes:
        if node.select:
            parent = node.id_data.name
            material = getMaterial(parent)
            if material:
                return 'MATERIAL', material.name, node.name
            else:
                group = getNodeGroup(parent)
                if group:
                    return 'NODE_GROUP', group.name, node.name


def getNodeEditor():
    """Return the currently open shader or geometry node editor space.

    :return: The editor space.
    :rtype: bpy.types.Space or None
    """
    for area in bpy.context.screen.areas:
        if area.type == 'NODE_EDITOR' and area.ui_type in ("ShaderNodeTree", "GeometryNodeTree"):
            for space in area.spaces:
                if space.type == 'NODE_EDITOR':
                    return space


def hasNodes(space):
    """Return True, if the node tree in the given space contains nodes.

    :param space: The shader editor space.
    :type space: bpy.types.Space or None

    :return: True, if the contained node tree contains nodes.
    :rtype: bool
    """
    if space.edit_tree:
        if space.edit_tree.nodes:
            return True
    return False


def getMaterial(name):
    """Return the material of the node tree which matches the given
    name.

    :param name: The name of the data block.
    :type name: str

    :return: The matching material.
    :rtype: bpy.type.Material or None
    """
    obj = bpy.context.active_object
    if obj:
        index = obj.active_material_index
        mat = obj.material_slots[index].material
        if mat and mat.node_tree and mat.node_tree.name == name:
            return mat


def getNodeGroup(name):
    """Return the node group which matches the given name

    :param name: The name of the data block.
    :type name: str

    :return: The node group with the given name.
    :rtype: bpy.types.NodeGroup or None
    """
    for group in bpy.data.node_groups:
        if group.name == name:
            return group


def getRBFOutputNodes(rbfNode):
    """Return a list of all connected output nodes of all output objects
    of the given RBF node.

    :param rbfNode: The RBF node to get the outputs from.
    :type rbfNode: bpy.types.Node

    :return: A dictionary with the driven objects as the key and a list
             of property output nodes.
    :rtype: dict
    """
    # Process each connected object output node.
    outList = []
    for node in plugs.getOutputNodes(rbfNode.outputs[0], "RBFObjectOutputNode"):
        obj = node.getObject()
        # First get all object output nodes and their objects. If one
        # isn't defined there's no need to process it.
        if obj:
            outList.append((node, obj))

    # Collect all connected output property nodes.
    rbfOutput = {}

    for node, obj in outList:
        outNodes = []
        for socket in node.outputs:
            outNodes.extend(plugs.getOutputNodes(socket))
        rbfOutput[obj] = outNodes

    # Collect the node output nodes.
    outNodes = []
    for node in plugs.getOutputNodes(rbfNode.outputs[1], "RBFNodeOutputNode"):
        data = node.getProperties()
        if data:
            outNodes.append(node)
    if len(outNodes):
        rbfOutput["NodeOutput"] = outNodes

    return rbfOutput


def setInputNodesEditable(rbfNode, state=True):
    """Set the editable state of the input nodes of the given RBF node.

    :param rbfNode: The RBF node to get the input nodes from.
    :type rbfNode: bpy.types.Node
    :param state: True, if the nodes should be editable.
    :type state: bool
    """
    nodeTypes = ["RBFObjectInputNode", "RBFNodeInputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getInputNodes(rbfNode.inputs[i], nodeId=nodeType):
            node.editable = state
            if node.bl_idname == "RBFObjectInputNode":
                for socket in node.inputs:
                    for inNode in plugs.getInputNodes(socket):
                        inNode.editable = state


def setOutputNodesEditable(rbfNode, state=True):
    """Set the editable state of the output nodes of the given RBF node.

    :param rbfNode: The RBF node to get the output nodes from.
    :type rbfNode: bpy.types.Node
    :param state: True, if the nodes should be editable.
    :type state: bool
    """
    nodeTypes = ["RBFObjectOutputNode", "RBFNodeOutputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getOutputNodes(rbfNode.outputs[i], nodeId=nodeType):
            node.editable = state
            if node.bl_idname == "RBFObjectOutputNode":
                for socket in node.outputs:
                    for outNode in plugs.getOutputNodes(socket):
                        outNode.editable = state
