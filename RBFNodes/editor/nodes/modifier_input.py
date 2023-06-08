# <pep8 compliant>

import bpy

from . import common, node


class RBFModifierInputNode(node.RBFNode):
    """Object modifier input node.
    """
    bl_idname = "RBFModifierInputNode"
    bl_label = "Modifier Input"
    bl_icon = 'MODIFIER'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def setLabelCallback(self, context):
        """Callback for updating the node label based on the property
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.modifierLabelCallback(self)

    def modItems(self, context):
        """Callback for the modifier drop down menu to collect the names
        of all object modifiers of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.modifierItemsCallback(self, source=False)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all modifier properties of the selected modifier.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.modifierPropertiesCallback(self, source=False)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    modifierEnum : bpy.props.EnumProperty(name="", items=modItems, update=setLabelCallback)
    propertyEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", "Modifier")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawModifierProperties(self, layout)

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
        return common.getModifierProperties(self, obj)
