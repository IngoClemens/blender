"""
toolShelf
Copyright (C) 2021-2022, Ingo Clemens, brave rabbit, www.braverabbit.com

    GNU GENERAL PUBLIC LICENSE Version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------

Description:

Tool Shelf provides a panel to create any number of grouped buttons to
execute custom code and scripts to optimize workflow.
The commands for each button can be either typed in directly or by
retrieving it from the text editor. This works with a complete text
document or any selection.
Groups and buttons can be edited afterwards, as well as having their
order changed.
Button commands can be extracted at any time by copying them to the text
editor.

------------------------------------------------------------------------

Changelog:

0.11.0 - 2023-03-24
       - Added the option to open a file browser to provide a file path
         for the operator via the BROWSER_GET_FILE placeholder.
         Because of a current Blender bug only files can be selected,
         not folders.
       - Fixed that expanded enum properties are not displayed anymore.
0.10.0 - 2022-11-25
       - Property placeholders for single properties can now also be
         PROP1, to be consistent with the formatting for multiple
         properties.
       - Added a basic spell check for string and boolean property
         types.
       - Fixed that entries ending with a colon caused the tool to fail.
       - Added Substance3DInBlender to the black list of add-ons.

0.9.0 - 2022-02-10
      - Added an option to set a group to be expanded by default.
      - Added undo capability to operator buttons.
      - Fixed that editing is not possible when New Group is active in
        Add Mode.

0.8.0 - 2021-06-01
      - Added tooltips for enum properties.
      - Fixed that enum items don't show their labels.

0.7.0 - 2021-05-31
      - Changed that drawing of labels for properties in a row doesn't
        depend on the total number of properties but just the number of
        properties in a single row.
      - Added the option to expand enum properties to appear as a line
        of buttons.
      - Added the option to use the tool command as a property callback
        as an alternative to having to press the tool button to execute
        the tool.

0.6.0 - 2021-05-27
      - Added the option to add enum properties.
      - Added the option to align multiple properties in a row rather
        than having them appear as a column.

0.5.0 - 2021-05-20
      - Added the option to use unicode characters instead of a label
        for a button.
      - Added the option to only show the button icon.
      - String properties can be defined by entering string in the value
        field.

0.4.0 - 2021-05-16
      - Added the option to add properties to a tool or tool set.

0.3.0 - 2021-05-09
      - Added the option to combine multiple buttons as a set.
      - Tool names can be repeated across all groups.
      - Import of groups and tools from another configuration file.

0.2.0 - 2021-04-29
      - Added an option to define a button as an add-on toggle.

0.1.0 - 2021-04-22
      - First public release

------------------------------------------------------------------------
"""

import bpy
import bpy.utils.previews
import addon_utils
from bpy_extras.io_utils import ImportHelper

import copy
import inspect
import io
import json
import logging
import os
import re
import sys
import types

bl_info = {"name": "Tool Shelf",
           "author": "Ingo Clemens",
           "version": (0, 11, 0),
           "blender": (2, 92, 0),
           "category": "Interface",
           "location": "View3D",
           "description": "Save scripts as buttons and organize them in groups for easy access",
           "warning": "",
           "doc_url": "https://www.braverabbit.com/toolShelf",
           "tracker_url": ""}


logger = logging.getLogger(__name__)


CONFIG_NAME = "config.json"
LOCAL_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(LOCAL_PATH, CONFIG_NAME)
ICONS_PATH = os.path.join(LOCAL_PATH, "icons")
SCRIPTS_PATH = os.path.join(LOCAL_PATH, "scripts")
BACKUP_PATH = os.path.join(LOCAL_PATH, "backup")
BACKUP_COUNT = 5

# The dictionary containing the panel and button data.
CONFIG_DATA = {}
# The backup dictionary for the configuration when reordering items.
CONFIG_DATA_BACKUP = {}
# The class instance to access the dictionary containing the button data
# to import from.
CONFIG_DATA_IMPORT = None
# The list of all classes representing the buttons.
CMD_CLASSES = []
# The dictionary with all button data per group.
GROUPS = []
# The list of all button icons.
ICONS = []
# Main dictionary for storing the menu icons.
ICON_COLLECTION = {}
# The list of custom properties.
PROPERTIES = []
# The list of property callbacks.
CALLBACKS = []

UPDATE_FIELDS = True

# Add the current path to the system in case other scripts are placed
# here.
sys.path.append(SCRIPTS_PATH)

# Define the alphanumeric regex pattern for the operator class name and
# idname.
ALPHANUM = re.compile("\W", re.UNICODE)
BRACKETS = re.compile("[\[\]()<>]")

# ----------------------------------------------------------------------
# Descriptions and tooltips
# ----------------------------------------------------------------------

ANN_ADDON = "The add-on to create a toggle button for"
ANN_COMMAND = ("The command string for the button.\n"
               "For simple commands the bpy import is added automatically.\n"
               "Leave empty to get the content from the text editor")
ANN_EXPAND = "Set the group to be expanded by default"
ANN_IMPORT_FILE = ("The configuration file to import groups or "
                   "tools from")
ANN_IMPORT_ITEM = "The group or tool to import"
ANN_GROUP = ("The group to add the tool to.\n"
             "A new group it will be created after the last or after the selected group item")
ANN_ICON = ("The name of the icon file with 32x32 pixel or a default Blender icon identifier "
            "enclosed in single quotes or a unicode character")
ANN_ICON_ONLY = "Only show the icon instead of the button label"
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
ANN_SET_COLUMNS = "The number of buttons in a row"
ANN_SET_NAME = "The name of the button set"
ANN_TOGGLE_ADDON = "Create a button to enable or disable an add-on"
ANN_TOOL = "The tool command to edit"
ANN_TOOLTIP = "The tooltip for the button"

# ----------------------------------------------------------------------
# List of add-ons not suitable for a toggle button.
# ----------------------------------------------------------------------

ADD_ON_BLACKLIST = ["animation_animall", "blender_id", "blenderkit", "curve_assign_shapekey",
                    "curve_tools", "greasepencil_tools", "io_export_paper_model", "io_mesh_atomic",
                    "magic_uv", "materials_library_vx", "mesh_auto_mirror", "mesh_bsurfaces",
                    "mesh_tools", "object_boolean_tools", "object_collection_manager",
                    "space_view3d_3d_navigation", "space_view3d_pie_menus", "Substance3DInBlender"]

# ----------------------------------------------------------------------
# 1. Read the configuration.
# Get all panel and button relevant data from the config.json file.
# Because the panel is build dynamically all steps depend on this file.
# ----------------------------------------------------------------------


def createDir(dirPath):
    """Create the given folder if it doesn't exist.

    :param dirPath: The path of the folder to create.
    :type dirPath: str

    :return: The path of the folder.
    :rtype: str
    """
    if not os.path.exists(dirPath):
        try:
            os.makedirs(dirPath)
        except OSError as exception:
            logger.error(exception)
    return dirPath


def configBase():
    """Return the basic dictionary of the tool shelf configuration.

    :return: The basic configuration dictionary.
    :rtype: dict
    """
    return {
                "name": "Tool Shelf",
                "category": "Tool Shelf",
                "label": "Tool Shelf",
                "region": "UI",
                "space": "VIEW_3D",
                "base": "view3d",
                "groups": []
            }


def readConfig():
    """Read the configuration file. If the file doesn't exist create the
    basic configuration and return it.
    Also return the default paths for icons, scripts and backup.

    :return: The content if the configuration file.
    :rtype: dict
    """
    for dirName in [ICONS_PATH, SCRIPTS_PATH, BACKUP_PATH]:
        createDir(dirName)

    if os.path.exists(CONFIG_PATH):
        return jsonRead(CONFIG_PATH)
    else:
        config = configBase()
        jsonWrite(CONFIG_PATH, config)
        return config


def jsonRead(filePath):
    """Return the content of the given json file. Return an empty
    dictionary if the file doesn't exist.

    :param filePath: The file path of the file to read.
    :type filePath: str

    :return: The content of the json file.
    :rtype: dict
    """
    content = {}

    if os.path.exists(filePath):
        try:
            with open(filePath, "r") as fileObj:
                return json.load(fileObj)
        except OSError as exception:
            logger.error(exception)
    return content


def jsonWrite(filePath, data):
    """Export the given data to the given json file.

    :param filePath: The file path of the file to write.
    :type filePath: str
    :param data: The data to write.
    :type data: dict or list

    :return: True, if writing was successful.
    :rtype: bool
    """
    # Make the unicode encoding work with Python 2 and 3.
    try:
        toUnicode = unicode
    except NameError:
        toUnicode = str

    try:
        with io.open(filePath, "w", encoding="utf8") as fileObj:
            writeString = json.dumps(addVersions(data), sort_keys=True, indent=4, ensure_ascii=False)
            fileObj.write(toUnicode(writeString))
        return True
    except OSError as exception:
        logger.error(exception)
    return False


def addVersions(data):
    """Add the current tool and blender versions to the configuration.

    :param data: The configuration data.
    :type data: dict

    :return: The configuration data.
    :rtype: dict
    """
    data["version"] = ".".join(str(i) for i in bl_info["version"])
    data["blenderVersion"] = bpy.app.version_string
    return data


def backupConfig(data):
    """Backup the given configuration.

    :param data: The configuration dictionary to backup.
    :type data: dict
    """
    backupFileName = "config_{}.json".format(nextBackupIndex())
    backupFilePath = os.path.join(BACKUP_PATH, backupFileName)
    jsonWrite(backupFilePath, data)


def nextBackupIndex():
    """Return the next index for the configuration backup. If the folder
    doesn't exist, create it.
    Get the index of the last file and compare it to the number of
    backup files.

    :return: The next index for the backup configuration.
    :rtype: int
    """
    fileList = os.listdir(createDir(BACKUP_PATH))
    if not len(fileList) or not fileList[-1].endswith(".json"):
        return 1

    lastIndex = int(fileList[-1].split(".")[0].split("_")[-1])
    newIndex = (lastIndex+1) % BACKUP_COUNT

    return newIndex


def updateConfig(data):
    """Update older configurations with mandatory settings.

    :param data: The configuration data.
    :type data: dict

    :return: The updated configuration data.
    :rtype: dict
    """
    # Cancel if no groups have been defined.
    if "groups" not in data:
        return data

    config = dict(data)

    updateItems = [("iconOnly", False)]

    update = False
    for i in range(len(config["groups"])):
        group = config["groups"][i]
        for j in range(len(group["commands"])):
            command = group["commands"][j]
            if "set" in command:
                for k in range(len(command["commands"])):
                    setCommand = command["commands"][k]
                    for item in updateItems:
                        if item[0] not in setCommand:
                            config["groups"][i]["commands"][j]["commands"][k][item[0]] = item[1]
                            update = True
                    # Copy the properties to the set commands.
                    if "valueName" in command and "valueName" not in setCommand:
                        config["groups"][i]["commands"][j]["commands"][k]["valueName"] = command["valueName"]
                        config["groups"][i]["commands"][j]["commands"][k]["value"] = command["value"]
                        update = True

            else:
                for item in updateItems:
                    if item[0] not in command:
                        config["groups"][i]["commands"][j][item[0]] = item[1]
                        update = True

    if update:
        # Backup the current configuration.
        backupConfig(data)
        # Save the configuration.
        jsonWrite(CONFIG_PATH, config)

    return config


