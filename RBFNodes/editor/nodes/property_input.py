# <pep8 compliant>

import bpy

from . import common, node
from ... import language


# Get the current language.
strings = language.getLanguage()


class RBFPropertyInputNode(node.RBFNode):
    """Object property input node.
    """
    bl_idname = "RBFPropertyInputNode"
    bl_label = strings.PROPERTY_INPUT_LABEL
    bl_icon = 'PROPERTIES'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def setLabelCallback(self, context):
        """Callback for updating the node label based on the property
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.propertyLabelCallback(self)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all object properties of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.propertyItemsCallback(self, source=False)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    propertyEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", strings.PROPERTY_LABEL)

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawPropertyProperties(self, layout)

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
        return common.getObjectProperties(self, obj)
