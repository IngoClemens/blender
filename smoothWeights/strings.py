# <pep8 compliant>


# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

# Common
MAX_GROUPS_LABEL = "Max Groups"
NORMALIZE_LABEL = "Normalize"

# Smooth Weights
AFFECT_SELECTED_LABEL = "Affect Selected"
BRUSH_COLOR_LABEL = "Brush Color"
CLEAR_SELECTION_LABEL = "Clear Selection"
CURVE_LABEL = "Curve"
DECREASE_VALUE_LABEL = "Decrease Value"
DESELECT_LABEL = "Deselect"
EXTRAS_LABEL = "Show Extras"
FLOOD_LABEL = "Flood"
IGNORE_BACKSIDE_LABEL = "Ignore Backside"
IGNORE_LOCK_LABEL = "Ignore Lock"
INCREASE_VALUE_LABEL = "Increase Value"
INFO_TEXT_COLOR_LABEL = "Tool Info Color"
KEEP_SELECTION_LABEL = "Keep Selection After Finishing"
OVERSAMPLING_LABEL = "Oversampling"
USE_ISLANDS_LABEL = "Use Islands"
USE_SELECTION_LABEL = "Use Selection"
USE_SYMMETRY_LABEL = "Use Symmetry"
RADIUS_LABEL = "Radius"
SELECT_LABEL = "Select"
SELECTED_COLOR_LABEL = "Selected Color"
SHOW_INFO_LABEL = "Show Tool Info"
SHOW_TIME_LABEL = "Show Execution Time"
STRENGTH_LABEL = "Strength"
UNDO_STEPS_LABEL = "Undo Steps"
UNSELECTED_COLOR_LABEL = "Unselected Color"
VOLUME_LABEL = "Use Volume"
VOLUME_RANGE_LABEL = "Volume Range"

# Symmetry Map
AXIS_LABEL = "Axis"
DIRECTION_LABEL = "Direction From"
TOLERANCE_LABEL = "Tolerance"
VERBOSE_LABEL = "Verbose"


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

MENU_FLOOD_SMOOTH = "Flood Smooth Weights"
MENU_LIMIT_GROUPS = "Limit Weight Groups"
MENU_SMOOTH_WEIGHTS = "Smooth Weights"


# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Common
ANN_MAX_GROUPS = "The number of vertex groups a vertex can share weights with. A zero value disables the limit"
ANN_NORMALIZE = "Normalize the averaged weights to a sum of 1"

# Smooth Weights
ANN_AFFECT_SELECTED = "Smooth only the selected vertices"
ANN_BRUSH_COLOR = "Display color for the brush circle (not gamma corrected)"
ANN_CLEAR_SELECTION = "Clear the selection"
ANN_CURVE = "The brush falloff curve"
ANN_DESELECT = "Deselect vertices"
ANN_EXTRAS = "Enable additional tools and properties"
ANN_FLOOD = "Flood smooth the vertex weights"
ANN_IGNORE_BACKSIDE = "Ignore faces which are viewed from the back"
ANN_IGNORE_LOCK = "Ignore the lock status of a vertex group"
ANN_INFO_COLOR = "Display color for the in-view info (not gamma corrected)"
ANN_KEEP_SELECTION = "Keep the tool selection vertices as selected vertices after finishing the tool"
ANN_OVERSAMPLING = "The number of iterations for the smoothing"
ANN_RADIUS = "The brush radius in generic Blender units"
ANN_SELECT = "Select vertices"
ANN_SELECTED_COLOR = "The color for selected vertices"
ANN_SHOW_INFO = "Display all tool settings and keymaps in the 3D view"
ANN_SHOW_TIME = "Display the execution time for the operators"
ANN_STRENGTH = "The strength of the smoothing stroke"
ANN_UNDO_STEPS = "Number of available undo steps"
ANN_UNSELECTED_COLOR = "The color for unselected vertices"
ANN_USE_ISLANDS = "Limit the smoothing to the current island when in surface mode"
ANN_USE_SELECTION = "Use only selected or unselected vertices for smoothing"
ANN_USE_SYMMETRY = "Use the symmetry map to mirror the weights according to the mesh topology"
ANN_VALUE_DOWN = "Decrease the maximum vertex groups or oversampling"
ANN_VALUE_UP = "Increase the maximum vertex groups or oversampling"
ANN_VOLUME = "Smooth weights within the brush volume. When off the weights are averaged based on linked vertices"
ANN_VOLUME_RANGE = "Scale factor for radius, determining neighboring vertices in volume mode"

# Symmetry Map
ANN_AXIS = "The axis which defines the symmetry. Also used as the mirror axis"
ANN_DIRECTION = "The direction to mirror values"
ANN_TOLERANCE = ("Value for finding symmetry points. Zero for automatic "
                 "tolerance based on average edge length")
ANN_VERBOSE = "Outputs the mapping result to the command line"


# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------

# Smooth Weights
INFO_FLOOD_FINISHED = "Flood smooth finished"

# Symmetry Map
INFO_CENTER_VERTEX = "Center vertex "
INFO_CLEARED_WALK_INDEX = "Cleared sibling walk index"
INFO_FLIP_MESH_FINISHED = "Flip mesh finished"
INFO_MAPPED = "Mapped "
INFO_MAPPING_COMPLETE = "Mapping complete"
INFO_MAPPING_FINISHED = "Mapping finished"
INFO_MAPPING_FOUND = "Symmetry mapping found "
INFO_MAPPING_NOT_SET = "Mapping not set"
INFO_MAP_REMOVED = "Symmetry map removed"
INFO_MIRROR_WEIGHTS_FINISHED = "Mirror weights finished"
INFO_MIRRORED = "Mirrored "
INFO_PARTIAL_FINISHED = "Partial mapping finished"
INFO_PARTIAL_MAP = "Partial mapping "
INFO_SELECTED = " selected"
INFO_SYMMETRIZE_FINISHED = "Symmetrize mesh finished"
INFO_USED_FOR_MAPPING = " used for mapping"
INFO_VERTEX_PAIR = "Vertices "
INFO_VERTICES = " vertices"
INFO_VERTICES_SELECTED = " vertices selected"


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

# Smooth Weights
WARNING_NO_OBJECT = "No object selected to smooth"

# Symmetry Map
ERROR_NON_MANIFOLD = "The mesh has non-manifold geometry"
ERROR_NO_POINTS_FOUND = "No selection or no symmetrical points found"
ERROR_TRAVERSE_COUNT = "Face count is different while traversing vertices: "
ERROR_PASS_COUNT_MISMATCH = "Mapping failed. The passes have a different vertex count. Vertices: "
ERROR_VERTEX_COUNT_MISMATCH = "Vertex count mismatch"

WARNING_EDGE_NOT_CONNECTED = "The symmetry edge is not connected to any faces"
WARNING_EDGE_NEEDS_TWO_FACES = "The symmetry edge must be connected to two faces"
WARNING_NO_EDGE_SELECTION = "No valid edge selection found for symmetry mapping"
WARNING_NO_MAPPING = "The object has no symmetry mapping"
WARNING_NO_SIBLING = "No sibling/s found"
