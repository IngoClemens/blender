# <pep8 compliant>

import bpy

from . import common, node
from ... import language
from ... core import poses


# Get the current language.
strings = language.getLanguage()


class RBFObjectInputNode(node.RBFNode):
    """Driver object input node.
    """
    bl_idname = "RBFObjectInputNode"
    bl_label = strings.OBJECT_INPUT_LABEL
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
        self.addOutput("RBFObjectSocket", strings.OBJECT_LABEL)
        self.addInput("RBFPropertySocket", strings.PROPERTIES_LABEL, link_limit=0)

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
