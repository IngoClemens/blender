# <pep8 compliant>


# ----------------------------------------------------------------------
# Global names
# ----------------------------------------------------------------------
NAME = "RBF Nodes"
ID_NAME = "RBFNodes"
NODE_TREE_TYPE = "RBFNodesNodeTree"
CATEGORIES_ID = "RBFNODES_TREE_NODE_CATEGORIES"
CONFIG_NAME = "config.json"

# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------
AUTO_LABEL = True
DEVELOPER_MODE = False
EXPOSE_DATA = False

DEFAULT_CONFIG = {
                    "autoLabel": True,
                    "developerMode": False,
                    "language": "ENGLISH",
                    "logData": False
                }

# ----------------------------------------------------------------------
# Socket colors
# ----------------------------------------------------------------------
COLOR_DEFAULT = [0.608, 0.608, 0.608, 1.0]
COLOR_BLUE = (0.308, 0.771, 0.973, 1.0)
COLOR_GREEN = (0.699, 0.862, 0.3154, 1.0)
COLOR_GREEN_2 = (0.548, 0.736, 0.18, 1.0)
COLOR_GREY = (0.73, 0.73, 0.73, 1)
COLOR_GREY_2 = (0.6, 0.6, 0.6, 1)
COLOR_ORANGE = (0.927, 0.614, 0.362, 1.0)
COLOR_PURPLE = (0.875, 0.587, 1.0, 1.0)
COLOR_RED = (0.933, 0.384, 0.342, 1.0)
COLOR_YELLOW = (0.976, 0.905, 0.426, 1.0)
COLOR_CYAN = (0.404, 0.843, 0.935, 1.0)

# ----------------------------------------------------------------------
# Node positioning
# ----------------------------------------------------------------------
NODE_WIDTH = 155

INPUT_OBJECT_OFFSET = (-300, 100)
OUTPUT_OBJECT_OFFSET = (330, 100)
FIRST_POSE_OFFSET = (-300, -300)
POSE_OFFSET = (0, -95)
FIRST_NODE_OFFSET = (-330, -50)
NODE_OFFSET = (0, -60)

# ----------------------------------------------------------------------
# Properties
# ----------------------------------------------------------------------
ROTATIONS = {'EULER': "rotation_euler",
             'QUATERNION': "rotation_quaternion",
             'AXIS_ANGLE': "rotation_axis_angle"}

ARRAY_SIZE = 4

# ----------------------------------------------------------------------
# Matrix sizes
# ----------------------------------------------------------------------
# The maximum number of values per vector array. This number is fixed
# as defined by Blender.
MAX_LEN = 32
# The number of concatenating arrays for storing pose and weight
# matrices.
# This number needs to be edited when the lists of floatVectorProperties
# are getting extended.
NUM_ARRAYS = 32
# The maximum number of values which can be stored by concatenating the
# floatVectorProperties.
# MAX_SIZE = MAX_LEN * NUM_ARRAYS