CONFIG_DATA = updateConfig(readConfig())


# ----------------------------------------------------------------------
# 2. Build the tool content classes.
# Create the operator class for each command represented by a button.
# A class contains the label, description and command executed by the
# button.
# ----------------------------------------------------------------------

# This method gets read through inspect and is added for each add-on
# toggle button.
def toggleAddOn(name):
    import addon_utils
    enabled, loaded = addon_utils.check(name)
    if not loaded:
        addon_utils.enable(name)
    else:
        addon_utils.disable(name)


def isAddOnToggle(command):
    """Return if the command toggles an add-on.

    :param command: The button command.
    :type command: str

    :return: True, if the command toggles an add-on.
    :rtype: bool
    """
    return command.startswith("toggleAddOn")


def getAddOns():
    """Return a list with all installed add-ons.

    :return: A list dictionaries containing all add-on names and
             categories.
    :rtype: list(dict())
    """
    items = []
    for mod in addon_utils.modules():
        info = {"name": mod.__name__,
                "label": mod.bl_info["name"],
                "category": mod.bl_info["category"]}
        items.append(info)

    return items


def idName(name):
    """Return a valid idname for the operator in lowercase and with
    underscores.

    Converting the name to an id name is primarily used to generate the
    bl_idname for the operator. But it's also needed for comparing if
    a new command matches an existing. This is important since the name
    is converted to a lowercase representation for the id name and there
    is no other indication if a new command name is entered with some
    uppercase letters.

    :param name: The command name.
    :type name: str

    :return: The idname string for the operator.
    :rtype: str
    """
    name = name.lower().replace(" ", "_").replace("+", "pos").replace("-", "neg")
    return "tool_shelf_{}".format(re.sub(ALPHANUM, "", name))


def getIdName(data, group):
    """Return the bl_idname for the given operator which gets combined
    from the UI area, i.e. view3d, the group and the lowercase name of
    the tool.

    Including the group in the idname makes it possible to have the same
    tool name in different groups which increases naming flexibility.

    :param data: The dictionary which describes the command.
    :type data: dict
    :param group: The name of the group the command belongs to.
    :type group: str

    :return: The idname string for the operator.
    :rtype: str
    """
    # If the command belongs to a set add the set name as a prefix to
    # make the idname unique. This allows to keep the button label
    # short, which can be useful in case of a set.
    items = [group.replace("-", "_"), data["name"]]
    if "set" in data:
        items.insert(1, data["set"].replace("-", "_"))
    return "{}.{}".format(CONFIG_DATA["base"], idName("_".join(items)))


def hasProperty(command):
    """Return if the command contains a property value name.

    :param command: The button command dictionary.
    :type command: dict

    :return: True, if the command contains a property value name
    :rtype: bool
    """
    return "valueName" in command and len(command["valueName"])


def matchString(string, searchString, minMatch):
    """Check, if the given string is a rough match to the search string.
    If the given number of characters match, return the search string.
    Otherwise, the original string is returned.

    :param: string: The string to match against the search string.
    :type string: str
    :param searchString: The string to match against.
    :type searchString: str
    :param minMatch: The number of characters which are needed for a
                     match.
    :type minMatch: int

    :return: The matched or unmatched string.
    :rtype: str
    """
    # If the string is longer than the search string by two characters
    # declare it as unmatched.
    if len(string) - 2 > len(searchString):
        return string

    count = 0
    for i in string:
        if i.lower() in searchString:
            count += 1
    if count >= minMatch and count <= len(searchString):
        return searchString
    return string


def correctString(string):
    """Correct typographic errors for the words 'string', 'true',
    'false'.

    :param: string: The string to correct.
    :type string: str

    :return: The corrected string.
    :rtype: str
    """
    result = matchString(string, "string", 3)
    if result == "string":
        return result
    result = matchString(string, "true", 3)
    if result == "true":
        return result
    result = matchString(string, "false", 3)
    if result == "false":
        return result
    return string


def stringToValue(string):
    """Return the value as the type defined by the given string.

    :param string: The string representation of the value.
    :type string: str

    :return: The typed value.
    :rtype: bool/int/float
    """
    # Spell-check the property value string.
    string = correctString(string)

    if string in ["true", "false"]:
        return string.title() == "True"
    elif len(string.split(".")) > 1:
        return float(string)
    elif string.lower() == "string":
        return "string"
    elif len(string.split(":")) > 1:
        return "enum"
    else:
        return int(string)


def listToEnumItemsString(items):
    """Convert the given list to a list of items for an enum property
    and return is as a string representation.

    :param items: The list of items to convert.
    :type items: list

    :return: The string representation of the enum item list.
    :rtype: str
    """
    enumItems = []
    for i in range(len(items)):
        label = items[i][0] if not len(items[i][1]) else ""
        enumItems.append('("{}", "{}", "{}", \'{}\', {})'.format(i,
                                                                 label,
                                                                 items[i][0],
                                                                 items[i][1],
                                                                 i))
    return "[{}]".format(",".join(enumItems))


class ToolProperty(object):
    """Class for the properties of a tool or set.

    Create a string representation for registering each property of
    the given tool dictionary and collect names, labels and types.
    """
    def __init__(self, data, group):
        """
        :param data: The dictionary which describes the command.
        :type data: dict
        :param group: The name of the group the command belongs to.
        :type group: str
        """
        self.data = data
        self.group = group

        self.labels = []
        self.rowCount = []

        self.names = []
        self.values = []
        self.callback = ""

        if hasProperty(data):
            # Get the property labels and row association.
            # In case of a property row the brackets are being removed.
            self.labels, self.rowCount = self.propertyLabels()
            # The list of unique property names for getting and setting
            # values.
            self.names = self.propertyName()
            # The values for the properties.
            self.values = [i.strip() for i in self.data["value"].rstrip(";").split(";")]
            # Create the name of the callback function if required.
            if "valueCallback" in self.data and self.data["valueCallback"]:
                self.callback = self.callbackName()

        properties = []
        propNames = []
        propLabels = []
        propTypes = []

        for i in range(len(self.names)):

            # ----------------------------------------------------------
            # Values
            # ----------------------------------------------------------

            valueItems = self.values[i].replace(" ", "").split(",")
            # The values can be split up to three elements: value, min,
            # max.
            # It's not necessary to always include all values.
            # Therefore, it's possible to have only a value, or a value
            # with a min setting.
            # But in order to include a max value a min value needs to
            # be given as well.
            value = stringToValue(valueItems[0]) if len(valueItems) else 0
            minValue = stringToValue(valueItems[1]) if len(valueItems) > 1 else None
            maxValue = stringToValue(valueItems[2]) if len(valueItems) > 2 else None

            valueString = ", default={}".format(value)
            minString = ""
            if minValue is not None:
                minString = ", min={}".format(minValue)
            maxString = ""
            if maxValue is not None:
                maxString = ", max={}".format(maxValue)

            # ----------------------------------------------------------
            # Property Type
            # ----------------------------------------------------------

            propString = ""
            if isinstance(value, bool):
                propString = "BoolProperty"
            elif isinstance(value, int):
                propString = "IntProperty"
            elif isinstance(value, float):
                propString = "FloatProperty"
            elif value == "string":
                propString = "StringProperty"
                valueString = ""
                minString = ""
                maxString = ""
            elif value == "enum":
                propString = "EnumProperty"
                items = valueItems[0].split(":")
                # Check, if one of the list items has a leading asterisk
                # which marks as the default.
                default = ""
                enumItems = []
                for j in range(len(items)):
                    # Split the enum string to get the icon if it's
                    # included.
                    enum, icon = self.enumData(items[j])

                    if enum.startswith("*"):
                        default = ', default="{}"'.format(j)
                        enum = enum[1:]
                        break

                    enumItems.append((enum, icon))

                valueString = ", items={}{}".format(listToEnumItemsString(enumItems), default)
                minString = ""
                maxString = ""

            label = self.labels[i][0]

            updateString = ""
            if label.startswith("!") and len(self.callback):
                updateString = ", update={}".format(self.callback)
                label = label[1:]

            if len(propString):
                properties.append('{}: bpy.props.{}(name="{}"{}{}{}{})'.format(self.names[i],
                                                                               propString,
                                                                               label,
                                                                               valueString,
                                                                               minString,
                                                                               maxString,
                                                                               updateString))
                propNames.append(self.names[i])
                propLabels.append(self.labels[i])
                propTypes.append(propString)

        # The list of property registration strings.
        self.properties = properties[:]
        # The list of property names for getting and setting values,
        # i.e. tool_shelf_groupName_toolName_buttonLabel.
        self.names = propNames[:]
        # The list of tuples with the labels and row association.
        self.labels = propLabels[:]
        # The list of property types.
        self.types = propTypes[:]

    def propertyLabels(self):
        """Return a list with all property labels contained in the given
        tool configuration.

        :return: The list of tuples with the property labels and the row
                 assignment. A list with the number of properties per
                 row.
        :rtype: list(tuple(str, bool)), list(int)
        """
        labels = []
        numLabels = []

        isRow = False
        count = 0
        for label in self.data["valueName"].rstrip(";").split(";"):
            if label[0] in ["[", "("] and not isRow:
                isRow = True
            elif label[-1] in ["]", ")"] and isRow:
                isRow = False
                numLabels.append(count + 1)
                count = 0
            expandEnum = True if label[0] == "<" else False

            if isRow:
                count += 1

            labels.append((re.sub(BRACKETS, "", label), isRow, expandEnum))

        return labels, numLabels

    def propertyName(self):
        """Return a unique property name for each property of a tool
        item.

        :return: The list of property names.
        :rtype: list(str)
        """
        nameList = []
        for label in [label for label, row, expandEnum in self.labels]:
            items = [self.group, self.data["name"], label]
            # If the property belongs to a set remove the tool name
            # because only the set names needs to be included.
            # This is important to make the property available to all
            # buttons of the set.
            if "set" in self.data:
                items.pop(1)
                items.insert(1, self.data["set"])
            name = "_".join(items)
            nameList.append("{}_value".format(idName(name.replace("-", "_"))))

        return nameList

    def callbackName(self):
        """Return a unique name for the property callback function.
        item.

        :return: The name of the callback function.
        :rtype: str
        """
        items = [self.group, self.data["name"]]
        if "set" in self.data:
            items = [self.group, self.data["set"]]
        name = "_".join(items)
        return "{}_callback".format(idName(name.replace("-", "_")))

    def initCallback(self):
        """Use the command string from the tool to create a property
        callback function.

        :return: The callback function as a string to execute.
        :rtype: str
        """
        execute = ["def {}(self, context):".format(self.callback)]
        cmd = replacePropertyPlaceholder(self.data["command"], self.names)
        execute.append("{}".format(cmd.replace("\n", "\n    ")))
        return "\n    ".join(execute)

    def isRow(self, index):
        """Return, if the property at the given index belongs to a row.

        :param index: The index of the property.
        :type index: int

        :return: True, if the property belongs to a row of properties.
        :rtype: bool
        """
        return self.labels[index][1]

    def typeString(self, index):
        """Return the type of property at the given index.

        :param index: The index of the property.
        :type index: int

        :return: The type of the property as a string.
        :rtype: str
        """
        return self.types[index].replace("Property", "").lower()

    def expandEnum(self, index):
        """Return, if the enum property should be expanded to appear as
        a radio button collection.

        :param index: The index of the property.
        :type index: int

        :return: True, if the enum should be expanded.
        :rtype: bool
        """
        return self.labels[index][2]

    def enumData(self, enumString):
        """Return the name and icon for the given enum property item.

        :param enumString: The string of the enum item as defined in the
                           configuration. This can only be the enum name
                           or the name and icon name, separated by the
                           @ symbol.
        :type enumString: str

        :return: A tuple with the name of the enum item and the icon.
        :rtype: tuple(str, str)
        """
        enum = ""
        icon = ""
        itemPair = enumString.split("@")
        if len(itemPair) > 1:
            enum, icon = itemPair
        else:
            enum = enumString
        return enum, icon


