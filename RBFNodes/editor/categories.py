# <pep8 compliant>

import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

from .. import var


class RBFNodesNodeCategory(NodeCategory):
    """Class to define which node tree the RBF categories belong to.
    """
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == var.NODE_TREE_TYPE


# Define the categories.
categories = [RBFNodesNodeCategory('INPUT',
                                   "Input",
                                   items=[NodeItem("RBFObjectInputNode"),
                                          NodeItem("RBFLocationInputNode"),
                                          NodeItem("RBFRotationInputNode"),
                                          NodeItem("RBFScaleInputNode"),
                                          NodeItem("RBFPropertyInputNode"),
                                          NodeItem("RBFShapeKeyInputNode"),
                                          NodeItem("RBFNodeInputNode")]),
              RBFNodesNodeCategory('OUTPUT',
                                   "Output",
                                   items=[NodeItem("RBFObjectOutputNode"),
                                          NodeItem("RBFLocationOutputNode"),
                                          NodeItem("RBFRotationOutputNode"),
                                          NodeItem("RBFScaleOutputNode"),
                                          NodeItem("RBFPropertyOutputNode"),
                                          NodeItem("RBFShapeKeyOutputNode"),
                                          NodeItem("RBFNodeOutputNode")]),
              RBFNodesNodeCategory('RBF',
                                   "RBF",
                                   items=[NodeItem("RBFSolverNode")])]


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

def register():
    """Register the node categories.
    """
    nodeitems_utils.register_node_categories(var.CATEGORIES_ID, categories)


def unregister():
    """Unregister the node categories.

    These need to be unregistered before unregistering the add-on.
    """
    nodeitems_utils.unregister_node_categories(var.CATEGORIES_ID)
