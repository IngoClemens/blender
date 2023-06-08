# <pep8 compliant>

import bpy

from . import common, node
from ... import var


class RBFRotationInputNode(node.RBFNode):
    """Object rotation input node.
    """
    bl_idname = "RBFRotationInputNode"
    bl_label = "Rotation Input"
    bl_icon = 'ORIENTATION_GIMBAL'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    w_axis : bpy.props.BoolProperty(name="W", default=False)
    x_axis : bpy.props.BoolProperty(name="X", default=False)
    y_axis : bpy.props.BoolProperty(name="Y", default=False)
    z_axis : bpy.props.BoolProperty(name="Z", default=False)

    rotationMode : bpy.props.EnumProperty(name="", items=var.ROTATION_MODE, default='EULER')

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", "Rotation")
        
    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawRotationProperties(self, layout)

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
        """Return the selected rotation properties for the given object.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected rotation properties and their
                 values as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getRotationProperties(self, obj)
