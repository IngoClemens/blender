# <pep8 compliant>

# ----------------------------------------------------------------------
# Label
# ----------------------------------------------------------------------

NAME_LABEL = "Tool Shelf"

# Preferences
LANGUAGE_LABEL = "Language (Requires Restart)"

ADD_GROUP_LABEL = "Add Group"
ADD_TOOL_LABEL = "Add Tool"
ADDON_TOGGLE_LABEL = "Add-on Toggle"
ADDON_LABEL = "Add-on"
AFTER_GROUP_LABEL = "After Group"
AFTER_TOOL_LABEL = "After Tool"
APPLY_ORDER_LABEL = "Apply Order"
AUTO_EXPAND_LABEL = "Auto Expand"
COMMAND_LABEL = "Command"
COMMANDS_LABEL = "Commands"
DELETE_LABEL = "Delete"
EDIT_LABEL = "Edit"
EDIT_SET_LABEL = "Edit Set"
GROUP_LABEL = "Group"
ICON_LABEL = "Icon"
ICONS_LABEL = "Icons"
ICON_ONLY_LABEL = "Icon Only"
IMPORT_LABEL = "Import"
LABELS_LABEL = "Labels"
MOVE_ITEM_DOWN_LABEL = "Move Item Down"
MOVE_ITEM_UP_LABEL = "Move Item Up"
MODE_LABEL = "Mode"
MOVE_DOWN_LABEL = "Move Down"
MOVE_UP_LABEL = "Move Up"
NEW_GROUP_LABEL = "New Group"
NEW_NAME_LABEL = "Name"
NEW_SET_LABEL = "New Set"
PROPERTY_LABEL = "Property"
PROPERTY_VALUE_LABEL = "Value"
PROPERTY_CALLBACK_LABEL = "Command As Callback"
ROW_BUTTONS_LABEL = "Row Buttons"
SELECT_ITEM_LABEL = "––– Select –––"
SET_NAME_LABEL = "Set Name"
SETUP_LABEL = "Setup"
TOOL_LABEL = "Tool"
TOOLTIP_LABEL = "Tooltip"
VIEW_COMMAND_LABEL = "View Command"

# ----------------------------------------------------------------------
# Description/Annotation
# ----------------------------------------------------------------------

# Preferences
ANN_LANGUAGE = "The language for properties and messages"

ANN_ADDON = "The add-on to create a toggle button for"
ANN_COMMAND = ("The command string for the button.\n"
               "For simple commands the bpy import is added automatically.\n"
               "Leave empty to get the content from the text editor")
ANN_EXECUTE_MODE = "Execute the current mode"
ANN_EXPAND = "Set the group to be expanded by default"
ANN_IMPORT_FILE = "The configuration file to import groups or tools from"
ANN_IMPORT_ITEM = "The group or tool to import"
ANN_GROUP = ("The group to add the tool to.\n"
             "A new group it will be created after the last or after the selected group item")
ANN_ICON = ("The name of the icon file with 32x32 pixel or a default Blender icon identifier "
            "enclosed in single quotes or a unicode character")
ANN_ICON_ONLY = "Only show the icon instead of the button label"
ANN_ITEM_ADD_NEW = "Add a new group or tool"
ANN_ITEM_DELETE_EXISTING = "Delete an existing group or button"
ANN_ITEM_DISPLAY_COMMAND = "Display a button command in the text editor"
ANN_ITEM_IMPORT = "Import a group or tool from a configuration file"
ANN_ITEM_OVERWRITE = ("Overwrite the command of an existing button.\nUse the asterisk * "
                      "symbol to keep existing settings")
ANN_ITEM_REORDER = "Reorder groups and buttons"
ANN_MODE = "Switch the editing mode"
ANN_NAME = ("The name of the group or tool.\n"
            "It needs to be unique in lowercase across all groups")
ANN_NEW_GROUP = "Add a new group instead of a new tool"
ANN_NEW_SET = "Add a new tool set"
ANN_PROPERTY = "Add a numeric, boolean or string property to the tool"
ANN_PROPERTY_NAME = "The name of the property"
ANN_PROPERTY_VALUE = ("The default value for the property. To define minimum and maximum values "
                      "use the format: value, value, value")
ANN_PROPERTY_CALLBACK = ("Use the command string as the body of a callback function for all "
                         "properties with their update option set")
ANN_SELECT_GROUP = "Select a group"
ANN_SET_COLUMNS = "The number of buttons in a row"
ANN_SET_NAME = "The name of the button set"
ANN_TOGGLE_ADDON = "Create a button to enable or disable an add-on"
ANN_TOOL = "The tool command to edit"
ANN_TOOLTIP = "The tooltip for the button"

# ----------------------------------------------------------------------
# Info
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Warning/Error
# ----------------------------------------------------------------------

WARNING_ADDON_INCOMPATIBLE = "The add-on is incompatible and has to be enabled/disabled from the preferences: "
WARNING_ADDON_MISSING = "An add-on with this name doesn't exist: "
WARNING_BRACKETS_INCOMPLETE = "The brackets for the properties are incomplete"
WARNING_GROUP_NAME_EXISTS = "The group name already exists"
WARNING_IMAGE_MISSING = "The image doesn't exist in the path: "
WARNING_LABEL_COMMAND_MISMATCH = "The number of tool labels and commands does not match"
WARNING_NO_GROUP_SELECTED = "No group selected"
WARNING_NO_NAME = "No name defined"
WARNING_NO_TEXT_EDITOR = "No text editor open to get the tool command"
WARNING_NO_TEXT_EDITOR_TO_VIEW = "No text editor open to view the command"
WARNING_NO_TOOL_IN_GROUP = "No tool exists in the selected group"
WARNING_NO_TOOL_SELECTED = "No tool selected"
WARNING_PROPERTY_NAME_MISSING = "A property name and/or default value is missing"
WARNING_PROPERTY_VALUE_MISMATCH = "The number of properties and values does not match"
WARNING_SELECT_CONFIG = "Select a valid configuration file"
WARNING_SELECT_TO_IMPORT = "Select a group or tool to import"
WARNING_TOOL_EXISTS_IN_GROUP = "The tool name already exists in the group"
