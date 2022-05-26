# <pep8 compliant>

import bpy

from . import preferences
from .. import var


# ----------------------------------------------------------------------
# Panel
# ----------------------------------------------------------------------

class RBFNODES_PT_RBF(bpy.types.Panel):

    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RBF Nodes"
    bl_label = "RBF"

    @classmethod
    def poll(cls, context):
        """Only draw the panel when the RBF editor is active.

        :param context: The current context.
        :type context: bpy.context
        """
        return context.space_data.tree_type == var.NODE_TREE_TYPE

    def draw(self, context):
        """Draw the panel.

        :param context: The current context.
        :type context: bpy.context
        """
        box = self.layout.box()
        box.label(text="Create")
        col = box.column(align=True)
        col.operator("rbfnodes.create_rbf")
        col.separator(factor=1.5)
        col.operator("rbfnodes.create_pose")
        col.separator(factor=1.5)
        col.operator("rbfnodes.create_node_input")
        col.operator("rbfnodes.create_node_output")
        col.separator(factor=1.5)

        box = self.layout.box()
        box.label(text="Activation")
        col = box.column(align=True)
        col.operator("rbfnodes.activate_rbf")
        col.separator(factor=1.5)
        col.operator("rbfnodes.reset_rbf")
        col.separator(factor=1.5)

        if preferences.getPreferences().developerMode:
            box = self.layout.box()
            box.label(text="Developer")
            col = box.column(align=True)
            col.operator("rbfnodes.dump_pose")
            col.operator("rbfnodes.dump_rbf")
