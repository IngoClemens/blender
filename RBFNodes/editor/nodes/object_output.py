# <pep8 compliant>

import bpy

from . import common, node


class RBFObjectOutputNode(node.RBFNode):
    """Driver object output node.
    """
    bl_idname = "RBFObjectOutputNode"
    bl_label = "Object Output"
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
        self.addOutput("RBFPropertySocket", "Properties", link_limit=0)
        self.addInput("RBFObjectSocket", "Object")

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
