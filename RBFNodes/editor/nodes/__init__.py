# <pep8 compliant>

import bpy

from . object_input import RBFObjectInputNode
from . object_output import RBFObjectOutputNode
from . pose import RBFPoseNode
from . property_input import RBFPropertyInputNode
from . property_output import RBFPropertyOutputNode
from . location_input import RBFLocationInputNode
from . location_output import RBFLocationOutputNode
from . rotation_input import RBFRotationInputNode
from . rotation_output import RBFRotationOutputNode
from . scale_input import RBFScaleInputNode
from . scale_output import RBFScaleOutputNode
from . shapeKey_input import RBFShapeKeyInputNode
from . shapeKey_output import RBFShapeKeyOutputNode
from . node_input import RBFNodeInputNode
from . node_output import RBFNodeOutputNode
from . rbf import RBFSolverNode


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [RBFObjectInputNode,
           RBFObjectOutputNode,
           RBFPoseNode,
           RBFPropertyInputNode,
           RBFPropertyOutputNode,
           RBFLocationInputNode,
           RBFLocationOutputNode,
           RBFRotationInputNode,
           RBFRotationOutputNode,
           RBFScaleInputNode,
           RBFScaleOutputNode,
           RBFShapeKeyInputNode,
           RBFShapeKeyOutputNode,
           RBFNodeInputNode,
           RBFNodeOutputNode,
           RBFSolverNode]


def register():
    """Register the node classes.
    """
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the node classes.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)
