# <pep8 compliant>


# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

# Common
AXIS_ANGLE_LABEL = "Axis Angle"
EULER_LABEL = "Euler"
QUATERNION_LABEL = "Quaternion"

# Preferences
AUTO_LABEL_LABEL = "Auto Label Property Nodes"
DEVELOPER_LABEL = "Developer Mode"
LANGUAGE_LABEL = "Language (Requires Restart)"
LOG_DATA_LABEL = "Log RBF Data"

# Operators
ACTIVATE_RBF_LABEL = "Activate RBF"
ADD_POSE_LABEL = "Add Pose"
CREATE_NODE_INPUT_LABEL = "Link Input Node"
CREATE_NODE_OUTPUT_LABEL = "Link Output Node"
CREATE_RBF_LABEL = "Create New RBF Setup"
DUMP_POSE_LABEL = "Dump Pose"
DUMP_RBF_LABEL = "Dump RBF"
EDIT_DRIVEN_LABEL = "Edit Driven"
EDIT_DRIVER_LABEL = "Edit Driver"
RECALL_POSE_LABEL = "Recall"
RESET_RBF_LABEL = "Reset RBF"

# Panel
ACTIVATION_LABEL = "Activation"
CATEGORY_LABEL = "RBF Nodes"
CREATE_LABEL = "Create"
DEVELOPER_LABEL_SHORT = "Developer"
EDIT_POSE_DATA_LABEL = "Edit Pose Data"
RBF_LABEL = "RBF"
REPLACE_LABEL = "Replace"
SEARCH_LABEL = "Search"

# Nodes
AUTO_LABEL = "Auto"
CUSTOM_INPUT_LABEL = "Custom Input"
CUSTOM_OUTPUT_LABEL = "Custom Output"
CUSTOM_LABEL = "Custom"
DEVIATION_LABEL = "Standard Deviation"
EDITOR_LABEL = "RBF Nodes Editor"
GAUSS_1_LABEL = "Gaussian 1"
GAUSS_2_LABEL = "Gaussian 2"
INPUT_LABEL = "Input"
KERNEL_LABEL = "Kernel"
LINEAR_LABEL = "Linear"
LOCATION_INPUT_LABEL = "Location Input"
LOCATION_OUTPUT_LABEL = "Location Output"
LOCATION_LABEL = "Location"
MANUAL_LABEL = "Manual"
MATERIAL_LABEL = "Material"
MEAN_DISTANCE_LABEL = "Mean Distance"
MODIFIER_INPUT_LABEL = "Modifier Input"
MODIFIER_OUTPUT_LABEL = "Modifier Output"
MODIFIER_LABEL = "Modifier"
MULTI_QUADRATIC_LABEL = "Multi-Quadratic Biharmonic"
MULTI_QUADRATIC_INVERSE_LABEL = "Inverse Multi-Quadratic Biharmonic"
NEGATIVE_WEIGHTS_LABEL = "Negative Weights"
NODE_INPUT_LABEL = "Node Input"
NODE_GROUP_LABEL = "Node Group"
NODE_OUTPUT_LABEL = "Node Output"
NODE_LABEL = "Node"
NODE_SOCKET_LABEL = "RBF Node Socket"
NODES_LABEL = "Nodes"
OBJECT_INPUT_LABEL = "Object Input"
OBJECT_OUTPUT_LABEL = "Object Output"
OBJECT_LABEL = "Object"
OBJECT_SOCKET_LABEL = "RBF Object Socket"
OBJECTS_LABEL = "Objects"
OUTPUT_LABEL = "Output"
PARENT_LABEL = "Parent"
PLUG_LABEL = "Plug"
POSE_LABEL = "Pose"
POSE_SOCKET_LABEL = "RBF Pose Socket"
POSES_LABEL = "Poses"
PROPERTIES_LABEL = "Properties"
PROPERTY_INPUT_LABEL = "Property Input"
PROPERTY_LABEL = "Property"
PROPERTY_OUTPUT_LABEL = "Property Output"
PROPERTY_SOCKET_LABEL = "RBF Property Socket"
RADIUS_LABEL = "Radius"
ROTATION_INPUT_LABEL = "Rotation Input"
ROTATION_LABEL = "Rotation"
ROTATION_OUTPUT_LABEL = "Rotation Output"
SCALE_INPUT_LABEL = "Scale Input"
SCALE_LABEL = "Scale"
SCALE_OUTPUT_LABEL = "Scale Output"
SELECT_LABEL = "––– Select –––"
SHAPE_KEY_INPUT_LABEL = "Shape Key Input"
SHAPE_KEY_LABEL = "Shape Key"
SHAPE_KEY_OUTPUT_LABEL = "Shape Key Output"
THIN_PLATE_LABEL = "Thin Plate"
VARIANCE_LABEL = "Variance"
W_LABEL = "W"
X_LABEL = "X"
Y_LABEL = "Y"
Z_LABEL = "Z"


# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_AUTO_LABEL = "Set the label for property and shape key nodes based on the property name"
ANN_DEVELOPER = "Show developer extras"
ANN_LANGUAGE = "The language for properties and messages"
ANN_LOG_DATA = "Write the RBF data to the command output"

# Operators
ANN_ACTIVATE_RBF = "Initialize the RBF"
ANN_ADD_POSE = "Create a new pose for the current RBF or selected node graph"
ANN_CREATE_NODE_INPUT = "Create a new input node from the current node graph selection"
ANN_CREATE_NODE_OUTPUT = "Create a new output node from the current node graph selection"
ANN_CREATE_RBF = "Create a new node tree with default nodes for a new RBF"
ANN_DUMP_POSE = "Write the pose values of the selected pose node to the command line"
ANN_DUMP_RBF = "Write the pose weight matrix to the command line"
ANN_EDIT_DRIVEN = "Search and replace pose driven data of all poses."
ANN_EDIT_DRIVER = "Search and replace pose driver data of all poses."
ANN_RECALL_POSE = "Set the properties of the RBF to match the selected pose"
ANN_RESET_RBF = "Resets the RBF to it's default and removes all drivers"

# Panel
INFO_RESET_TO_UPDATE = "Reset the RBF to update"
INFO_VERSION_MISMATCH = "Version mismatch"

# Nodes
ANN_EDIT_POSE = "Edit the selected pose. This disables any drivers on the RBF target for editing"

# General
INFO_ADDED_SHAPE_KEY = "Added new shape key to existing pose"
INFO_UPDATE_1 = "The RBF node setup is not compatible with the current version."
INFO_UPDATE_2 = "The installed version is"
INFO_UPDATE_3 = "Please update the node tree with the following steps"
INFO_UPDATE_4 = "1. Press 'Reset RBF' in the RBF editor's side panel."
INFO_UPDATE_5 = "2. Press 'Activate RBF' in the same panel."
INFO_REPLACE = "Replaced occurrences in pose nodes"

# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_DRIVER_MISMATCH = "The number of driver values differs from existing poses"
WARNING_DRIVEN_MISMATCH = "The number of driven values differs from existing poses"
WARNING_INPUT_SIZE_EXCEEDED = "Too many poses or input values"
WARNING_NO_DRIVEN = "No driven object or properties defined"
WARNING_NO_DRIVEN_OBJECT = "No driven object selected"
WARNING_NO_DRIVEN_PROPERTY = "No driven properties defined"
WARNING_NO_DRIVER = "No driver object or properties defined"
WARNING_NO_DRIVER_OBJECT = "No driving object selected"
WARNING_NO_DRIVER_PROPERTY = "No driving properties defined"
WARNING_NO_POSE_NODES = "No pose nodes found in node tree"
WARNING_NO_POSES = "No poses defined"
WARNING_NO_RBF_NODE = "No RBF node to add pose to"
WARNING_NO_RBF_NODE_IN_TREE = "No RBF node found in node tree"
WARNING_NO_SEARCH_STRING = "No string to search for"
WARNING_OUTPUT_SIZE_EXCEEDED = "Too many poses or output values"
WARNING_POSE_MATRIX_SIZE_EXCEEDED = "Maximum pose matrix size exceeded"
WARNING_SIMILAR_POSE = "A pose has no unique values and is similar to another pose. Pose index"
WARNING_POSES_MISMATCH = "The number of poses between input and output is different"
WARNING_TITLE = "RBF Nodes Warning"
WARNING_WEIGHT_MATRIX_SIZE_EXCEEDED = "Maximum weight matrix size exceeded"

ERROR_DECOMPOSITION = "Decomposition error"
ERROR_EVALUATION = "Evaluation error"
ERROR_PROPERTIES_MISMATCH = "Number of pose and driven properties don't match. Possible cause is a difference in Blender versions"
ERROR_WRONG_VALUE_TYPE = "The stored value doesn't match the property value. Possible cause is a difference in Blender versions"
