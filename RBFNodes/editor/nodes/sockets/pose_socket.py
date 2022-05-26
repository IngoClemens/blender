# <pep8 compliant>

import bpy

from . socket import RBFSocket
from .... import var


class RBFPoseSocket(bpy.types.NodeSocket, RBFSocket):
    """RBF pose socket"""
    bl_idname = "RBFPoseSocket"
    bl_label = "RBF Pose Socket"

    color = var.COLOR_CYAN

    def draw(self, context, layout, node, text):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        :param node: The node the socket belongs to.
        :type node: bpy.types.Node
        :param text: The text label to draw alongside properties.
        :type text: str
        """
        layout.label(text=text)
