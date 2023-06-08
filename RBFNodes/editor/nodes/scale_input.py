# <pep8 compliant>

import bpy

from . import common, node


class RBFScaleInputNode(node.RBFNode):
    """Object scale input node.
    """
    bl_idname = "RBFScaleInputNode"
    bl_label = "Scale Input"
    bl_icon = 'FIXED_SIZE'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    x_axis : bpy.props.BoolProperty(name="X", default=False)
    y_axis : bpy.props.BoolProperty(name="Y", default=False)
    z_axis : bpy.props.BoolProperty(name="Z", default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", "Scale")
        
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
