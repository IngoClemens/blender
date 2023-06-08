# <pep8 compliant>

import bpy

from . import common, node
from ... core import poses


class RBFObjectInputNode(node.RBFNode):
    """Driver object input node.
    """
    bl_idname = "RBFObjectInputNode"
    bl_label = "Object Input"
    bl_icon = 'OBJECT_DATA'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    sceneObject : bpy.props.PointerProperty(type=bpy.types.Object)
    bone : bpy.props.StringProperty()

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFObjectSocket", "Object")
        self.addInput("RBFPropertySocket", "Properties", link_limit=0)

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawObjectProperties(self, context, layout)

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getObject(self):
        """Return the selected object of the node.

        :return: The currently selected object.
        :rtype: bpy.types.Object
        """
        return common.getObjectFromNode(self)
