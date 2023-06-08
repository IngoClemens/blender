# <pep8 compliant>

import bpy
from bpy.app.handlers import persistent

from . import nodeTree, rbf, utils
from .. var import VERSION


@persistent
def refresh(none):
    """Check, if the elapsed time requires an update of the solvers in
    the scene.
    """
    trees = nodeTree.getSceneTrees()
    for tree in trees:
        nodes = nodeTree.getRBFFromTree(tree)
        for rbfNode in nodes:
            if rbfNode.active and not rbfNode.mute:
                result = rbf.getPoseWeights(rbfNode)
                if result is not None:
                    title = "Evaluation error"
                    if not bpy.app.background:
                        utils.displayMessage(title, result, 'ERROR')
                    else:
                        print("{} : {}".format(title, result))

@persistent
def verifyVersion(none):
    """Check, if the contained RBF nodes of a file match the current
    version.
    """
    trees = nodeTree.getSceneTrees()
    for tree in trees:
        nodes = nodeTree.getRBFFromTree(tree)
        for rbfNode in nodes:
            if not utils.verifyVersion(rbfNode):
                title = "RBF Nodes Warning"
                message = ["The RBF node setup is not compatible with the current version.",
                           "The installed version is {}".format(utils.versionString(VERSION)),
                           "Please update the node tree with the following steps:",
                           "1. Press 'Reset RBF' in the RBF editor's side panel.",
                           "2. Press 'Activate RBF' in the same panel."]
                if not bpy.app.background:
                    utils.displayMessage(title, message, 'ERROR')
                else:
                    print("{} : {}".format(title, message))
                return
