# <pep8 compliant>

import bpy

from .... import var


class RBFSocket:
    """Basic socket class"""
    color : var.COLOR_GREY
    name : bpy.props.StringProperty()
    value : None

    @classmethod
    def draw_color_simple(cls):
        """Return the color of the socket.

        :param context: The current context.
        :type context: bpy.context
        :param node: The node the socket belongs to.
        :type node: bpy.types.Node

        :return: The socket color.
        :rtype: list(float, float, float, float)
        """
        return cls.color


class RBFSocket_legacy3:
    """Basic socket class"""
    color : var.COLOR_GREY
    name : bpy.props.StringProperty()
    value : None

    def draw_color(self, context, node):
        """Return the color of the socket.

        :param context: The current context.
        :type context: bpy.context
        :param node: The node the socket belongs to.
        :type node: bpy.types.Node

        :return: The socket color.
        :rtype: list(float, float, float, float)
        """
        return self.color
