# <pep8 compliant>

import bpy

from .. import language
from .. core import dev, rbf, nodeTree, poses


# Get the current language.
strings = language.getLanguage()


class RBFNODES_OT_CreateRBF(bpy.types.Operator):
    """Operator class for creating a new RBF node tree.
    """
    bl_idname = "rbfnodes.create_rbf"
    bl_label = strings.CREATE_RBF_LABEL
    bl_description = strings.ANN_CREATE_RBF
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        nodeTree.createRBF(context)
        return {'FINISHED'}


class RBFNODES_OT_CreatePose(bpy.types.Operator):
    """Operator class for creating a new pose.
    """
    bl_idname = "rbfnodes.create_pose"
    bl_label = strings.ADD_POSE_LABEL
    bl_description = strings.ANN_ADD_POSE
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = poses.createPose(context)
        if result:
            self.report(result[0], result[1])

        return {'FINISHED'}


class RBFNODES_OT_CreateNodeInput(bpy.types.Operator):
    """Operator class for creating a new input node from a node graph
    selection.
    """
    bl_idname = "rbfnodes.create_node_input"
    bl_label = strings.CREATE_NODE_INPUT_LABEL
    bl_description = strings.ANN_CREATE_NODE_INPUT
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        nodeTree.createInputNode(context)

        return {'FINISHED'}


class RBFNODES_OT_CreateNodeOutput(bpy.types.Operator):
    """Operator class for creating a new output node from a node graph
    selection.
    """
    bl_idname = "rbfnodes.create_node_output"
    bl_label = strings.CREATE_NODE_OUTPUT_LABEL
    bl_description = strings.ANN_CREATE_NODE_OUTPUT
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        nodeTree.createOutputNode(context)

        return {'FINISHED'}


class RBFNODES_OT_RecallPose(bpy.types.Operator):
    """Operator class for recalling a pose.
    """
    bl_idname = "rbfnodes.recall_pose"
    bl_label = strings.RECALL_POSE_LABEL
    bl_description = strings.ANN_RECALL_POSE
    bl_options = {'REGISTER', 'UNDO'}

    nodeName : bpy.props.StringProperty()

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = poses.recallPose(context, self.nodeName)
        if result:
            self.report(result[0], result[1])

        return {'FINISHED'}


class RBFNODES_OT_ActivateRBF(bpy.types.Operator):
    """Operator class for activating the RBF solver.
    """
    bl_idname = "rbfnodes.activate_rbf"
    bl_label = strings.ACTIVATE_RBF_LABEL
    bl_description = strings.ANN_ACTIVATE_RBF
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = rbf.initialize(context)
        if result:
            self.report(result[0], result[1])

        return {'FINISHED'}


class RBFNODES_OT_ResetRBF(bpy.types.Operator):
    """Operator class for resetting the RBF solver.
    """
    bl_idname = "rbfnodes.reset_rbf"
    bl_label = strings.RESET_RBF_LABEL
    bl_description = strings.ANN_RESET_RBF
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        result = rbf.reset(context)
        if result:
            self.report(result[0], result[1])

        return {'FINISHED'}


class RBFNODES_OT_DumpPose(bpy.types.Operator):
    """Operator class for printing the pose data to the command line.
    """
    bl_idname = "rbfnodes.dump_pose"
    bl_label = strings.DUMP_POSE_LABEL
    bl_description = strings.ANN_DUMP_POSE
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        dev.dumpPose(context)
        return {'FINISHED'}


class RBFNODES_OT_DumpRBF(bpy.types.Operator):
    """Operator class for printing the pose weight matrix to the command
    line.
    """
    bl_idname = "rbfnodes.dump_rbf"
    bl_label = strings.DUMP_RBF_LABEL
    bl_description = strings.ANN_DUMP_RBF
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        dev.dumpRBF(context)
        return {'FINISHED'}


class RBFNODES_OT_SearchReplacePoseDriverData(bpy.types.Operator):
    """Operator class for editing pose driver data via search and
    replace.
    """
    bl_idname = "rbfnodes.search_replace_pose_driver_data"
    bl_label = strings.EDIT_DRIVER_LABEL
    bl_description = strings.ANN_EDIT_DRIVER
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        props = context.window_manager.rbf_nodes

        result = poses.replaceData(context=context,
                                   searchString=props.search_value,
                                   replaceString=props.replace_value,
                                   driver=True)
        self.report(result[0], result[1])
        return {'FINISHED'}


class RBFNODES_OT_SearchReplacePoseDrivenData(bpy.types.Operator):
    """Operator class for editing pose driven data via search and
    replace.
    """
    bl_idname = "rbfnodes.search_replace_pose_driven_data"
    bl_label = strings.EDIT_DRIVEN_LABEL
    bl_description = strings.ANN_EDIT_DRIVEN
    bl_options = {'REGISTER', 'UNDO'}

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        props = context.window_manager.rbf_nodes

        result = poses.replaceData(context=context,
                                   searchString=props.search_value,
                                   replaceString=props.replace_value,
                                   driver=False)
        self.report(result[0], result[1])
        return {'FINISHED'}
