# <pep8 compliant>

import bpy

from . import nodeTree, poses

import json


def dumpPose(context):
    """Write the pose data of the current node to the command line.

    :param context: The current context.
    :type context: bpy.context
    """
    node = context.active_node
    if node and node.bl_idname == "RBFPoseNode":
        print("Pose: {}".format(node.name))
        print("Driver:")
        lines = poses.recallPoseForObject(json.loads(node.driverData), False)
        print("\n".join(lines))
        print("Driven:")
        lines = poses.recallPoseForObject(json.loads(node.drivenData), False)
        print("\n".join(lines))


def dumpRBF(context):
    """Write the pose weight matrix to the command line.

    :param context: The current context.
    :type context: bpy.context
    """
    rbfNode = nodeTree.getRBFNode(context)
    print(rbfNode.getWeightMatrix())
