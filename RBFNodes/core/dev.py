# <pep8 compliant>

import bpy

from . import nodeTree, poses
from .. import dev

import json


def dumpPose(context):
    """Write the pose data of the current node to the command line.

    :param context: The current context.
    :type context: bpy.context
    """
    node = context.active_node
    if node and node.bl_idname == "RBFPoseNode":
        dev.log("# Pose: {}".format(node.name))
        dev.log("# Driver:")
        lines = poses.recallPoseForObject(json.loads(node.driverData), True)
        dev.log("\n".join(lines))
        dev.log("# Driven:")
        lines = poses.recallPoseForObject(json.loads(node.drivenData), True)
        dev.log("\n".join(lines))


def dumpRBF(context):
    """Write the pose weight matrix to the command line.

    :param context: The current context.
    :type context: bpy.context
    """
    rbfNode = nodeTree.getRBFNode(context)
    dev.log(rbfNode.getWeightMatrix())
