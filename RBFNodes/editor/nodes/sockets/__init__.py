# <pep8 compliant>

import bpy

from . node_socket import RBFNodeSocket
from . object_socket import RBFObjectSocket
from . pose_socket import RBFPoseSocket
from . property_socket import RBFPropertySocket


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [RBFNodeSocket,
           RBFObjectSocket,
           RBFPoseSocket,
           RBFPropertySocket]


def register():
    """Register the socket classes.
    """
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the socket classes.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)
