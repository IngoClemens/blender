# <pep8 compliant>

import bpy
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

from .. import language, var


# Get the current language.
strings = language.getLanguage()


class RBFNodesNodeCategory(NodeCategory):
    """Class to define which node tree the RBF categories belong to.
    """
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == var.NODE_TREE_TYPE


# Define the categories.
categories = [RBFNodesNodeCategory('INPUT',
                                   strings.INPUT_LABEL,
                                   items=[NodeItem("RBFObjectInputNode"),
                                          NodeItem("RBFLocationInputNode"),
                                          NodeItem("RBFRotationInputNode"),
                                          NodeItem("RBFScaleInputNode"),
                                          NodeItem("RBFPropertyInputNode"),
                                          NodeItem("RBFCustomInputNode"),
                                          NodeItem("RBFShapeKeyInputNode"),
                                          NodeItem("RBFModifierInputNode"),
                                          NodeItem("RBFNodeInputNode")]),
              RBFNodesNodeCategory('OUTPUT',
                                   strings.OUTPUT_LABEL,
                                   items=[NodeItem("RBFObjectOutputNode"),
                                          NodeItem("RBFLocationOutputNode"),
                                          NodeItem("RBFRotationOutputNode"),
                                          NodeItem("RBFScaleOutputNode"),
                                          NodeItem("RBFPropertyOutputNode"),
                                          NodeItem("RBFCustomOutputNode"),
                                          NodeItem("RBFShapeKeyOutputNode"),
                                          NodeItem("RBFModifierOutputNode"),
                                          NodeItem("RBFNodeOutputNode")]),
              RBFNodesNodeCategory('RBF',
                                   strings.RBF_LABEL,
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
