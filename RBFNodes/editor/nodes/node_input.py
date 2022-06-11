# <pep8 compliant>

import bpy

from . import common, node


class RBFNodeInputNode(node.RBFNode):
    """Node tree input node.
    """
    bl_idname = "RBFNodeInputNode"
    bl_label = "Node"
    bl_icon = 'NODETREE'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    parentItems = [('MATERIAL', "Material", ""),
                   ('NODE_GROUP', "Node Group", "")]
    nodeParent : bpy.props.EnumProperty(name="", items=parentItems)
    parentName : bpy.props.StringProperty(name="Parent")
    nodeName : bpy.props.StringProperty(name="Node")
    plugName : bpy.props.StringProperty(name="Plug")
    propertyEnum : bpy.props.EnumProperty(name="",
                                          items=common.nodeItemsCallback,
                                          update=common.setPropertyPlugName)

    propertyPlugs = {}

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFNodeSocket", "Node")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawNodeProperties(self, layout)

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getProperties(self):
        """Return the name of the selected custom property.

        :return: A list with the selected custom property and the value
                 as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getNodeProperties(self)
