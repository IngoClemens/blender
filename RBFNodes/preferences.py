# <pep8 compliant>

import bpy

from . import language, var

import io
import json
import os


LOCAL_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(LOCAL_PATH, var.CONFIG_NAME)


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def readConfig():
    """Read the configuration file.
    If the file doesn't exist create and return the basic configuration.

    :return: The content of the configuration file.
    :rtype: dict
    """
    if os.path.exists(CONFIG_PATH):
        config = jsonRead(CONFIG_PATH)
        if config:
            return config
        return var.DEFAULT_CONFIG
    else:
        config = var.DEFAULT_CONFIG
        jsonWrite(CONFIG_PATH, config)
        return config


def writeConfig(data):
    """Write the configuration file.

    :param data: The data to write.
    :type data: dict or list
    """
    jsonWrite(CONFIG_PATH, data)


def jsonRead(filePath):
    """Return the content of the given json file. Return an empty
    dictionary if the file doesn't exist.

    :param filePath: The file path of the file to read.
    :type filePath: str

    :return: The content of the json file.
    :rtype: dict
    """
    if os.path.exists(filePath):
        try:
            with open(filePath, "r") as fileObj:
                return json.load(fileObj)
        except OSError as exception:
            print(exception)


def jsonWrite(filePath, data):
    """Export the given data to the given json file.

    :param filePath: The file path of the file to write.
    :type filePath: str
    :param data: The data to write.
    :type data: dict or list

    :return: True, if writing was successful.
    :rtype: bool
    """
    try:
        with io.open(filePath, "w", encoding="utf8") as fileObj:
            writeString = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
            fileObj.write(str(writeString))
        return True
    except OSError as exception:
        print(exception)
    return False


def updateConfiguration(self, context):
    """Property callback for updating the current configuration.

    :param context: The current context.
    :type context: bpy.context
    """
    props = {"autoLabel": "autoLabel",
             "developerMode": "developerMode",
             "language": "language",
             "logData": "logData"}

    prefs = getPreferences()
    config = {}

    for prop in props:
        data = getattr(prefs, prop)
        config[props[prop]] = data

    # Write the configuration.
    writeConfig(config)


config = readConfig()
language.LANGUAGE = config["language"]


# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------


# Get the current language.
strings = language.getLanguage()


def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons[var.ID_NAME].preferences
    return prefs


def updateLanguageCallback(self, context):
    """Property callback for changing the active language.

    :param context: The current context.
    :type context: bpy.context
    """
    updateConfiguration(self, context)
    # language.reloadDependencies()
    # Reload the add-on.
    # bpy.ops.script.reload()


class RBFNODESPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = var.ID_NAME

    # Get the current configuration.
    config = readConfig()

    autoLabel : bpy.props.BoolProperty(name=strings.AUTO_LABEL_LABEL,
                                       description=strings.ANN_AUTO_LABEL,
                                       default=var.AUTO_LABEL)
    developerMode : bpy.props.BoolProperty(name=strings.DEVELOPER_LABEL,
                                           description=strings.ANN_DEVELOPER,
                                           default=var.DEVELOPER_MODE)
    language: bpy.props.EnumProperty(name=strings.LANGUAGE_LABEL,
                                     items=language.LANGUAGE_ITEMS,
                                     description=strings.ANN_LANGUAGE,
                                     default=config["language"],
                                     update=updateLanguageCallback)
    logData : bpy.props.BoolProperty(name=strings.LOG_DATA_LABEL,
                                     description=strings.ANN_LOG_DATA,
                                     default=var.EXPOSE_DATA)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "language")
        col.separator()
        col.prop(self, "autoLabel")
        col.separator(factor=1.5)
        col.prop(self, "developerMode")
        if self.developerMode:
            col.prop(self, "logData")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [RBFNODESPreferences]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)