def replacePropertyPlaceholder(cmdString, propNames):
    """Replace the placeholder to access the tool or set property with
    the reference to the property.

    :param cmdString: The command string of the button.
    :type cmdString: str
    :param propNames: The list of property names.
    :type propNames: list(str)

    :return: The replaced command string.
    :rtype: str
    """
    for i in range(len(propNames)):
        propString = "context.scene.tool_shelf.{}".format(propNames[i])
        if len(propNames) == 1:
            # Starting with version 0.10.0 the placeholder for a single
            # property can now also be PROP1 for consisteny.
            # Even though PROP is still maintained for compatibility.
            placeholder = "PROP"
            if "PROP1" in cmdString:
                placeholder = "PROP1"
        else:
            placeholder = "PROP{}".format(i + 1)
        cmdString = cmdString.replace(placeholder, propString)

    return cmdString


def getOperatorClassName(data, group):
    """Return the class name for the given operator.

    :param data: The dictionary which describes the command.
    :type data: dict
    :param group: The name of the group the command belongs to.
    :type group: str

    :return: The idname string for the operator.
    :rtype: str
    """
    name = "Tool_Shelf_{}_{}".format(group.title(), re.sub(ALPHANUM, '', data["name"].title()))
    return "OBJECT_OT_{}".format(name)


def buildOperatorClass(data, group, propCls):
    """Construct and register an operator class for the given command.

    :param data: The dictionary which describes the command.
    :type data: dict
    :param group: The name of the group the command belongs to.
    :type group: str
    :param propCls: The class instance for the properties of a command.
    :type propCls: class instance

    :return: The operator class.
    :rtype: class
    """
    # Build the execute method for the operator up front so that it can
    # be referenced when the class gets build.
    execute = ["def execute(self, context):"]

    classItems = (bpy.types.Operator, )

    # If the operator contains a property register it within the
    # operator.
    execute.extend(propCls.properties)

    # Add the command.
    if isAddOnToggle(data["command"]):
        execute.append("{}".format(inspect.getsource(toggleAddOn).replace("\n", "\n    ")))
        execute.append(data["command"])
    # If no property callback is defined add the command to the
    # operator.
    elif not len(propCls.callback):
        cmd = replacePropertyPlaceholder(data["command"], propCls.names)

        # If the file browser should be included in the operator add the
        # in-built mix-in class ImportHelper to open the file browser
        # and get access to the selected path.
        # Also replace the placeholder with the call to open the file
        # browser.
        if "BROWSER_GET_FILE" in cmd:
            classItems = (bpy.types.Operator, ImportHelper)
            cmd = cmd.replace("BROWSER_GET_FILE", "self.properties.filepath")

        execute.append("{}".format(cmd.replace("\n", "\n    ")))

    execute.append("return {'FINISHED'}")

    # Register the method within the module.
    module = types.ModuleType("operatorExecute")
    # print("\n    ".join(execute))
    exec("\n    ".join(execute), module.__dict__)

    # Create the class.
    toolClass = type(getOperatorClassName(data, group),
                     classItems,
                     {"bl_idname": getIdName(data, group),
                      "bl_label": data["name"],
                      "bl_description": data["tooltip"],
                      "bl_options": {'REGISTER', 'UNDO'},
                      "execute": module.execute})

    return toolClass


def readConfiguration(configData):
    """Evaluate the configuration file and store the group data in the
    designated public lists.

    :param configData: The configuration dictionary from the json file.
    :type configData: dict
    """
    # Cancel if no groups have been defined.
    if "groups" not in configData:
        return

    # For each defined group in the configuration file build the classes
    # for all contained buttons and set up a dictionary for every button
    # containing the operator idname and the related icon.
    for group in configData["groups"]:
        toolData = []
        # Process each button/command in the current group.
        for cmd in group["commands"]:
            # Create a copy of the command so that the added data isn't
            # reflected in the configuration data.
            cmd = copy.deepcopy(cmd)

            # Get either the single command for the button or in case of
            # a set the list of contained commands.
            if "set" not in cmd:
                commands = [cmd]
            else:
                commands = cmd["commands"]

            # Create the property for registering.
            # Also, get all property related data.
            # The properties are defined per tool because they need to
            # be available to each operator class but for a set they
            # only need to be registered once.
            toolProp = ToolProperty(commands[0], group["name"])
            PROPERTIES.extend(toolProp.properties)
            if len(toolProp.callback):
                CALLBACKS.append(toolProp.initCallback())

            # Build the operators for each tool or tool group.
            toolItem = []
            for cmdItem in commands:
                CMD_CLASSES.append(buildOperatorClass(cmdItem, group["name"], toolProp))

                addOnName = ""
                # If the complete toggleAddOn("NAME") command is given
                # strip everything away but the add-on name.
                if isAddOnToggle(cmdItem["command"]):
                    addOnName = cmdItem["command"][13:-2]

                # If the command includes an icon, add it to the list
                # of icons to be added to the preview collection.
                if cmdItem["icon"]:
                    ICONS.append(cmdItem["icon"])

                # Collect the operator data in a dictionary which is
                # used to set up the buttons.
                cmdItem["id"] = getIdName(cmdItem, group["name"])
                cmdItem["addOn"] = addOnName
                cmdItem["property"] = toolProp
                toolItem.append(cmdItem)

            if len(toolItem) == 1:
                toolData.extend(toolItem)
            else:
                toolData.append(toolItem)

        if "expand" not in group:
            group["expand"] = False

        # Store the collected data per group along with the group name.
        GROUPS.append({"name": group["name"], "toolData": toolData, "expand": group["expand"]})


readConfiguration(CONFIG_DATA)

# Initialize the property callbacks.
for callback in CALLBACKS:
    exec(callback)


# ----------------------------------------------------------------------
# 3. Store the icons in the preview collection.
# ----------------------------------------------------------------------

def iconIdName(image):
    """Return the icon id name for the given image.

    :param image: The name of the image for the icon.
    :type image: str

    :return: The icon id name to be used for the preview collection.
    :rtype: str
    """
    return "icon_{}".format(image.split(".")[0])


def registerIcons(icons, filePath):
    """Register the icons contained in the configuration and add them
    to a new preview collection which then can be referenced by the
    panel classes.

    :param icons: The list of image files to be registered.
    :type icons: list(str)
    :param filePath: The absolute file path of the icons folder.
    :type filePath: str

    :return: A new preview collection with the icons.
    :rtype: bpy.utils.previews
    """
    # Setup the preview collection for giving access to the icon.
    pcoll = bpy.utils.previews.new()
    # Parse every icon which is associated with a button and test if
    # it's a valid file. Add it to the preview collection.
    for icon in icons:
        if len(icon) and not icon.startswith("'") and icon.split(".")[-1] == "png":
            imagePath = os.path.join(filePath, icon)
            if os.path.exists(imagePath):
                # Try to add the icon to the preview collection in case
                # the image already exists.
                try:
                    pcoll.load(iconIdName(icon), imagePath, 'IMAGE', True)
                except (Exception,):
                    pass

    return pcoll


ICON_COLLECTION["icons"] = registerIcons(ICONS, ICONS_PATH)


# ----------------------------------------------------------------------
# 4. Property Group
# Globally define all properties for adding new buttons and commands.
# ----------------------------------------------------------------------

def clearFields(context):
    """Clear all fields.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    tool_shelf.name_value = ""
    tool_shelf.cmd_value = ""
    tool_shelf.tip_value = ""
    tool_shelf.image_value = ""
    tool_shelf.image_only_value = False
    tool_shelf.new_set_value = False
    tool_shelf.expand_value = False
    tool_shelf.addon_value = False
    tool_shelf.set_value = ""
    tool_shelf.column_value = 2
    tool_shelf.property_value = False
    tool_shelf.property_name_value = ""
    tool_shelf.property_value_value = ""
    tool_shelf.property_callback_value = False


def groupChanged(self, context):
    """Callback for when the group enum property selection changes.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    # Reset the tool selection.
    tool_shelf.button_value = 'NONE'
    clearFields(context)
    # Clear all fields in edit mode.
    if tool_shelf.mode_value == 'EDIT':
        groupIndex = getGroupIndex(CONFIG_DATA, tool_shelf.group_value)
        if groupIndex is not None:
            tool_shelf.name_value = tool_shelf.group_value
            tool_shelf.expand_value = CONFIG_DATA["groups"][groupIndex]["expand"]


