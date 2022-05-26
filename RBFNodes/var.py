# <pep8 compliant>

DEVELOPER_MODE = False
EXPOSE_DATA = False

NAME = "RBF Nodes"

NODE_TREE_TYPE = "RBFNodesNodeTree"

CATEGORIES_ID = "RBFNODES_TREE_NODE_CATEGORIES"

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

INPUT_OBJECT_OFFSET = (-300, 100)
OUTPUT_OBJECT_OFFSET = (300, 100)
FIRST_POSE_OFFSET = (-300, -300)
POSE_OFFSET = (0, -45)
FIRST_NODE_OFFSET = (-300, -50)
NODE_OFFSET = (0, -50)

ROTATIONS = {'EULER': "rotation_euler",
             'QUATERNION': "rotation_quaternion",
             'AXIS_ANGLE': "rotation_axis_angle"}

ROTATION_MODE = [('EULER', "Euler", "", "", 1),
                 ('QUATERNION', "Quaternion", "", "", 2),
                 ('AXIS_ANGLE', "Axis Angle", "", "", 3)]

ROTATION_TYPE = [('SWING', "Swing", "", "", 1),
                 ('TWIST', "Twist", "", "", 2),
                 ('SWING_TWIST', "Swing Twist", "", "", 3)]
