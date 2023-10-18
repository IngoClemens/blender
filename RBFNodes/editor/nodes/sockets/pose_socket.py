# <pep8 compliant>

import bpy

if bpy.app.version < (4, 0, 0):
    from . socket import RBFSocket_legacy3 as RBFSocket
else:
    from . socket import RBFSocket

from .... import language, var


# Get the current language.
strings = language.getLanguage()


class RBFPoseSocket(bpy.types.NodeSocket, RBFSocket):
    """RBF pose socket"""
    bl_idname = "RBFPoseSocket"
    bl_label = strings.POSE_SOCKET_LABEL

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