def toolChanged(self, context):
    """Callback for when the tool enum property selection changes.
    Populates the fields in edit mode to show the current command
    definition.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    if tool_shelf.mode_value == 'EDIT':
        clearFields(context)

        groupIndex = getGroupIndex(CONFIG_DATA, tool_shelf.group_value)
        if groupIndex is None:
            return

        toolIndex = getToolIndex(CONFIG_DATA, tool_shelf.button_value, groupIndex)
        if toolIndex is not None:
            command = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]

            # Single tool
            if "name" in command:
                tool_shelf.name_value = command["name"]
                tool_shelf.cmd_value = command["command"]
                tool_shelf.tip_value = command["tooltip"]
                tool_shelf.image_value = command["icon"]
                tool_shelf.image_only_value = command["iconOnly"]
                tool_shelf.addon_value = isAddOnToggle(command["command"])
                useProp = False
                propName = ""
                propValue = ""
                propCallbackValue = False
                if hasProperty(command):
                    useProp = True
                    propName = command["valueName"]
                    propValue = command["value"]
                    propCallbackValue = command["valueCallback"] if "valueCallback" in command else False
                tool_shelf.property_value = useProp
                tool_shelf.property_name_value = propName
                tool_shelf.property_value_value = propValue
                tool_shelf.property_callback_value = propCallbackValue
            # Tool set
            else:
                tool_shelf.new_set_value = True
                tool_shelf.name_value = ";".join([c["name"] for c in command["commands"]])
                tool_shelf.cmd_value = ";".join([c["command"] for c in command["commands"]])
                tool_shelf.tip_value = command["commands"][0]["tooltip"]
                tool_shelf.image_value = ";".join([c["icon"] for c in command["commands"]])
                tool_shelf.image_only_value = command["commands"][0]["iconOnly"]
                tool_shelf.set_value = command["set"]
                tool_shelf.column_value = command["columns"]
                useProp = False
                propName = ""
                propValue = ""
                propCallbackValue = False
                if hasProperty(command):
                    useProp = True
                    propName = command["valueName"]
                    propValue = command["value"]
                    propCallbackValue = command["valueCallback"] if "valueCallback" in command else False
                tool_shelf.property_value = useProp
                tool_shelf.property_name_value = propName
                tool_shelf.property_value_value = propValue
                tool_shelf.property_callback_value = propCallbackValue
        # Group
        else:
            tool_shelf.name_value = tool_shelf.group_value


def addOnChanged(self, context):
    """Callback for when the add-on enum property selection changes.
    Populates the fields in add mode with the selected add-on name.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    tool_shelf.name_value = ""
    tool_shelf.cmd_value = ""
    tool_shelf.tip_value = ""
    # To retrieve the add-on name for the name field get the list of
    # tuples for all installed add-ons and check which one matches the
    # current selection. Since the label is the second element in the
    # tuple and cannot be queried directly the search must go by module
    # name which is also the value of the enum item.
    if tool_shelf.addon_list_value != 'NONE':
        items = getAddOnItems()
        for item in items:
            if item is not None and item[0] == tool_shelf.addon_list_value:
                tool_shelf.name_value = item[1]
                break
        tool_shelf.cmd_value = tool_shelf.addon_list_value


