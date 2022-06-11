# <pep8 compliant>

import bpy


def getInputNodes(socket, nodeId="", allNodes=False):
    """Find and return all nodes of the given bl_idname which are
    connected to the given input socket.

    :param socket: The input socket to query.
    :type socket: bpy.types.NodeSocket
    :param nodeId: The bl_idname string of the node to search for.
                   If passed an empty string all nodes will be returned.
    :type nodeId: str
    :param allNodes: Evaluate all inputs.
    :type allNodes: bool

    :return: A list with all nodes connected to the input.
    :rtype: list(bpy.types.Node)
    """
    nodes = []
    for link in socket.links:
        srcNode = link.from_node
        # First check for reroutes.
        if isinstance(srcNode, bpy.types.NodeReroute):
            nodes.extend(getInputNodes(srcNode.inputs[0],
                                       nodeId=nodeId))
        elif srcNode.bl_idname == nodeId or nodeId == "":
            if not isinstance(srcNode, bpy.types.NodeReroute):
                nodes.append(srcNode)
        elif allNodes:
            for plug in srcNode.inputs:
                nodes.extend(getInputNodes(plug,
                                           nodeId=nodeId,
                                           allNodes=allNodes))
    return nodes


def getOutputNodes(socket, nodeId="", allNodes=False):
    """Find and return all nodes of the given bl_idname which are
    connected to the given output socket.

    :param socket: The output socket to query.
    :type socket: bpy.types.NodeSocket
    :param nodeId: The bl_idname string of the node to search for.
    :type nodeId: str
    :param allNodes: Evaluate all inputs.
    :type allNodes: bool

    :return: A list with all nodes connected to the output.
    :rtype: list(bpy.types.Node)
    """
    nodes = []
    for link in socket.links:
        dstNode = link.to_node
        # First check for reroutes.
        if isinstance(dstNode, bpy.types.NodeReroute):
            nodes.extend(getOutputNodes(dstNode.outputs[0],
                                        nodeId=nodeId))
        elif dstNode.bl_idname == nodeId or nodeId == "":
            if not isinstance(dstNode, bpy.types.NodeReroute):
                nodes.append(dstNode)
        elif allNodes:
            for plug in dstNode.outputs:
                nodes.extend(getOutputNodes(plug,
                                            nodeId=nodeId,
                                            allNodes=allNodes))
    return nodes


def getObjectFromSocket(socket, source=True):
    """Return the object from the object node connected to the given
    socket.

    :param socket: The output socket to get the object node from.
    :type socket: bpy.types.NodeSocket
    :param source: True, if the object can be found on the source node.
    :type source: bool

    :return: The object of the connected object node.
    :rtype: bpy.types.Object or None
    """
    if source:
        nodes = getInputNodes(socket, "RBFObjectOutputNode")
    else:
        nodes = getOutputNodes(socket, "RBFObjectInputNode")
    if len(nodes):
        return nodes[0].getObject()
