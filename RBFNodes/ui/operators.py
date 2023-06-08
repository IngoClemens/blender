# <pep8 compliant>

import bpy

from .. core import dev, rbf, nodeTree, poses


class RBFNODES_OT_CreateRBF(bpy.types.Operator):
    """Operator class for creating a new RBF node tree.
    """
    bl_idname = "rbfnodes.create_rbf"
    bl_label = "Create New RBF Setup"
    bl_description = "Create a new node tree with default nodes for a new RBF"
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
    bl_label = "Add Pose"
    bl_description = "Create a new pose for the current RBF or selected node graph"
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
    bl_label = "Link Input Node"
    bl_description = "Create a new input node from the current node graph selection"
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
    bl_label = "Link Output Node"
    bl_description = "Create a new output node from the current node graph selection"
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
    bl_label = "Recall"
    bl_description = "Set the properties of the RBF to match the selected pose"
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
    bl_label = "Activate RBF"
    bl_description = "Initialize the RBF"
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
    bl_label = "Reset RBF"
    bl_description = "Resets the RBF to it's default and removes all drivers"
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
    bl_label = "Dump Pose"
    bl_description = "Write the pose values of the selected pose node to the command line"
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
    bl_label = "Dump RBF"
    bl_description = "Write the pose weight matrix to the command line"
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
    bl_label = "Edit Driver"
    bl_description = "Search and replace pose driver data of all poses."
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
    bl_label = "Edit Driven"
    bl_description = "Search and replace pose driven data of all poses."
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
