# <pep8 compliant>

from . import language


# Get the current language.
strings = language.getLanguage()


NAME = "smoothWeights"
CONFIG_NAME = "config.json"

PANEL_CLASS = "SMOOTHWEIGHTS_PT_settings"

# Properties
MAP_PROPERTY_NAME = "br_symmetry_map"
META_PROPERTY_NAME = "br_symmetry_map_meta"
WALK_PROPERTY_NAME = "br_walk_sibling_index"

# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

# Preferences
PANEL_LOCATIONS = ["TOOLS", "TAB", "PROPERTIES"]
PANEL_LOCATION_ITEMS = (("TOOLS", strings.PANEL_LOCATION_TOOL_LABEL, ""),
                        ("TAB", strings.PANEL_LOCATION_TAB_LABEL, ""),
                        ("PROPERTIES", strings.PANEL_LOCATION_PROPERTIES_LABEL, ""))
PANEL_AREAS = {"TOOLS": {"bl_label": "",
                         "bl_space_type": 'VIEW_3D',
                         "bl_region_type": 'UI',
                         "bl_category": "Tool"},
               "TAB": {"bl_label": "",
                       "bl_space_type": 'VIEW_3D',
                       "bl_region_type": 'UI',
                       "bl_category": ""},
               "PROPERTIES": {"bl_label": "",
                              "bl_space_type": 'PROPERTIES',
                              "bl_region_type": 'WINDOW',
                              "bl_context": "data"}}
PIE_AREAS = ["pie_west", "pie_east", "pie_south", "pie_north",
             "pie_north_west", "pie_north_east", "pie_south_west", "pie_south_east"]
PIE_ITEMS = ["IGNORE_BACKSIDE",
             "USE_ISLANDS",
             "NORMALIZE",
             "OVERSAMPLING",
             "SELECTION",
             "USE_SYMMETRY",
             "VERTEX_GROUPS",
             "VOLUME",
             "NONE"]
PIE_ENUMS = (("IGNORE_BACKSIDE", strings.IGNORE_BACKSIDE_LABEL, strings.ANN_IGNORE_BACKSIDE),
             ("USE_ISLANDS", strings.USE_ISLANDS_LABEL, strings.ANN_USE_ISLANDS),
             ("NORMALIZE", strings.NORMALIZE_LABEL, strings.ANN_NORMALIZE),
             ("OVERSAMPLING", strings.OVERSAMPLING_LABEL, strings.ANN_OVERSAMPLING),
             ("SELECTION", strings.SELECTION_LABEL, strings.ANN_USE_SELECTION),
             ("USE_SYMMETRY", strings.USE_SYMMETRY_LABEL, strings.ANN_USE_SYMMETRY),
             ("VERTEX_GROUPS", strings.VERTEX_GROUPS_LABEL, strings.ANN_VERTEX_GROUPS),
             ("VOLUME", strings.VOLUME_LABEL, strings.ANN_VOLUME),
             ("NONE", strings.EMPTY_LABEL, strings.ANN_EMPTY))

DEFAULT_CONFIG = {
                    "brushColor": [0.263, 0.723, 0.0],
                    "extras": False,
                    "infoColor": [0.263, 0.723, 0.0],
                    "language": "ENGLISH",
                    "keepSelection": True,
                    "keymap": {
                        "affectSelected": "A",
                        "blend": "J",
                        "clearSelection": "C",
                        "deselect": "E",
                        "flood": "F",
                        "ignoreBackside": "X",
                        "ignoreLock": "L",
                        "islands": "I",
                        "maxGroups": "G",
                        "normalize": "N",
                        "oversampling": "O",
                        "pieMenu": "Y",
                        "radius": "B",
                        "select": "W",
                        "strength": "S",
                        "useSelection": "Q",
                        "useSymmetry": "T",
                        "value_down": "MINUS",
                        "value_up": "PLUS",
                        "vertexGroups": "D",
                        "volume": "V",
                        "volumeRange": "R"
                    },
                    "panelLocation": 'TOOLS',
                    "panelName": strings.MENU_SMOOTH_WEIGHTS,
                    "pieMenu": True,
                    "selectedColor": [0.03, 0.302, 1.0],
                    "showInfo": True,
                    "showTime": False,
                    "smoothPie": [
                        "VERTEX_GROUPS",
                        "OVERSAMPLING",
                        "VOLUME",
                        "USE_SYMMETRY",
                        "SELECTION",
                        "USE_ISLANDS",
                        "IGNORE_BACKSIDE",
                        "NORMALIZE"
                    ],
                    "undoSteps": 20,
                    "unselectedColor": [1.0, 1.0, 1.0]
                }


# Common
# The number of weight group assignments.
MAX_GROUPS = 5
# Normalization switch.
NORMALIZE = True
# The vertex groups to affect.
VERTEX_GROUPS = (("ALL", strings.VERTEX_GROUPS_ALL_LABEL, strings.ANN_VERTEX_GROUPS_ALL),
                 ("DEFORM", strings.VERTEX_GROUPS_DEFORM_LABEL, strings.ANN_VERTEX_GROUPS_DEFORM),
                 ("OTHER", strings.VERTEX_GROUPS_OTHER_LABEL, strings.ANN_VERTEX_GROUPS_OTHER))
VERTEX_GROUPS_ITEMS = ["ALL", "DEFORM", "OTHER"]


# Smooth Weights
# The name of the color attribute which stores the current selection.
SELECT_COLOR_ATTRIBUTE = "smoothWeights_selection"
# The number of points for the brush circle.
CIRCLE_POINTS = 64

# Switch for smoothing only selected vertices.
AFFECT_SELECTED = True
# Switch for blending open vertex group borders.
BLEND = True
# The curve options.
CURVE_ITEMS = (("NONE", strings.CURVE_NONE_LABEL, ""),
               ("LINEAR", strings.CURVE_LINEAR_LABEL, ""),
               ("SMOOTH", strings.SMOOTH_LABEL, ""),
               ("NARROW", strings.CURVE_NARROW_LABEL, ""))
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
