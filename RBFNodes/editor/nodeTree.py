# <pep8 compliant>

import bpy

from .. import var
from .. import language


# Get the current language.
strings = language.getLanguage()


class RBFNodesNodeTree(bpy.types.NodeTree):
    """RBF Nodes"""
    bl_idname = var.NODE_TREE_TYPE
    bl_label = strings.EDITOR_LABEL
    bl_icon = 'POINTCLOUD_DATA'
