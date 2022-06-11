# <pep8 compliant>

import bpy
import bpy.utils.previews

from . import operators, panel, preferences
# from . icons import toolIcons


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


def register():
    """Register the panel and operators.
    """
    # toolIcons.create()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the panel and operators.
    """
    # toolIcons.delete()

    for cls in classes:
        bpy.utils.unregister_class(cls)
