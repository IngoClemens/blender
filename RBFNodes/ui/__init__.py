# <pep8 compliant>

import bpy

from . import operators, panel, preferences


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [preferences.RBFNODESPreferences,
           operators.RBFNODES_OT_CreateRBF,
           operators.RBFNODES_OT_CreatePose,
           operators.RBFNODES_OT_CreateNodeInput,
           operators.RBFNODES_OT_CreateNodeOutput,
           operators.RBFNODES_OT_RecallPose,
           operators.RBFNODES_OT_ActivateRBF,
           operators.RBFNODES_OT_ResetRBF,
           operators.RBFNODES_OT_DumpPose,
           operators.RBFNODES_OT_DumpRBF,
           panel.RBFNODES_PT_RBF]

# Excluded:
# operators.RBF_Nodes_Properties


def register():
    """Register the panel and operators.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Scene.rbf_nodes = bpy.props.PointerProperty(type=operators.RBF_Nodes_Properties)


def unregister():
    """Unregister the panel and operators.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.rbf_nodes
