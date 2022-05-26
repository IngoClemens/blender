# <pep8 compliant>

import bpy
from bpy.app.handlers import persistent

from . import nodeTree, rbf

import time


class Timer(object):
    """Timer class for comparing refresh times.
    """
    def __init__(self):
        self.start = None


updateTimer = Timer()


@persistent
def refresh(none):
    """Check, if the elapsed time requires an update of the solvers in
    the scene.
    """
    update = False
    if updateTimer.start is None or time.time() - updateTimer.start > 0.01:
        updateTimer.start = time.time()
        update = True

    if update:
        trees = nodeTree.getSceneTrees()
        for tree in trees:
            nodes = nodeTree.getRBFFromTree(tree)
            for rbfNode in nodes:
                if rbfNode.active and not rbfNode.mute:
                    rbf.getPoseWeights(rbfNode)
