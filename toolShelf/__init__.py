"""
toolShelf
Copyright (C) 2021, Ingo Clemens, brave rabbit, www.braverabbit.com

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

0.1.0 - 2021-04-22
      - First public release

------------------------------------------------------------------------
"""

bl_info = {"name": "Tool Shelf",
           "author": "Ingo Clemens",
           "version": (0, 1, 0),
           "blender": (2, 92, 0),
           "category": "Interface",
           "location": "View3D",
           "description": "Save scripts as buttons and organize them in groups for easy access",
           "warning": "",
           "doc_url": "https://www.braverabbit.com/toolShelf",
           "tracker_url": ""}

import bpy
import bpy.utils.previews

import io
import json
import logging
import os
import re
import sys
import types

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
# The list of all classes representing the buttons.
CMD_CLASSES = []
# The dictionary with all button data per group.
GROUPS = []
# The list of all button icons.
ICONS = []
# Main dictionary for storing the menu icons.
ICON_COLLECTION = {}

UPDATE_FIELDS = True

# Add the current path to the system in case other scripts are placed
# here.
sys.path.append(SCRIPTS_PATH)

# Define the alphanumeric regex pattern for the operator class name and
# idname.
ALPHANUM = re.compile("[\W]", re.UNICODE)

# ----------------------------------------------------------------------
# Descriptions and tooltips
# ----------------------------------------------------------------------

ANN_MODE = "Switch the editing mode"
ANN_NEW_GROUP = "Add a new group instead of a new command"
ANN_NAME = ("The name of the group or button command.\n"
            "It needs to be unique in lowercase across all groups")
ANN_COMMAND = ("The command string for the button.\n"
               "For simple commands the bpy import is added automatically.\n"
               "Leave empty to get the content from the text editor")
ANN_TOOLTIP = "The tooltip for the button"
ANN_ICON = ("The name of the icon file with 32x32 pixel or a default Blender icon identifier "
            "enclosed in single quotes")
ANN_GROUP = ("The group to add the command to.\n"
             "A new group it will be created after the last or after the selected group item")
ANN_TOOL = "The tool command to edit"

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


CONFIG_DATA = readConfig()


# ----------------------------------------------------------------------
# 2. Build the tool content classes.
# Create the operator class for each command represented by a button.
# A class contains the label, description and command executed by the
# button.
# ----------------------------------------------------------------------

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
    return re.sub(ALPHANUM, '', name.lower().replace(" ", "_"))


def getIdName(data):
    """Return the bl_idname for the given operator which gets combined
    from the UI area, i.e. view3d, and the lowercase name of the tool.

    :param data: The dictionary which describes the command.
    :type data: dict

    :return: The idname string for the operator.
    :rtype: str
    """
    return "{}.{}".format(CONFIG_DATA["base"], idName(data["name"]))


def getOperatorClassName(data):
    """Return the class name for the given operator.

    :param data: The dictionary which describes the command.
    :type data: dict

    :return: The idname string for the operator.
    :rtype: str
    """
    name = re.sub(ALPHANUM, '', data["name"].title())
    return "OBJECT_OT_{}".format(name)


