# <pep8 compliant>

import bpy

from . import categories, nodes, nodeTree
from . nodes import sockets


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [nodeTree.RBFNodesNodeTree]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    sockets.register()
    nodes.register()

    # Register the node categories.
    categories.register()


def unregister():
    """Unregister the add-on.
    """
    # Unregister the node categories.
    # This needs to be done before the add-on.
    categories.unregister()

    for cls in classes:
        bpy.utils.unregister_class(cls)

    sockets.unregister()
    nodes.unregister()
