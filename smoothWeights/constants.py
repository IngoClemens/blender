# <pep8 compliant>

NAME = "smoothWeights"

# Properties
MAP_PROPERTY_NAME = "br_symmetry_map"
WALK_PROPERTY_NAME = "br_walk_sibling_index"

# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

# Preferences
BRUSH_COLOR = (0.263, 0.723, 0.0)
EXTRAS = False
INFO_COLOR = (0.263, 0.723, 0.0)
KEEP_SELECTION = True
SELECTED_COLOR = (0.03, 0.302, 1.0)
SHOW_INFO = True
SHOW_TIME = False
UNDO_STEPS = 20
UNSELECTED_COLOR = (1.0, 1.0, 1.0)

# Common
# The number of weight group assignments.
MAX_GROUPS = 5
# Normalization switch.
NORMALIZE = True

# Smooth Weights
# The name of the color attribute which stores the current selection.
SELECT_COLOR_ATTRIBUTE = "smoothWeights_selection"
# The number of points for the brush circle.
CIRCLE_POINTS = 64

# Switch for smoothing only selected vertices.
AFFECT_SELECTED = True
# The curve options.
CURVE_ITEMS = (("NONE", "None", ""),
               ("LINEAR", "Linear", ""),
               ("SMOOTH", "Smooth", ""),
               ("NARROW", "Narrow", ""))
# The deselection state.
DESELECT = False
# Switch for ignoring backside faces.
IGNORE_BACKSIDE = True
# Switch for ignoring any locked weights.
IGNORE_LOCK = False
# The oversampling value.
OVERSAMPLING = 1
# The default radius of the brush.
RADIUS = 0.25
# The selection state.
SELECT = False
# The default strength of the brush.
STRENGTH = 1.0
# Value for skipping evaluation steps.
UNDERSAMPLING = 3
# Switch for handling islands as a continuous mesh.
USE_ISLANDS = False
# Switch for using selected or unselected vertices.
USE_SELECTION = False
# Switch for using the symmetry map.
USE_SYMMETRY = False
# Switch for toggling between a volume-based and a surface-based brush.
VOLUME = False
# The radius multiplier for finding close vertices in volume mode.
VOLUME_RANGE = 0.2


# Symmetry Map
AXIS = "X"
AXIS_INDICES = {"X": 0, "Y": 1, "Z": 2}
DIRECTION = "POSITIVE"
DIRECTION_INDICES = {"POSITIVE": 1, "NEGATIVE": 0}
TOLERANCE = 0.0
VERBOSE = False

SIDE_LABELS = {"left": "right",
               "lt": "rt",
               "lft": "rgt",
               "lf": "rg",
               "l": "r"}
