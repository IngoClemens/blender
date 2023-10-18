# <pep8 compliant>

import bpy

from . import common, node
from ... import language


# Get the current language.
strings = language.getLanguage()


class RBFShapeKeyInputNode(node.RBFNode):
    """Shape key input node.
    """
    bl_idname = "RBFShapeKeyInputNode"
    bl_label = strings.SHAPE_KEY_INPUT_LABEL
    bl_icon = 'SHAPEKEY_DATA'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def setLabelCallback(self, context):
        """Callback for updating the node label based on the shape key
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.shapeKeyLabelCallback(self)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all shape keys of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.shapeKeyItemsCallback(self, source=False)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    modeItems = [('LIST', strings.AUTO_LABEL, ""),
                 ('MANUAL', strings.MANUAL_LABEL, "")]
    mode : bpy.props.EnumProperty(items=modeItems)
    shapeName : bpy.props.StringProperty(name="", update=setLabelCallback)
    shapeNameEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", strings.SHAPE_KEY_LABEL)

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawShapeKeyProperties(self, layout)

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
        """Return the name of the selected shape key.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: The selected shape key name and the value as a tuple.
        :rtype: tuple(str, float)
        """
        return common.getShapeKeyProperties(self, obj)
