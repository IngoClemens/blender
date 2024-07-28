# <pep8 compliant>

import bpy

from . import common, node
from ... import language


# Get the current language.
strings = language.getLanguage()


class RBFRotationInputNode(node.RBFNode):
    """Object rotation input node.
    """
    bl_idname = "RBFRotationInputNode"
    bl_label = strings.ROTATION_INPUT_LABEL
    bl_icon = 'ORIENTATION_GIMBAL'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    w_axis : bpy.props.BoolProperty(name=strings.W_LABEL, default=False)
    x_axis : bpy.props.BoolProperty(name=strings.X_LABEL, default=False)
    y_axis : bpy.props.BoolProperty(name=strings.Y_LABEL, default=False)
    z_axis : bpy.props.BoolProperty(name=strings.Z_LABEL, default=False)

    rotationMode : bpy.props.EnumProperty(name="", items=common.ROTATION_MODE, default='EULER')
    
    include_external_rotations : bpy.props.BoolProperty(name=strings.INCLUDE_EXTERNAL_ROTATIONS_LABEL,
                                             default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFPropertySocket", strings.ROTATION_LABEL)
        
    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawRotationProperties(self, layout)
        layout.prop(self, "include_external_rotations")

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
