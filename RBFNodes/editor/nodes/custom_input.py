# <pep8 compliant>

import bpy

from . import common, node


class RBFCustomInputNode(node.RBFNode):
    """Custom property input node.
    """
    bl_idname = "RBFCustomInputNode"
    bl_label = "Custom Input"
    bl_icon = 'EMPTY_SINGLE_ARROW'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def setLabelCallback(self, context):
        """Callback for updating the node label based on the property
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.customLabelCallback(self)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all custom properties of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.customItemsCallback(self, source=False)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    modeItems = [('LIST', "Auto", ""),
                 ('MANUAL', "Manual", "")]
    mode : bpy.props.EnumProperty(items=modeItems)
    propertyName : bpy.props.StringProperty(name="", update=setLabelCallback)
    propertyEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", "Custom")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawCustomProperties(self, layout)

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

    def getProperties(self, obj):
        """Return the name of the selected custom property.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected custom property and the value
                 as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getCustomProperties(self, obj)