def buildOperatorClass(data):
    """Construct and register an operator class for the given command.

    :param data: The dictionary which describes the command.
    :type data: dict

    :return: The operator class.
    :rtype: class
    """
    # Build the execute method for the operator up front so that it can
    # be referenced when the class gets build.
    execute = ["def execute(self, context):"]
    execute.append("{}".format(data["command"].replace("\n", "\n    ")))
    execute.append("return {'FINISHED'}")

    # Register the method within the module.
    module = types.ModuleType("operatorExecute")
    exec("\n    ".join(execute), module.__dict__)

    # Create the class.
    toolClass = type(getOperatorClassName(data),
                     (bpy.types.Operator, ),
                     {"bl_idname": getIdName(data),
                      "bl_label": data["name"],
                      "bl_description": data["tooltip"],
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

    # For each defined group in the configuration file build the classes for
    # all contained buttons and set up a dictionary for every button
    # containing the operator idname and the related icon.
    for group in configData["groups"]:
        toolData = []
        # Process each button/command in the current group.
        for cmd in group["commands"]:
            CMD_CLASSES.append(buildOperatorClass(cmd))
            # Collect the operator data in a dictionary which is used then
            # setting up the buttons.
            toolData.append({"id": getIdName(cmd),
                             "icon": cmd["icon"]})
            # If the command includes an icon, add it to the list of icons
            # to be added to the preview collection.
            if cmd["icon"]:
                ICONS.append(cmd["icon"])

        # Store the collected data per group along with the group name.
        GROUPS.append({"name": group["name"], "toolData": toolData})


readConfiguration(CONFIG_DATA)


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
    # Parse every icon which is associated with a button and test if it's a
    # valid file. Add it to the preview collection.
    for icon in icons:
        if len(icon) and not icon.startswith("'"):
            imagePath = os.path.join(filePath, icon)
            if os.path.exists(imagePath):
                # Try to add the icon to the preview collection in case the
                # image already exists.
                try:
                    pcoll.load(iconIdName(icon), imagePath, 'IMAGE', True)
                except:
                    pass

    return pcoll


ICON_COLLECTION["icons"] = registerIcons(ICONS, ICONS_PATH)


# ----------------------------------------------------------------------
# 4. Property Group
# Globally define all properties for adding new buttons and commands.
# ----------------------------------------------------------------------

def groupChanged(self, context):
    """Callback for when the group enum property selection changes.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    # Reset the tool selection.
    tool_shelf.button_value = 'NONE'
    # Clear all fields in edit mode.
    if tool_shelf.mode_value == 'EDIT':
        tool_shelf.name_value = tool_shelf.group_value
        tool_shelf.cmd_value = ""
        tool_shelf.tip_value = ""
        tool_shelf.image_value = ""


def toolChanged(self, context):
    """Callback for when the tool enum property selection changes.
    Populates the fields in edit mode to show the current command
    definition.

    :param context: The current context.
    :type context: bpy.context
    """
    tool_shelf = context.scene.tool_shelf

    if tool_shelf.mode_value == 'EDIT':
        groupIndex = currentGroupIndex(tool_shelf.group_value)
        toolIndex = currentToolIndex(tool_shelf.button_value, groupIndex)
        if toolIndex is not None:
            command = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]
            tool_shelf.name_value = command["name"]
            tool_shelf.cmd_value = command["command"]
            tool_shelf.tip_value = command["tooltip"]
            tool_shelf.image_value = command["icon"]
        else:
            tool_shelf.name_value = tool_shelf.group_value
            tool_shelf.cmd_value = ""
            tool_shelf.tip_value = ""
            tool_shelf.image_value = ""


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
        groupIndex = currentGroupIndex(tool_shelf.group_value)
        commands = CONFIG_DATA["groups"][groupIndex]["commands"]
        for item in commands:
            tools.append((item["name"], item["name"], ""))

    return tools


def modeItems(self, context):
    """Return the items for the modes enum property.

    :param context: The current context.
    :type context: bpy.context

    :return: A tuple with the enum items.
    :rtype: tuple()
    """
    return (('ADD', "", "Add a new group or button command", 'ADD', 0),
            ('REMOVE', "", "Delete an existing group or button", 'REMOVE', 1),
            ('EDIT', "", "Overwrite the command of an existing button.\nUse the asterisk * "
             "symbol to keep existing settings", 'GREASEPENCIL', 2),
            ('REORDER', "", "Reorder groups and buttons", 'LINENUMBERS_ON', 3),
            ('VIEW', "", "Display a button command in the text editor", 'FILE', 4))


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
                                          default="",
                                          subtype='FILE_NAME')
    group_value: bpy.props.EnumProperty(name="Group",
                                        description=ANN_GROUP,
                                        items=groupItems,
                                        update=groupChanged)
    button_value: bpy.props.EnumProperty(name="Tool",
                                         description=ANN_TOOL,
                                         items=toolItems,
                                         update=toolChanged)


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

            if tool_shelf.new_group_value:
                col.prop(tool_shelf, "name_value")
                col.prop(tool_shelf, "group_value", text="After Group")
                label = "Add Group"
            else:
                col.prop(tool_shelf, "group_value")
                if mode == 'ADD':
                    col.prop(tool_shelf, "button_value", text="After Tool")
                else:
                    col.prop(tool_shelf, "button_value")
                    label = "Edit"

                # Begin a new section.
                col = self.layout.column(align=True)

                col.prop(tool_shelf, "name_value")
                if mode == 'ADD' or (mode == 'EDIT' and tool_shelf.button_value != 'NONE'):
                    col.prop(tool_shelf, "cmd_value")
                    col.prop(tool_shelf, "tip_value")
                    col.prop(tool_shelf, "image_value")
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
        op.name_value = tool_shelf.name_value
        op.cmd_value = tool_shelf.cmd_value
        op.tip_value = tool_shelf.tip_value
        op.image_value = tool_shelf.image_value
        op.group_value = tool_shelf.group_value
        op.button_value = tool_shelf.button_value


def buildPanelClass(name, data, index):
    """Build the expandable sub panel for the given tool group.

    :param name: The name of the sub panel/group.
    :type name: str
    :param data: The list of tool dictionaries, containing the operator
                 idname and icon for each button.
    :type data: list(dict)
    :param index: The index of the group used for defining a unique
                  panel class name.
    :type index: int

    :return: The class of the sub panel.
    :rtype: class
    """
    # Get a reference to the preview collection to access the icons.
    pcoll = ICON_COLLECTION["icons"]

    # Build the draw method for the panel up front so that it can be
    # referenced when the class gets build.
    draw = ["def draw(self, context):"]
    for button in data:
        # If no icon is defined only add a simple button.
        if not len(button["icon"]):
            draw.append("self.layout.operator('{}')".format(button["id"]))
        else:
            if button["icon"].startswith("'"):
                draw.append("self.layout.operator('{}', icon={})".format(button["id"], button["icon"]))
            else:
                # Get the icon id related to the image from the preview
                # collection.
                icon_id = pcoll[iconIdName(button["icon"])].icon_id
                draw.append("self.layout.operator('{}', icon_value={})".format(button["id"], icon_id))
    # If no buttons are defined, which is the case when a new group has
    # just been added, add pass to the method to make it valid.
    if not len(data):
        draw.append("pass")

    # Register the method within the module.
    module = types.ModuleType("panelDraw")
    exec("\n    ".join(draw), module.__dict__)

    # Define the class name based on the group index.
    clsName = "VIEW3D_PT_ToolShelf_Sub_{}".format(index)
    # Create the class.
    toolClass = type(clsName,
                     (VIEW3D_PT_ToolShelf, ),
                     {"bl_parent_id": "VIEW3D_PT_ToolShelf_Main",
                      "bl_label": name,
                      "bl_options": {"DEFAULT_CLOSED"},
                      "draw": module.draw})

    return toolClass


def buildGroupPanels():
    """Construct a sub panel for each group and add the related buttons.
    """
    for i in range(len(GROUPS)):
        CMD_CLASSES.append(buildPanelClass(GROUPS[i]["name"],
                                           GROUPS[i]["toolData"],
                                           i))


buildGroupPanels()


# ----------------------------------------------------------------------
# 6. Set up the operator for adding new buttons.
# ----------------------------------------------------------------------

class TOOLSHELF_OT_Editor(bpy.types.Operator):
    """Operator class for the tool.
    """
    bl_idname = "view3d.tool_shelf"
    bl_label = "Tool Shelf"
    bl_description = ""

    mode_value: bpy.props.EnumProperty(name="Mode",
                                       description=ANN_MODE,
                                       items=modeItems)
    new_group_value: bpy.props.BoolProperty(name="New Group",
                                            description=ANN_NEW_GROUP,
                                            default=False)
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
                                          default="",
                                          subtype='FILE_NAME')
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
            # If no name if provided cancel the operation.
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
                         "commands": []}
                # If no groups exist append to the empty list.
                if not len(CONFIG_DATA["groups"]):
                    CONFIG_DATA["groups"].append(group)
                # Add the group at the end of the list or after the
                # currently selected group.
                else:
                    if self.group_value != 'NONE':
                        insertIndex = currentGroupIndex(self.group_value)+1
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
                    # If no name if provided cancel the operation.
                    if not len(self.name_value):
                        self.report({'WARNING'}, "No name defined")
                        return {'CANCELLED'}

                    # Backup the current configuration.
                    backupConfig(CONFIG_DATA)

                    # Rename the group.
                    groupIndex = currentGroupIndex(self.group_value)
                    CONFIG_DATA["groups"][groupIndex]["name"] = self.name_value

                # ------------------------------------------------------
                # Edit the button command.
                # ------------------------------------------------------
                else:
                    # Check, if a button with the name already exists.
                    if mode == 'ADD':
                        for group in CONFIG_DATA["groups"]:
                            for cmd in group["commands"]:
                                if idName(cmd["name"]) == idName(self.name_value):
                                    self.report({'WARNING'}, "The command name already exists in "
                                                             "group: {}".format(group["name"]))
                                    return {'CANCELLED'}

                    # Check, if the image exists in the icons folder.
                    if (not self.image_value.startswith("'") and
                            not os.path.exists(os.path.join(ICONS_PATH, self.image_value))):
                        self.report({'WARNING'}, "The image doesn't exist in the path: "
                                                 "{}".format(ICONS_PATH))
                        return {'CANCELLED'}

                    # Backup the current configuration.
                    backupConfig(CONFIG_DATA)

                    # Add a new command to the configuration and save it.
                    buttonCommand = ""
                    if mode == 'ADD' or (mode == 'EDIT' and self.cmd_value.strip() != "*"):
                        buttonCommand = processCommand(self.cmd_value)
                        if buttonCommand is None:
                            self.report({'WARNING'}, "No text editor open to get the button command")
                            return {'CANCELLED'}

                    groupIndex = currentGroupIndex(self.group_value)

                    # Create a new command from the given data.
                    if mode == 'ADD':
                        cmd = {"name": self.name_value,
                               "icon": self.image_value,
                               "command": buttonCommand,
                               "tooltip": self.tip_value if len(self.tip_value) else self.name_value}
                        # Add the command at the end of the list or
                        # after the currently selected tool.
                        if self.button_value != 'NONE':
                            insertIndex = currentToolIndex(self.button_value, groupIndex)+1
                            CONFIG_DATA["groups"][groupIndex]["commands"].insert(insertIndex, cmd)
                        else:
                            CONFIG_DATA["groups"][groupIndex]["commands"].append(cmd)
                    # Update the existing command with the given data.
                    else:
                        toolIndex = currentToolIndex(self.button_value, groupIndex)
                        if len(self.name_value) and self.name_value.strip() != "*":
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["name"] = self.name_value
                        if len(self.image_value) and self.image_value.strip() != "*":
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["icon"] = self.image_value
                        if self.cmd_value.strip() != "*":
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["command"] = buttonCommand
                        if len(self.tip_value) and self.tip_value.strip() != "*":
                            toolTip = self.tip_value if len(self.tip_value) else self.name_value
                            CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["tooltip"] = toolTip

                # Save the configuration.
                jsonWrite(CONFIG_PATH, CONFIG_DATA)

            # Reload the panel.
            bpy.ops.script.reload()

            context.scene.tool_shelf.name_value = ""
            context.scene.tool_shelf.cmd_value = ""
            context.scene.tool_shelf.tip_value = ""
            context.scene.tool_shelf.image_value = ""

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
                CONFIG_DATA["groups"].pop(currentGroupIndex(self.group_value))
                # Reset the enum values to prevent errors because
                # the removed item is not found anymore.
                self.group_value = 'NONE'
                context.scene.tool_shelf.group_value = 'NONE'

            # ----------------------------------------------------------
            # Delete the selected button.
            # ----------------------------------------------------------
            else:
                groupIndex = currentGroupIndex(self.group_value)
                toolIndex = currentToolIndex(self.button_value, groupIndex)
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
            textName = idName(self.button_value)
            bpy.data.texts.new(textName)
            # Set the text to display in the editor.
            textArea.text = bpy.data.texts[textName]

            # Go through all groups and search which command matches the
            # current selection.
            groupIndex = currentGroupIndex(self.group_value)
            toolIndex = currentToolIndex(self.button_value, groupIndex)
            # Get the command from the configuration and write it to the
            # text file.
            if toolIndex is not None:
                command = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]["command"]
                bpy.data.texts[currentTextIndex()].write(command)

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
                groupIndex=currentGroupIndex(tool_shelf.group_value),
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
                groupIndex=currentGroupIndex(tool_shelf.group_value),
                up=False)
        if isGroup:
            tool_shelf.group_value = name
        else:
            tool_shelf.button_value = name

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Helper methods
# ----------------------------------------------------------------------

def currentGroupIndex(name):
    """Get the index of the currently selected group.

    :param name: The name of the selected group.
    :type name: str

    :return: The index of the group.
    :rtype: int
    """
    for i in range(len(CONFIG_DATA["groups"])):
        if CONFIG_DATA["groups"][i]["name"] == name:
            return i


def currentToolIndex(name, groupIndex):
    """Get the index of the currently selected tool.
    Return None, if the tool cannot be found in the given group.

    :param name: The name of the selected tool.
    :type name: str
    :param groupIndex: The index of the group the tool belongs to.
    :type groupIndex: int

    :return: The index of the tool.
    :rtype: int or None
    """
    commands = CONFIG_DATA["groups"][groupIndex]["commands"]
    for i in range(len(commands)):
        if commands[i]["name"] == name:
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
        # Add the bpy import if the given command requires it.
        if "bpy." in cmd and "import bpy" not in cmd:
            return "import bpy; {}".format(cmd)
        else:
            return cmd
    # If no command is provided get the content of the current text
    # editor or it's selection.
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
        toolIndex = currentToolIndex(name, groupIndex)
        if (up and toolIndex > 0) or (not up and toolIndex < len(CONFIG_DATA["groups"][groupIndex]["commands"])-1):
            toolData = CONFIG_DATA["groups"][groupIndex]["commands"][toolIndex]
            CONFIG_DATA["groups"][groupIndex]["commands"].pop(toolIndex)
            CONFIG_DATA["groups"][groupIndex]["commands"].insert(toolIndex+direction, toolData)


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
CLASSES = [Tool_Shelf_Properties,
           TOOLSHELF_OT_Editor,
           TOOLSHELF_OT_MoveItemUp,
           TOOLSHELF_OT_MoveItemDown,
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