def importFileChanged(self, context):
    """Callback for when the import file path property changes.
    Reads the content of the selected configuration file and populates
    the import enum property with the contained commands.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf
    CONFIG_DATA_IMPORT.config = jsonRead(tool_shelf.file_value)
    if not len(CONFIG_DATA_IMPORT.config):
        tool_shelf.import_value = 'NONE'


def groupItems(self, context):
    """Callback for populating the enum property with the group names.

    :param context: The current context.
    :type context: bpy.context
    """
    # The list of enum items representing the available groups.
    groups = [('NONE', "––– Select –––", "Select a group")]

    for group in CONFIG_DATA["groups"]:
        groups.append((group["name"], group["name"], ""))

    return groups


def toolItems(self, context):
    """Callback for populating the enum property with the tool names
    based on the current group selection.

    :param context: The current context.
    :type context: bpy.context
    """
    tools = [('NONE', "––– Select –––", "")]

    tool_shelf = context.scene.tool_shelf

    if tool_shelf.group_value != 'NONE':
        groupIndex = getGroupIndex(CONFIG_DATA, tool_shelf.group_value)
        commands = CONFIG_DATA["groups"][groupIndex]["commands"]
        for item in commands:
            if "set" not in item:
                tools.append((item["name"], item["name"], ""))
            else:
                tools.append((item["set"], item["set"], ""))

    return tools


def modeItems(self, context):
    """Return the items for the modes enum property.

    :param context: The current context.
    :type context: bpy.context

    :return: A tuple with the enum items.
    :rtype: tuple()
    """
    return (('ADD', "", "Add a new group or tool", 'ADD', 0),
            ('REMOVE', "", "Delete an existing group or button", 'REMOVE', 1),
            ('EDIT', "", "Overwrite the command of an existing button.\nUse the asterisk * "
             "symbol to keep existing settings", 'GREASEPENCIL', 2),
            ('REORDER', "", "Reorder groups and buttons", 'LINENUMBERS_ON', 3),
            ('VIEW', "", "Display a button command in the text editor", 'FILE', 4),
            ('IMPORT', "", "Import a group or tool from a configuration file", 'IMPORT', 5))


def getAddOnItems():
    """Return a list of installed add-ons for the add-on enum property.
    The list contains a tuple for each entry with the value, label and
    tooltip.

    This method is exists standalone to be able to get the add-on data
    independent of the enum property callback.

    :return: A list with tuples representing the enum property items.
    :rtype: list(tuple(str, str, str))
    """
    addOns = [('NONE', "––– Select –––", "")]
    lastCategory = ""
    # Go through all installed add-ons and only add the ones which are
    # not on the blacklist of incompatible add-ons.
    for item in getAddOns():
        if item["name"] not in ADD_ON_BLACKLIST:
            # Add a separator whenever a new category starts.
            # Alternatively it would have been better to be able to add
            # a category divider in form of ––– Category ––– but for
            # some reason this results in unicode characters showing up
            # as list items.
            if item["category"] != lastCategory:
                addOns.append(None)
                lastCategory = item["category"]
            addOns.append((item["name"], item["label"], ""))
    return addOns


def addOnItems(self, context):
    """Callback for populating the enum property with the add-on names.

    :param context: The current context.
    :type context: bpy.context

    :return: A list with tuples representing the enum property items.
    :rtype: list(tuple(str, str, str))
    """
    return getAddOnItems()


def importItems(self, context):
    """Callback for populating the enum property with the tool names
    based on the selected configuration file for the import.

    :param context: The current context.
    :type context: bpy.context
    """
    tools = [('NONE', "––– Select –––", "")]

    tool_shelf = context.scene.tool_shelf

    # If the path to the configuration file is valid get its data.
    # This is necessary because when the script gets reloaded in
    # mid-action while an item in the list is selected an error gets
    # reported that the last list selection cannot be found anymore.
    # Therefore, it's best to keep the list updated.
    CONFIG_DATA_IMPORT.config = jsonRead(tool_shelf.file_value)

    # Cancel if no groups have been defined.
    if "groups" not in CONFIG_DATA_IMPORT.config:
        return tools

    # Build the enum items from the config file.
    # To visually separate groups and tools the latter are indented by
    # two white spaces.
    # In order to be able to find the tool to import, and it's
    # containing group the item identifier contains the group and tool
    # name separated by three underscores.
    for group in CONFIG_DATA_IMPORT.config["groups"]:
        tools.append((group["name"], group["name"], ""))
        for cmd in group["commands"]:
            toolName = cmd["name"] if "set" not in cmd else cmd["set"]
            tools.append(("{}___{}".format(group["name"], toolName), "  {}".format(toolName), ""))

    return tools


class ImportData(object):
    """Class for handling the data of the import configuration because
    using a public dictionary doesn't work in this case because even
    though the file has been read correctly and the dictionary is valid
    importItems() still gets an empty dictionary.
    """
    def __init__(self):
        """Define the configuration variable"""
        self.config = {}


CONFIG_DATA_IMPORT = ImportData()


class Tool_Shelf_Properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    mode_value: bpy.props.EnumProperty(name="Mode",
                                       description=ANN_MODE,
                                       items=modeItems)
    newGroup = False
    if not len(CONFIG_DATA["groups"]):
        newGroup = True
    new_group_value: bpy.props.BoolProperty(name="New Group",
                                            description=ANN_NEW_GROUP,
                                            default=newGroup)
    expand_value: bpy.props.BoolProperty(name="Auto Expand",
                                         description=ANN_EXPAND,
                                         default=False)
    addon_value: bpy.props.BoolProperty(name="Add-on Toggle",
                                        description=ANN_TOGGLE_ADDON,
                                        default=False)
    new_set_value: bpy.props.BoolProperty(name="New Set",
                                          description=ANN_NEW_SET,
                                          default=False)
    set_value: bpy.props.StringProperty(name="Set Name",
                                        description=ANN_SET_NAME,
                                        default="")
    column_value: bpy.props.IntProperty(name="Row Buttons",
                                        description=ANN_SET_COLUMNS,
                                        min=1,
                                        max=10,
                                        default=2)
    name_value: bpy.props.StringProperty(name="Name",
                                         description=ANN_NAME,
                                         default="")
    cmd_value: bpy.props.StringProperty(name="Command",
                                        description=ANN_COMMAND,
                                        default="")
    tip_value: bpy.props.StringProperty(name="Tooltip",
                                        description=ANN_TOOLTIP,
                                        default="")
    image_value: bpy.props.StringProperty(name="Icon",
                                          description=ANN_ICON,
                                          default="")
    image_only_value: bpy.props.BoolProperty(name="Icon Only",
                                             description=ANN_ICON_ONLY,
                                             default=False)
    property_value: bpy.props.BoolProperty(name="Property",
                                           description=ANN_PROPERTY,
                                           default=False)
    property_name_value: bpy.props.StringProperty(name="Name",
                                                  description=ANN_PROPERTY_NAME,
                                                  default="")
    property_value_value: bpy.props.StringProperty(name="Value",
                                                   description=ANN_PROPERTY_VALUE,
                                                   default="")
    property_callback_value: bpy.props.BoolProperty(name="Command As Callback",
                                                    description=ANN_PROPERTY_CALLBACK,
                                                    default=False)
    group_value: bpy.props.EnumProperty(name="Group",
                                        description=ANN_GROUP,
                                        items=groupItems,
                                        update=groupChanged)
    button_value: bpy.props.EnumProperty(name="Tool",
                                         description=ANN_TOOL,
                                         items=toolItems,
                                         update=toolChanged)
    addon_list_value: bpy.props.EnumProperty(name="Add-on",
                                             description=ANN_ADDON,
                                             items=addOnItems,
                                             update=addOnChanged)
    file_value: bpy.props.StringProperty(name="Import",
                                         description=ANN_IMPORT_FILE,
                                         subtype='FILE_PATH',
                                         update=importFileChanged)
    import_value: bpy.props.EnumProperty(name="Command",
                                         description=ANN_IMPORT_ITEM,
                                         items=importItems)

    # Add the command properties.
    for prop in PROPERTIES:
        # print("Registering property: {}".format(prop))
        exec(prop)


# ----------------------------------------------------------------------
# 5. Create the tool panel and sub panels for included groups.
# Before creating the sub panels the parent panel and containing panel
# need to exist.
# ----------------------------------------------------------------------

class VIEW3D_PT_ToolShelf(bpy.types.Panel):
    """Create the tool panel in the ui space defined in the
    configuration file.

    This class is not included in the overall registration because it
    only acts as a container to make the main and sub panels work.
    """
    bl_space_type = CONFIG_DATA["space"]
    bl_region_type = CONFIG_DATA["region"]
    bl_category = CONFIG_DATA["category"]
    bl_label = CONFIG_DATA["label"]


class VIEW3D_PT_ToolShelf_Main(VIEW3D_PT_ToolShelf):
    """Create the main tool panel area which contains all sub panels.

    This class gets passed the main tool panel but has no further
    functionality because it only serves as a parent for the sub panels.
    """
    bl_label = CONFIG_DATA["name"]

    def draw(self, context):
        """Draw the panel and it's properties.

        This method doesn't contain any drawing functionality because
        of it's purpose to be the parent for the sub panels.

        :param context: The current context.
        :type context: bpy.context
        """
        pass


class VIEW3D_PT_ToolShelf_Sub(VIEW3D_PT_ToolShelf):
    """Create the first sub panel which contains all properties for
    creating new buttons and commands.
    """
    # For the sub panel it's important to reference the parent panel.
    bl_parent_id = "VIEW3D_PT_ToolShelf_Main"
    bl_label = "Setup"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        tool_shelf = context.scene.tool_shelf

        # Get the display mode.
        mode = tool_shelf.mode_value
        label = "Add Tool"
        nameLabel = "Name"
        commandLabel = "Command"
        iconLabel = "Icon"

        # Set the global display style of the properties.
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False  # No animation.

        # Layout the mode enum values as a button row by setting the
        # expand flag to True.
        self.layout.prop(tool_shelf, "mode_value", expand=True)

        # Set the column alignment for a nicer placement of the fields.
        col = self.layout.column(align=True)

        if mode in ['ADD', 'EDIT']:
            if mode == 'ADD':
                col.prop(tool_shelf, "new_group_value")

            if tool_shelf.new_group_value and mode == 'ADD':
                col.prop(tool_shelf, "name_value")
                col.prop(tool_shelf, "group_value", text="After Group")
                col.prop(tool_shelf, "expand_value")
                label = "Add Group"
            else:
                col.prop(tool_shelf, "group_value")
                if mode == 'ADD':
                    col.prop(tool_shelf, "button_value", text="After Tool")
                else:
                    col.prop(tool_shelf, "button_value")
                    label = "Edit"

                showSet = False
                setLabel = "New Set"
                if mode == 'EDIT':
                    if tool_shelf.button_value != 'NONE':
                        setLabel = "Edit Set"
                        showSet = True
                else:
                    showSet = True

                if showSet:
                    col.prop(tool_shelf, "new_set_value", text=setLabel)

                if tool_shelf.new_set_value:
                    col.prop(tool_shelf, "set_value")
                    col.prop(tool_shelf, "column_value")
                    nameLabel = "Labels"
                    commandLabel = "Commands"
                    iconLabel = "Icons"
                elif mode == 'ADD':
                    col.prop(tool_shelf, "addon_value")
                    if mode == 'ADD' and tool_shelf.addon_value:
                        col.prop(tool_shelf, "addon_list_value")

                # Begin a new section.
                col = self.layout.column(align=True)

                col.prop(tool_shelf, "name_value", text=nameLabel)

                if mode == 'EDIT' and tool_shelf.button_value == 'NONE':
                    col.prop(tool_shelf, "expand_value")

                if mode == 'ADD' or (mode == 'EDIT' and tool_shelf.button_value != 'NONE'):
                    col.prop(tool_shelf, "cmd_value", text=commandLabel)
                    col.prop(tool_shelf, "tip_value")
                    if not tool_shelf.addon_value:
                        col.prop(tool_shelf, "image_value", text=iconLabel)
                        col.prop(tool_shelf, "image_only_value")
                        col.prop(tool_shelf, "property_value")
                        if tool_shelf.property_value:
                            col.prop(tool_shelf, "property_name_value")
                            col.prop(tool_shelf, "property_value_value")
                            col.prop(tool_shelf, "property_callback_value")
        elif mode == 'IMPORT':
            col.prop(tool_shelf, "file_value")
            if tool_shelf.file_value:
                col.prop(tool_shelf, "import_value")
                col.prop(tool_shelf, "group_value")
            label = "Import"
        else:
            col.prop(tool_shelf, "group_value")
            col.prop(tool_shelf, "button_value")
            if mode == 'REMOVE':
                label = "Delete"
            elif mode == 'REORDER':
                row = self.layout.row(align=True)
                row.operator("view3d.tool_shelf_item_up", text="Move Up")
                row.operator("view3d.tool_shelf_item_down", text="Move Down")
                label = "Apply Order"
            elif mode == 'VIEW':
                label = "View Command"

        # Call the operator with the current settings.
        op = self.layout.operator("view3d.tool_shelf", text=label)
        op.mode_value = tool_shelf.mode_value
        op.new_group_value = tool_shelf.new_group_value
        op.expand_value = tool_shelf.expand_value
        op.new_set_value = tool_shelf.new_set_value
        op.set_value = tool_shelf.set_value
        op.column_value = tool_shelf.column_value
        op.addon_value = tool_shelf.addon_value
        op.name_value = tool_shelf.name_value
        op.cmd_value = tool_shelf.cmd_value
        op.tip_value = tool_shelf.tip_value
        op.image_value = tool_shelf.image_value
        op.image_only_value = tool_shelf.image_only_value
        op.group_value = tool_shelf.group_value
        op.button_value = tool_shelf.button_value
        op.file_value = tool_shelf.file_value
        op.import_value = tool_shelf.import_value
        op.property_value = tool_shelf.property_value
        op.property_name_value = tool_shelf.property_name_value
        op.property_value_value = tool_shelf.property_value_value
        op.property_callback_value = tool_shelf.property_callback_value


def buildPanelProperty(button, parent, exists):
    """Return the layout elements for the property included in the
    tool.

    :param button: The tool dictionary.
    :type button: dict
    :param parent: The parent layout.
    :type parent: str
    :param exists: False, if the property hasn't been created yet.
    :type exists: bool

    :return: A tuple with the list of strings to create the property,
             the current parent layout and if the property has been
             created.
    :rtype: tuple(list(str), str, bool)
    """
    draw = []

    prop = button["property"]
    count = len(prop.labels)

    # If the tool includes a property use a box layout to visually
    # combine the controls.
    if count and not exists:
        # If the current tool doesn't belong to a set add the box
        # layout.
        # The box layout for a set has been set up before iterating
        # through the button commands.
        if "set" not in button:
            draw.append("box = self.layout.box()")
            draw.append("col = box.column(align=True)")
            parent = "col"

        isRow = False
        rowCountIndex = 0
        text = ""
        parentPrev = parent
        for i in range(count):
            # If the buttons should be aligned in a row start a new one.
            if prop.isRow(i) and not isRow:
                draw.append("row = {}.row(align=True)".format(parent))
                parent = "row"
                isRow = True
                # Get the number of properties in the current row.
                # This defines if the labels are added or discarded.
                rowCount = prop.rowCount[rowCountIndex]

                # If there are more than two properties in a row remove
                # the labels to safe space, except for checkboxes.
                if prop.typeString(i) != "bool" and rowCount > 2:
                    text = ', text=""'

            # If the property is an enum which should be expanded start
            # a new row.
            expandEnum = ""
            if prop.expandEnum(i):
                draw.append("row = {}.row(align=True)".format(parent))
                parent = "row"
                expandEnum = ", expand=True"

            draw.append('{}.prop(tool_shelf, "{}"{}{})'.format(parent,
                                                               prop.names[i],
                                                               text,
                                                               expandEnum))

            # If the current button was the last in the row end the row
            # and reset the parent layout.
            if not prop.isRow(i) and isRow:
                parent = parentPrev
                text = ""
                isRow = False
                rowCountIndex += 1

            # Reset to the parent layout after the expanded enum.
            if prop.expandEnum(i):
                parent = parentPrev

        # Start a new row after the property if the buttons belong to a
        # set.
        if "set" in button:
            draw.append("row = col.row(align=True)")

        # Add the row layout for a set to align the buttons accordingly.
        # This has been skipped before adding the properties.
        if "set" in button:
            draw.append("row = col.row(align=True)")
            parent = "row"

        exists = True

    return draw, parent, exists


def buildPanelClass(name, data, index, expand):
    """Build the expandable sub panel for the given tool group.

    :param name: The name of the sub panel/group.
    :type name: str
    :param data: The list of tool dictionaries, containing the operator
                 idname and icon for each button.
    :type data: list(dict)
    :param index: The index of the group used for defining a unique
                  panel class name.
    :type index: int
    :param expand: True, if the group should be expanded by default.
    :type expand: bool

    :return: The class of the sub panel.
    :rtype: class
    """
    # Get a reference to the preview collection to access the icons.
    pcoll = ICON_COLLECTION["icons"]

    # Build the draw method for the panel up front so that it can be
    # referenced when the class gets build.
    draw = ["def draw(self, context):"]
    draw.append("tool_shelf = context.scene.tool_shelf")
    draw.append("self.layout.use_property_split = True")
    draw.append("self.layout.use_property_decorate = False")

    for item in data:
        parent = "self.layout"
        # For single buttons the item is a dictionary.
        # If the item is a tool set it's a list of dictionaries.
        if isinstance(item, dict):
            buttons = [item]
        else:
            buttons = item[:]
            draw.append("box = self.layout.box()")
            draw.append("box.label(text='{}')".format(buttons[0]["set"]))
            draw.append("col = box.column(align=True)")

            # If a set contains properties skip the row layout until
            # after the properties have been created, so that these are
            # placed in a column.
            if len(buttons[0]["property"].labels):
                parent = "col"
            else:
                draw.append("row = col.row(align=True)")
                parent = "row"

        lastRow = 0
        propertyAdded = False

        for button in buttons:

            prop = button["property"]

            # In case of a tool set add a new row to the layout when the
            # defined row number increases.
            if "row" in button and button["row"] > lastRow:
                draw.append("row = col.row(align=True)")
                lastRow = button["row"]

            # Create the properties.
            lines, parent, propertyAdded = buildPanelProperty(button, parent, propertyAdded)
            draw.extend(lines)

            # Check, if the icon is a default icon, an image or a
            # unicode string.
            labelSymbol, button["icon"] = filterIcon(button["icon"])

            if not len(prop.callback):

                # ------------------------------------------------------
                # No icon or add-on button.
                # ------------------------------------------------------
                if not len(button["icon"]):
                    # Add a simple button with no icon.
                    if not len(button["addOn"]):
                        label = ""
                        if len(labelSymbol):
                            label = ", text='{}'".format(labelSymbol)
                        elif button["iconOnly"]:
                            label = ", text=''"
                        draw.append("{}.operator('{}'{})".format(parent, button["id"], label))

                    # In case of an add-on toggle button the icon
                    # depends on the loaded state of the add-on
                    else:
                        draw.append("import addon_utils")
                        draw.append("checkBox = 'CHECKBOX_DEHLT'")
                        draw.append('enabled, loaded = addon_utils.check("{}")'.format(button["addOn"]))
                        draw.append("if loaded:")
                        draw.append("    checkBox = 'CHECKBOX_HLT'")
                        draw.append("{}.operator('{}', icon='{{}}'.format(checkBox))".format(parent, button["id"]))
                # ------------------------------------------------------
                # Icon button.
                # ------------------------------------------------------
                else:
                    label = ""
                    if button["iconOnly"]:
                        label = ", text=''"

                    # Default icon
                    if button["icon"].startswith("'"):
                        draw.append("{}.operator('{}'{}, icon={})".format(parent,
                                                                          button["id"],
                                                                          label,
                                                                          button["icon"]))
                    # Custom icon
                    else:
                        # Get the icon id related to the image from the
                        # preview collection.
                        icon_id = pcoll[iconIdName(button["icon"])].icon_id
                        draw.append("{}.operator('{}', icon_value={})".format(parent,
                                                                              button["id"],
                                                                              label,
                                                                              icon_id))

    # If no buttons are defined, which is the case when a new group has
    # just been added, add pass to the method to make it valid.
    if not len(data):
        draw.append("pass")

    # Register the method within the module.
    module = types.ModuleType("panelDraw")
    exec("\n    ".join(draw), module.__dict__)
    # print("\n    ".join(draw))

    # Define the class name based on the group index.
    clsName = "VIEW3D_PT_ToolShelf_Sub_{}".format(index)

    # Define the panel options.
    options = {"bl_parent_id": "VIEW3D_PT_ToolShelf_Main"}
    options["bl_label"] = name
    if not expand:
        options["bl_options"] = {"DEFAULT_CLOSED"}
    options["draw"] = module.draw

    # Create the class.
    toolClass = type(clsName,
                     (VIEW3D_PT_ToolShelf, ),
                     options)

    return toolClass


def buildGroupPanels():
    """Construct a sub panel for each group and add the related buttons.
    """
    for i in range(len(GROUPS)):
        CMD_CLASSES.append(buildPanelClass(GROUPS[i]["name"],
                                           GROUPS[i]["toolData"],
                                           i,
                                           GROUPS[i]["expand"]))


def filterIcon(icon):
    """Check, if the icon is a default icon, an image or a unicode
    character.

    In case of a unicode character no image is returned so that the
    button gets drawn without an icon but rather using the unicode
    character as a label.

    :param icon: The image string contained in the dictionary for a
                 button.
    :type icon: str

    :return: A tuple with the button label in case of a unicode
             character and the image for the button icon.
    :rtype: tuple(str, str)
    """
    if len(icon):
        if icon.startswith("'") or icon.split(".")[-1] == "png":
            return "", icon
        else:
            return icon, ""
    return "", ""


buildGroupPanels()


# ----------------------------------------------------------------------
# 6. Set up the operator for adding new buttons.
# ----------------------------------------------------------------------

class TOOLSHELF_OT_Editor(bpy.types.Operator):
    """Operator class for the tool.
    """
    bl_idname = "view3d.tool_shelf"
    bl_label = "Tool Shelf"
    bl_description = "Execute the current mode"

    mode_value: bpy.props.EnumProperty(name="Mode",
                                       description=ANN_MODE,
                                       items=modeItems)
    new_group_value: bpy.props.BoolProperty(name="New Group",
                                            description=ANN_NEW_GROUP,
                                            default=False)
    expand_value: bpy.props.BoolProperty(name="Auto Expand",
                                         description=ANN_EXPAND,
                                         default=False)
    addon_value: bpy.props.BoolProperty(name="Add-on Toggle",
                                        description=ANN_TOGGLE_ADDON,
                                        default=False)
    new_set_value: bpy.props.BoolProperty(name="New Set",
                                          description=ANN_NEW_SET,
                                          default=False)
    set_value: bpy.props.StringProperty(name="Set Name",
                                        description=ANN_SET_NAME,
                                        default="")
    column_value: bpy.props.IntProperty(name="Row Buttons",
                                        description=ANN_SET_COLUMNS,
                                        min=1,
                                        max=10,
                                        default=2)
    name_value: bpy.props.StringProperty(name="Name",
                                         description=ANN_NAME,
                                         default="")
    cmd_value: bpy.props.StringProperty(name="Command",
                                        description=ANN_COMMAND,
                                        default="")
    tip_value: bpy.props.StringProperty(name="Tooltip",
                                        description=ANN_TOOLTIP,
                                        default="")
    image_value: bpy.props.StringProperty(name="Icon",
                                          description=ANN_ICON,
                                          default="")
    image_only_value: bpy.props.BoolProperty(name="Icon Only",
                                             description=ANN_ICON_ONLY,
                                             default=False)
    property_value: bpy.props.BoolProperty(name="Property",
                                           description=ANN_PROPERTY,
                                           default=False)
    property_name_value: bpy.props.StringProperty(name="Name",
                                                  description=ANN_PROPERTY_NAME,
                                                  default="")
    property_value_value: bpy.props.StringProperty(name="Value",
                                                   description=ANN_PROPERTY_VALUE,
                                                   default="")
    property_callback_value: bpy.props.BoolProperty(name="Command As Callback",
                                                    description=ANN_PROPERTY_CALLBACK,
                                                    default=False)
    # It's not advised to use the update callbacks when defining the
    # operator properties because they are being constantly evaluated.
    # When using update callbacks it's best to only define these when
    # setting up the property group.
    group_value: bpy.props.EnumProperty(name="Group",
                                        description=ANN_GROUP,
                                        items=groupItems)
    button_value: bpy.props.EnumProperty(name="Tool",
                                         description=ANN_TOOL,
                                         items=toolItems)
    addon_list_value: bpy.props.EnumProperty(name="Add-on",
                                             description=ANN_ADDON,
                                             items=addOnItems)
    file_value: bpy.props.StringProperty(name="Import",
                                         description=ANN_IMPORT_FILE,
                                         default="",
                                         subtype='FILE_PATH')
    import_value: bpy.props.EnumProperty(name="Command",
                                         description=ANN_IMPORT_ITEM,
                                         items=importItems)

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        mode = self.mode_value

        # --------------------------------------------------------------
        # Add/Edit mode
        # --------------------------------------------------------------
        if mode == 'ADD' or mode == 'EDIT':
            # If no name is provided cancel the operation.
            if not len(self.name_value):
                self.report({'WARNING'}, "No name defined")
                return {'CANCELLED'}

            # ----------------------------------------------------------
            # Create a new tool group.
            # ----------------------------------------------------------
            if mode == 'ADD' and self.new_group_value:
                # If a new group should be created check if the new name
                # already exists.
                for group in CONFIG_DATA["groups"]:
                    if group["name"] == self.name_value:
                        self.report({'WARNING'}, "The group name already exists")
                        return {'CANCELLED'}

                # Backup the current configuration.
                backupConfig(CONFIG_DATA)

                # Add a new group to the configuration and save it.
                group = {"name": self.name_value,
                         "commands": [],
                         "expand": self.expand_value}
                # If no groups exist append to the empty list.
                if not len(CONFIG_DATA["groups"]):
                    CONFIG_DATA["groups"].append(group)
                # Add the group at the end of the list or after the
                # currently selected group.
                else:
                    if self.group_value != 'NONE':
                        insertIndex = getGroupIndex(CONFIG_DATA, self.group_value)+1
                        CONFIG_DATA["groups"].insert(insertIndex, group)
                    else:
                        CONFIG_DATA["groups"].append(group)

                # Save the configuration.
                jsonWrite(CONFIG_PATH, CONFIG_DATA)

            # ----------------------------------------------------------
            # Add or edit a new button or group.
            # ----------------------------------------------------------
            else:
                # Make sure a group is selected.
                if self.group_value == 'NONE':
                    self.report({'WARNING'}, "No group selected")
                    return {'CANCELLED'}

                # ------------------------------------------------------
                # Edit the group name.
                # ------------------------------------------------------
                if mode == 'EDIT' and self.button_value == 'NONE':
                    # If no name is provided cancel the operation.
                    if not len(self.name_value):
                        self.report({'WARNING'}, "No name defined")
                        return {'CANCELLED'}

                    # Backup the current configuration.
                    backupConfig(CONFIG_DATA)

                    # Rename the group.
                    groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)
                    CONFIG_DATA["groups"][groupIndex]["name"] = self.name_value
                    CONFIG_DATA["groups"][groupIndex]["expand"] = self.expand_value

                # ------------------------------------------------------
                # Edit the button command.
                # ------------------------------------------------------
                else:
                    # Check, if a button with the name already exists in
                    # the group.
                    if mode == 'ADD':
                        groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)
                        toolIndex = getToolIndex(CONFIG_DATA, self.name_value, groupIndex)
                        if toolIndex is not None:
                            self.report({'WARNING'}, "The tool name already exists in the group")
                            return {'CANCELLED'}

                    # Check, if the image exists in the icons folder.
                    for image in self.image_value.rstrip(";").split(";"):
                        if (not image.startswith("'") and image.split(".")[-1] == "png" and
                                not os.path.exists(os.path.join(ICONS_PATH, image))):
                            self.report({'WARNING'}, "The image doesn't exist in the path: "
                                                     "{}".format(os.path.join(ICONS_PATH, image)))
                            return {'CANCELLED'}

                    # Check if the add-on exists.
                    if self.addon_value:
                        addOnName = self.cmd_value
                        # If the complete command is given strip
                        # everything away but the add-on name.
                        if isAddOnToggle(addOnName):
                            addOnName = addOnName[13:-2]
                        if addOnName not in [item["name"] for item in getAddOns()]:
                            self.report({'WARNING'}, "An add-on with this name doesn't exist: "
                                                     "{}".format(addOnName))
                            return {'CANCELLED'}

                        if addOnName in ADD_ON_BLACKLIST:
                            self.report({'WARNING'}, "The add-on is incompatible and has to be "
                                                     "enabled/disabled from the preferences: "
                                                     "{}".format(addOnName))
                            return {'CANCELLED'}

                    # Check for the property values.
                    if self.property_value:
                        if not len(self.property_name_value) and not len(self.property_value_value):
                            self.report({'WARNING'}, "A property name and/or default value is missing")
                            return {'CANCELLED'}

                        names = self.property_name_value.rstrip(";").split(";")
                        values = self.property_value_value.rstrip(";").split(";")
                        if len(names) != len(values):
                            self.report({'WARNING'}, "The number of properties and values does not match")
                            return {'CANCELLED'}

                        if not balancedBrackets(self.property_name_value):
                            self.report({'WARNING'}, "The brackets for the properties are incomplete")
                            return {'CANCELLED'}

                    # Backup the current configuration.
                    backupConfig(CONFIG_DATA)

                    # Add a new command to the configuration and save
                    # it.
                    buttonCommand = ""
                    if mode == 'ADD' or (mode == 'EDIT' and self.cmd_value.strip() != "*"):
                        # Check if the toggle command has been entered
                        # or should be constructed.
                        if self.addon_value:
                            if not isAddOnToggle(self.cmd_value):
                                self.cmd_value = 'toggleAddOn("{}")'.format(self.cmd_value)
                        buttonCommand = processCommand(self.cmd_value)
                        if buttonCommand is None:
                            self.report({'WARNING'}, "No text editor open to get the tool command")
                            return {'CANCELLED'}

                    groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)

                    # Create a new command from the given data.
                    if mode == 'ADD':
                        if not self.new_set_value:
                            cmd = {"name": self.name_value,
                                   "icon": self.image_value,
                                   "iconOnly": self.image_only_value,
                                   "command": buttonCommand,
                                   "tooltip": self.tip_value if len(self.tip_value) else self.name_value}
                            # Only add the property if the option is
                            # enabled. It's possible that the fields
                            # contain data even if the user decided to
                            # disable this option again.
                            if self.property_value:
                                cmd["valueName"] = self.property_name_value
                                cmd["value"] = self.property_value_value
                                cmd["valueCallback"] = self.property_callback_value
                        else:
                            setItems = splitSetCommandString(self.set_value,
                                                             self.column_value,
                                                             self.name_value,
                                                             buttonCommand,
                                                             self.tip_value,
                                                             self.image_value,
                                                             self.image_only_value)
                            if setItems is None:
                                self.report({'WARNING'}, "The number of tool labels and commands "
                                                         "does not match")
                                return {'CANCELLED'}

                            cmd = {"set": self.set_value,
                                   "columns": self.column_value,
                                   "commands": setItems}
                            # Only add the property if the option is
                            # enabled. It's possible that the fields
                            # contain data even if the user decided to
                            # disable this option again.
                            if self.property_value:
                                cmd["valueName"] = self.property_name_value
                                cmd["value"] = self.property_value_value
                                cmd["valueCallback"] = self.property_callback_value

                        # Add the command at the end of the list or
                        # after the currently selected tool.
                        if self.button_value != 'NONE':
                            insertIndex = getToolIndex(CONFIG_DATA, self.button_value, groupIndex) + 1
                            CONFIG_DATA["groups"][groupIndex]["commands"].insert(insertIndex, cmd)
                        else:
                            CONFIG_DATA["groups"][groupIndex]["commands"].append(cmd)

                    # Update the existing command with the given data.
                    else:
                        toolIndex = getToolIndex(CONFIG_DATA, self.button_value, groupIndex)
                        if not len(self.set_value):
                            if len(self.name_value) and self.name_value.strip() != "*":
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["name"] = self.name_value
                            if self.image_value.strip() != "*":
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["icon"] = self.image_value
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["iconOnly"] = self.image_only_value
                            if self.cmd_value.strip() != "*":
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["command"] = buttonCommand
                            if len(self.tip_value) and self.tip_value.strip() != "*":
                                toolTip = self.tip_value if len(self.tip_value) else self.name_value
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["tooltip"] = toolTip
                            if len(self.property_name_value) and self.property_name_value.strip() != "*":
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["valueName"] = self.property_name_value
                            if len(self.property_value_value) and self.property_value_value.strip() != "*":
                                CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["value"] = self.property_value_value
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["valueCallback"] = self.property_callback_value

                            # If the property option has been disabled
                            # but the tool contains a property, remove
                            # it.
                            if not self.property_value:
                                if "valueName" in CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]:
                                    CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex].pop("valueName", None)
                                if "value" in CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]:
                                    CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex].pop("value", None)
                                if "valueCallback" in CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]:
                                    CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex].pop("valueCallback", None)
                        else:
                            setItems = splitSetCommandString(self.set_value,
                                                             self.column_value,
                                                             self.name_value,
                                                             buttonCommand,
                                                             self.tip_value,
                                                             self.image_value,
                                                             self.image_only_value)
                            if setItems is None:
                                self.report({'WARNING'}, "The number of tool labels and commands "
                                                         "does not match")
                                return {'CANCELLED'}

                            cmd = {"set": self.set_value,
                                   "columns": self.column_value,
                                   "commands": setItems}
                            # Only add the property if the option is
                            # enabled. It's possible that the fields
                            # contain data even if the user decided to
                            # disable this option again.
                            if self.property_value:
                                cmd["valueName"] = self.property_name_value
                                cmd["value"] = self.property_value_value
                                cmd["valueCallback"] = self.property_callback_value
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex] = cmd

                # Save the configuration.
                jsonWrite(CONFIG_PATH, CONFIG_DATA)

            # Reload the panel.
            bpy.ops.script.reload()

            context.scene.tool_shelf.expand_value = False
            context.scene.tool_shelf.new_set_value = False
            context.scene.tool_shelf.set_value = ""
            context.scene.tool_shelf.column_value = 2
            context.scene.tool_shelf.addon_value = False
            context.scene.tool_shelf.name_value = ""
            context.scene.tool_shelf.cmd_value = ""
            context.scene.tool_shelf.tip_value = ""
            context.scene.tool_shelf.image_value = ""
            context.scene.tool_shelf.image_only_value = False
            context.scene.tool_shelf.property_value = False
            context.scene.tool_shelf.property_name_value = ""
            context.scene.tool_shelf.property_value_value = ""
            context.scene.tool_shelf.property_callback_value = False

        # --------------------------------------------------------------
        # Remove mode
        # --------------------------------------------------------------
        elif mode == 'REMOVE':
            # Make sure a group is selected.
            if self.group_value == 'NONE':
                self.report({'WARNING'}, "No group selected")
                return {'CANCELLED'}

            # Backup the current configuration.
            backupConfig(CONFIG_DATA)

            # ----------------------------------------------------------
            # Delete the selected group.
            # ----------------------------------------------------------
            if self.button_value == 'NONE':
                CONFIG_DATA["groups"].pop(getGroupIndex(CONFIG_DATA, self.group_value))
                # Reset the enum values to prevent errors because
                # the removed item is not found anymore.
                self.group_value = 'NONE'
                context.scene.tool_shelf.group_value = 'NONE'

            # ----------------------------------------------------------
            # Delete the selected button.
            # ----------------------------------------------------------
            else:
                groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)
                toolIndex = getToolIndex(CONFIG_DATA, self.button_value, groupIndex)
                if toolIndex is not None:
                    CONFIG_DATA["groups"][groupIndex]["commands"].pop(toolIndex)
                    # Reset the enum values to prevent errors because
                    # the removed item is not found anymore.
                    self.button_value = 'NONE'
                    context.scene.tool_shelf.button_value = 'NONE'
                else:
                    self.report({'WARNING'}, "No tool doesn't exist in the selected group")
                    return {'CANCELLED'}

            # Save the configuration.
            jsonWrite(CONFIG_PATH, CONFIG_DATA)

            # Reload the panel.
            bpy.ops.script.reload()

        # --------------------------------------------------------------
        # Reorder mode
        # --------------------------------------------------------------
        elif mode == 'REORDER':
            # Backup the current configuration.
            backupConfig(CONFIG_DATA_BACKUP)

            # Save the configuration.
            jsonWrite(CONFIG_PATH, CONFIG_DATA)

            # Reload the panel.
            bpy.ops.script.reload()

            return {'FINISHED'}

        # --------------------------------------------------------------
        # View mode
        # --------------------------------------------------------------
        elif mode == 'VIEW':
            # Make sure a tool is selected.
            if self.button_value == 'NONE':
                self.report({'WARNING'}, "No tool selected")
                return {'CANCELLED'}

            textArea = currentTextArea()
            if textArea is None:
                self.report({'WARNING'}, "No text editor open to view the command")
                return {'CANCELLED'}

            # Create a new document with the name of the command.
            textName = idName("_".join((self.group_value, self.button_value)))
            bpy.data.texts.new(textName)
            # Set the text to display in the editor.
            textArea.text = bpy.data.texts[textName]

            # Go through all groups and search which command matches the
            # current selection.
            groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)
            toolIndex = getToolIndex(CONFIG_DATA, self.button_value, groupIndex)
            # Get the command from the configuration and write it to the
            # text file.
            if toolIndex is not None:
                command = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]
                if "name" in command:
                    cmdString = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["command"]
                else:
                    cmdString = ";".join([c["command"] for c in command["commands"]])
                bpy.data.texts[currentTextIndex()].write(cmdString)

        # --------------------------------------------------------------
        # Import mode
        # --------------------------------------------------------------
        elif mode == 'IMPORT':
            # Make sure the file exists.
            if not os.path.exists(self.file_value):
                self.report({'WARNING'}, "Select a valid configuration file")
                return {'CANCELLED'}
            # Make sure that a group or tool is selected.
            if self.import_value == 'NONE':
                self.report({'WARNING'}, "Select a group or tool to import")
                return {'CANCELLED'}

            # ----------------------------------------------------------
            # Import a group.
            # ----------------------------------------------------------
            if "___" not in self.import_value:
                groupName = self.import_value

                # Check if the group already exists.
                groupIndex = getGroupIndex(CONFIG_DATA, groupName)
                if groupIndex is not None:
                    self.report({'WARNING'}, "A group with this name already exists")
                    return {'CANCELLED'}

                # Backup the current configuration.
                backupConfig(CONFIG_DATA_BACKUP)

                groupIndex = getGroupIndex(CONFIG_DATA_IMPORT.config, groupName)
                CONFIG_DATA["groups"].append(CONFIG_DATA_IMPORT.config["groups"][groupIndex])

                # Save the configuration.
                jsonWrite(CONFIG_PATH, CONFIG_DATA)

                context.scene.tool_shelf.import_value = 'NONE'

                # Reload the panel.
                bpy.ops.script.reload()

            # ----------------------------------------------------------
            # Import a tool.
            # ----------------------------------------------------------
            else:
                # Make sure a group is selected.
                if self.group_value == 'NONE':
                    self.report({'WARNING'}, "No group selected")
                    return {'CANCELLED'}

                # Get the group and tool name from the selected element.
                groupName, toolName = self.import_value.split("___")

                groupIndex = getGroupIndex(CONFIG_DATA, self.group_value)
                toolIndex = getToolIndex(CONFIG_DATA, toolName, groupIndex)
                if toolIndex is not None:
                    self.report({'WARNING'}, "The tool name already exists in the group")
                    return {'CANCELLED'}

                # Backup the current configuration.
                backupConfig(CONFIG_DATA_BACKUP)

                # Get the group and tool name from the selected element.
                importGroupIndex = getGroupIndex(CONFIG_DATA_IMPORT.config, groupName)
                importToolIndex = getToolIndex(CONFIG_DATA_IMPORT.config, toolName, importGroupIndex)
                CONFIG_DATA["groups"][groupIndex]["commands"].append(CONFIG_DATA_IMPORT.config["groups"][importGroupIndex]["commands"][importToolIndex])

                # Save the configuration.
                jsonWrite(CONFIG_PATH, CONFIG_DATA)

                context.scene.tool_shelf.group_value = 'NONE'
                context.scene.tool_shelf.import_value = 'NONE'

                # Reload the panel.
                bpy.ops.script.reload()

        return {'FINISHED'}

# ----------------------------------------------------------------------
# 7. Set up the operators for additional actions.
# ----------------------------------------------------------------------


class TOOLSHELF_OT_MoveItemUp(bpy.types.Operator):
    """Operator class for moving an item up in the list.
    """
    bl_idname = "view3d.tool_shelf_item_up"
    bl_label = "Tool Shelf Move Item Up"

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        # Backup the configuration to be able to write a backup with the
        # unmodified dictionary when applying the new order.
        CONFIG_DATA_BACKUP = CONFIG_DATA.copy()

        tool_shelf = context.scene.tool_shelf
        name, isGroup = getReorderItem(context)
        # If no group is selected there is nothing to reorder.
        if name is None:
            return {'CANCELLED'}

        reorder(name=name,
                isGroup=isGroup,
                groupIndex=getGroupIndex(CONFIG_DATA, tool_shelf.group_value),
                up=True)
        if isGroup:
            tool_shelf.group_value = name
        else:
            tool_shelf.button_value = name

        return {'FINISHED'}


class TOOLSHELF_OT_MoveItemDown(bpy.types.Operator):
    """Operator class for moving an item up in the list.
    """
    bl_idname = "view3d.tool_shelf_item_down"
    bl_label = "Tool Shelf Move Item Down"

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        # Backup the configuration to be able to write a backup with the
        # unmodified dictionary when applying the new order.
        CONFIG_DATA_BACKUP = CONFIG_DATA.copy()

        tool_shelf = context.scene.tool_shelf
        name, isGroup = getReorderItem(context)
        # If no group is selected there is nothing to reorder.
        if name is None:
            return {'CANCELLED'}

        reorder(name=name,
                isGroup=isGroup,
                groupIndex=getGroupIndex(CONFIG_DATA, tool_shelf.group_value),
                up=False)
        if isGroup:
            tool_shelf.group_value = name
        else:
            tool_shelf.button_value = name

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Operators for getting file paths.
# ----------------------------------------------------------------------


class TOOLSHELF_OT_BrowseFilePath(bpy.types.Operator, ImportHelper):
    """Open a file browser and return the selected file path.
    """
    bl_idname = "toolshelf.browse_file_path"
    bl_label = "Select File"

    # The callback function to execute when the browser window gets
    # closed with the selected file item.
    callback = None

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        filepath = self.properties.filepath
        # Run the callback function if it's defined.
        if self.callback:
            self.callback(filepath)
        return {'FINISHED'}


def getFilePath(callback):
    """Call the operator for opening a file browser dialog to get a file
    selection.

    This function is provided with a callback function from the caller.
    This callback function is necessary to return the selected file path
    to the caller.

    :param callback: The function to return the selected file path to.
    :type callback: func
    """
    bpy.ops.toolshelf.browse_file_path('INVOKE_DEFAULT')
    TOOLSHELF_OT_BrowseFilePath.callback = lambda self, filepath: callback(self.filepath)


# ----------------------------------------------------------------------
# Helper methods
# ----------------------------------------------------------------------


def getGroupIndex(data, name):
    """Get the index of the currently selected group.

    :param data: The configuration dictionary to get the group from.
    :type data: dict
    :param name: The name of the selected group.
    :type name: str

    :return: The index of the group.
    :rtype: int or None
    """
    for i in range(len(data["groups"])):
        if data["groups"][i]["name"] == name:
            return i


def getToolIndex(data, name, groupIndex):
    """Get the index of the currently selected tool.
    Return None, if the tool cannot be found in the given group.

    :param data: The configuration dictionary to get the group from.
    :type data: dict
    :param name: The name of the selected tool.
    :type name: str
    :param groupIndex: The index of the group the tool belongs to.
    :type groupIndex: int

    :return: The index of the tool.
    :rtype: int or None
    """
    commands = data["groups"][groupIndex]["commands"]
    for i in range(len(commands)):
        if "name" in commands[i] and commands[i]["name"] == name:
            return i
        elif "set" in commands[i] and commands[i]["set"] == name:
            return i


def processCommand(cmd):
    """Format the given command string to include the necessary bpy
    import or get the content from the current text editor panel.
    Return None if no command is given and no text editor is currently
    open to get command lines from.

    :param cmd: The command string entered in the command field.
    :type cmd: str

    :return: The complete command for the button.
    :rtype: str or None
    """
    if len(cmd):
        cmdItems = cmd.rstrip(";").split(";")
        for i in range(len(cmdItems)):
            # Add the bpy import if the given command requires it.
            if "bpy." in cmdItems[i] and "import bpy" not in cmdItems[i]:
                cmdItems[i] = "import bpy\n{}".format(cmdItems[i])
        return ";".join(cmdItems)
    # If no command is provided get the content of the current text
    # editor, or it's selection.
    else:
        textIndex = currentTextIndex()
        if textIndex is None:
            return

        start, end = selectionRange(textIndex)
        content = []
        # If there is no text selection and the text cursor is placed
        # anywhere the start and end lines are the same. In this case
        # get the entire text.
        if start == end:
            for line in bpy.data.texts[textIndex].lines:
                content.append(line.body.replace("\t", "    "))
        else:
            # If there are more than two lines selected extend the end
            # index by one to make the range function work.
            # This is not necessary if only one line is selected and the
            # cursor is placed at the beginning of the next line.
            if end > start+1:
                end += 1
            for i in range(start, end):
                content.append(bpy.data.texts[textIndex].lines[i].body.replace("\t", "    "))
        return "\n".join(content)


def splitSetCommandString(setName, columns, labels, commands, tip, icons, iconOnly):
    """Split the given set command data into separate commands and
    return them as a list.

    :param setName: The name of the set.
    :type setName: str
    :param columns: The number of buttons in a row.
    :type columns: int
    :param labels: The semicolon-separated string for all button labels.
    :type labels: str
    :param commands: The semicolon-separated string for all commands.
    :type commands: str
    :param tip: The tooltip for all buttons.
    :type tip: str
    :param icons: The semicolon-separated string for all icons.
    :type icons: str
    :param iconOnly: True, if only the icon should be displayed.
    :type iconOnly: str

    :return: The list of command dictionaries or None if the number of
             labels and commands don't match.
    :rtype: list(dict) or None
    """
    labelItems = labels.rstrip(";").split(";")
    commandItems = commands.rstrip(";").split(";")
    iconItems = icons.rstrip(";").split(";")

    # The number of button labels and commands has to match.
    if len(labelItems) != len(commandItems):
        return

    # If the tooltip is missing add the name of the set.
    if not len(tip):
        tip = setName

    # If icons are missing add empty entries.
    if not len(iconItems):
        iconItems = [""] * len(labelItems) - 1
    if len(iconItems) < len(labelItems):
        for i in range(len(iconItems), len(labelItems)):
            iconItems.append("")

    cmdList = []
    columnIndex = 0
    rowIndex = 0
    for i in range(len(commandItems)):
        cmd = {"set": setName,
               "column": columnIndex,
               "row": rowIndex,
               "name": labelItems[i],
               "icon": iconItems[i],
               "iconOnly": iconOnly,
               "command": commandItems[i],
               "tooltip": tip}
        columnIndex += 1
        if columnIndex == columns:
            columnIndex = 0
            rowIndex += 1
        cmdList.append(cmd)

    return cmdList


def currentTextArea():
    """Return the currently active text object if there is an active
    text editor. Return None if no text editor exists.

    :return: The current text object.
    :rtype: bpy.types.Text or None
    """
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            return area.spaces.active


def currentTextIndex():
    """Return the index of the current text item.
    Return None if no text editor exists.

    :return: The index of the current text object.
    :rtype: int or None
    """
    textArea = currentTextArea()
    if textArea is None:
        return
    return textIndexByName(textArea.text.name)


def textIndexByName(name):
    """Return the index of the text object which matches the given name.

    :param name: The name of the text object.
    :type name: str

    :return: The index of the text object.
    :rtype: int or None
    """
    # Get a list of tuples with the text name and object.
    items = bpy.data.texts.items()
    for i in range(len(items)):
        if items[i][0] == name:
            return i


def selectionRange(index):
    """Return the indices of the lines which are defined by the current
    selection.

    :param index: The index of the text object currently being shown in
                  the text editor.
    :type index: int

    :return: The indices of the start and end lines.
    :rtype: tuple(int, int)
    """
    current = bpy.data.texts[index].current_line_index
    selectEnd = bpy.data.texts[index].select_end_line_index

    if current < selectEnd or current == selectEnd:
        return current, selectEnd
    else:
        return selectEnd, current


def getReorderItem(context):
    """Return the group or tool item name to reorder.

    :param context: The current context.
    :type context: bpy.context

    :return: A tuple with the group or tool name and an indicator if the
             item is a group.
             The tuple contains None if no group is selected.
    :rtype: tuple(str, bool) or tuple(None, None)
    """
    tool_shelf = context.scene.tool_shelf

    groupName = tool_shelf.group_value
    if groupName == 'NONE':
        return None, None
    else:
        toolName = tool_shelf.button_value
        if toolName == 'NONE':
            return groupName, True
        else:
            return toolName, False


def reorder(name="", isGroup=True, groupIndex=0, up=True):
    """Reorder the given item in the list based on the given direction.

    :param name: The name of the group or tool.
    :type name: str
    :param isGroup: True, if the item is a group.
    :type isGroup: bool
    :param groupIndex: The index of the current group.
    :type groupIndex: int
    :param up: True, if the item should be moved up in the list.
    :type up: bool
    """
    direction = -1 if up else 1

    if isGroup:
        if (up and groupIndex > 0) or (not up and groupIndex < len(CONFIG_DATA["groups"])-1):
            groupData = CONFIG_DATA["groups"][groupIndex]
            CONFIG_DATA["groups"].pop(groupIndex)
            CONFIG_DATA["groups"].insert(groupIndex+direction, groupData)
    else:
        toolIndex = getToolIndex(CONFIG_DATA, name, groupIndex)
        if (up and toolIndex > 0) or (not up and toolIndex < len(CONFIG_DATA["groups"][groupIndex]["commands"])-1):
            toolData = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]
            CONFIG_DATA["groups"][groupIndex]["commands"].pop(toolIndex)
            CONFIG_DATA["groups"][groupIndex]["commands"].insert(toolIndex+direction, toolData)


def balancedBrackets(checkString):
    """Return, if the given string contains balanced brackets.

    :param checkString: The string to check for brackets.
    :type checkString: str

    :return: True, if the string has balanced brackets.
    :rtype: bool
    """
    pairs = {"(": ")", "[": "]"}
    brackets = []
    for char in checkString:
        if char in ["(", "["]:
            brackets.append(char)
        elif brackets:
            if char == pairs[brackets[-1]]:
                brackets.pop()
        elif char in [")", "]"]:
            return False

    return len(brackets) == 0


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
CLASSES = [Tool_Shelf_Properties,
           TOOLSHELF_OT_Editor,
           TOOLSHELF_OT_MoveItemUp,
           TOOLSHELF_OT_MoveItemDown,
           TOOLSHELF_OT_BrowseFilePath,
           VIEW3D_PT_ToolShelf_Main,
           VIEW3D_PT_ToolShelf_Sub]
CLASSES.extend(CMD_CLASSES)


def register():
    """Register the add-on.
    """
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.tool_shelf = bpy.props.PointerProperty(type=Tool_Shelf_Properties)


def unregister():
    """Unregister the add-on.
    """
    # Remove the preview collection.
    for pcoll in ICON_COLLECTION.values():
        bpy.utils.previews.remove(pcoll)
    ICON_COLLECTION.clear()

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.tool_shelf


if __name__ == "__main__":
    register()
