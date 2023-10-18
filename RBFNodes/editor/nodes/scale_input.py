# <pep8 compliant>

import bpy

from . import common, node
from ... import language


# Get the current language.
strings = language.getLanguage()


class RBFScaleInputNode(node.RBFNode):
    """Object scale input node.
    """
    bl_idname = "RBFScaleInputNode"
    bl_label = strings.SCALE_INPUT_LABEL
    bl_icon = 'FIXED_SIZE'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    x_axis : bpy.props.BoolProperty(name=strings.X_LABEL, default=False)
    y_axis : bpy.props.BoolProperty(name=strings.Y_LABEL, default=False)
    z_axis : bpy.props.BoolProperty(name=strings.Z_LABEL, default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", strings.SCALE_LABEL)
        
    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawTransformProperties(self, layout)

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
        """Return the selected scale properties for the given object.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected scale properties and their
                 values as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getScaleProperties(self, obj)
