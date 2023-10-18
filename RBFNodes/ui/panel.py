# <pep8 compliant>

import bpy

from .. import language, preferences, var
from .. core import nodeTree, utils

'''
# Custom icons:
from . icons import toolIcons
icon_value=toolIcons.getIcon("tool_icon").icon_id
'''


# Get the current language.
strings = language.getLanguage()


# ----------------------------------------------------------------------
# Panel
# ----------------------------------------------------------------------

class RBF_Nodes_Properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    search_value : bpy.props.StringProperty(name=strings.SEARCH_LABEL)
    replace_value : bpy.props.StringProperty(name=strings.REPLACE_LABEL)


class RBFNODES_PT_RBF(bpy.types.Panel):

    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = strings.CATEGORY_LABEL
    bl_label = strings.RBF_LABEL

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
        rbfNodesProps = context.window_manager.rbf_nodes

        node = nodeTree.getRBFNode(context)
        if node is None or utils.verifyVersion(node):
            box = self.layout.box()
            box.label(text=strings.CREATE_LABEL)
            col = box.column(align=True)
            col.operator("rbfnodes.create_rbf", icon='FILE_NEW')
            col.separator(factor=1.5)
            col.operator("rbfnodes.create_pose", icon='POSE_HLT')
            col.separator(factor=1.5)
            col.operator("rbfnodes.create_node_input", icon='IMPORT')
            col.operator("rbfnodes.create_node_output", icon='EXPORT')

            box = self.layout.box()
            box.label(text=strings.ACTIVATION_LABEL)
            col = box.column(align=True)
            col.operator("rbfnodes.activate_rbf", icon='QUIT')
            col.separator(factor=1.5)
            col.operator("rbfnodes.reset_rbf", icon='CANCEL')

            if preferences.getPreferences().developerMode:
                box = self.layout.box()
                box.label(text=strings.DEVELOPER_LABEL_SHORT)
                col = box.column(align=True)
                col.operator("rbfnodes.dump_pose")
                col.operator("rbfnodes.dump_rbf")
                # col.separator(factor=1.5)
                box = self.layout.box()
                box.label(text=strings.EDIT_POSE_DATA_LABEL)
                col = box.column(align=True)
                col.prop(rbfNodesProps, "search_value")
                col.prop(rbfNodesProps, "replace_value")
                col.operator("rbfnodes.search_replace_pose_driver_data")
                col.operator("rbfnodes.search_replace_pose_driven_data")
        else:
            box = self.layout.box()
            box.label(text=strings.ACTIVATION_LABEL)
            col = box.column(align=True)
            col.label(text=strings.INFO_VERSION_MISMATCH)
            col.label(text=strings.INFO_RESET_TO_UPDATE)
            col.separator(factor=1.5)
            col.operator("rbfnodes.reset_rbf", icon='CANCEL')
