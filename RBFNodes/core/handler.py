# <pep8 compliant>

import bpy
from bpy.app.handlers import persistent

from . import nodeTree, rbf, utils
from .. import language


# Get the current language.
strings = language.getLanguage()


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
                    title = strings.ERROR_EVALUATION
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
                title = strings.WARNING_TITLE
                message = [strings.INFO_UPDATE_1,
                           "{} {}".format(strings.INFO_UPDATE_2, utils.versionString(utils.VERSION)),
                           "{}:".format(strings.INFO_UPDATE_3),
                           strings.INFO_UPDATE_4,
                           strings.INFO_UPDATE_5]
                if not bpy.app.background:
                    utils.displayMessage(title, message, 'ERROR')
                else:
                    print("{} : {}".format(title, message))
                return
