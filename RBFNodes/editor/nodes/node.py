# <pep8 compliant>

import bpy

from ... import var


class RBFNode(bpy.types.Node):
    """Class, which all driver tree nodes inherit from.
    """
    bl_width_default = 155

    @classmethod
    def poll(cls, nodeTree):
        """Make the node only visible to the RBF node tree.

        :param nodeTree: The current node tree.
        :type nodeTree: bpy.types.NodeTree

        :return: True, if the node tree is related to the node.
        :rtype: bool
        """
        return nodeTree.bl_idname == var.NODE_TREE_TYPE

    def addInput(self, socketType, name, **kwargs):
        """Add a new input socket to the node.

        :param socketType: The type of socket to add.
        :type socketType: class
        :param name: The name of the socket.
        :type name: str
        :param kwargs: Optional keyword arguments
        :type kwargs: div

        :return: The created socket object.
        :rtype: bpy.types.NodeSocket
        """
        socket = self.inputs.new(socketType, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)
        return socket

    def addOutput(self, socketType, name, **kwargs):
        """Add a new output socket to the node.

        :param socketType: The type of socket to add.
        :type socketType: class
        :param name: The name of the socket.
        :type name: str
        :param kwargs: Optional keyword arguments
        :type kwargs: div

        :return: The created socket object.
        :rtype: bpy.types.NodeSocket
        """
        socket = self.outputs.new(socketType, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)
        return socket

    def draw_buttons(self, context, layout):
        """Draw node buttons.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    def draw(self, context, layout):
        """Draw node buttons.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        layout.use_property_decorate = False
