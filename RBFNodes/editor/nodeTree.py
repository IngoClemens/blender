# <pep8 compliant>

import bpy

from .. import var


class RBFNodesNodeTree(bpy.types.NodeTree):
    """RBF Nodes"""
    bl_idname = var.NODE_TREE_TYPE
    bl_label = "RBF Nodes Editor"
    bl_icon = 'POINTCLOUD_DATA'
