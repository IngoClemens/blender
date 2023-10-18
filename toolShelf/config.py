# <pep8 compliant>

from . import constants as const

import bpy
import addon_utils

import io
import json
import logging
import os


logger = logging.getLogger(__name__)


LOCAL_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(LOCAL_PATH, const.CONFIG_NAME)
ICONS_PATH = os.path.join(LOCAL_PATH, "icons")
SCRIPTS_PATH = os.path.join(LOCAL_PATH, "scripts")
BACKUP_PATH = os.path.join(LOCAL_PATH, "backup")
BACKUP_COUNT = 5


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
                "language": const.LANGUAGE,
                "region": "UI",
                "space": "VIEW_3D",
                "base": "view3d",
                "groups": []
            }


def readConfig():
    """Read the configuration file. If the file doesn't exist create the
    basic configuration and return it.
    Also return the default paths for icons, scripts and backup.

    :return: The content of the configuration file.
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
    try:
        with io.open(filePath, "w", encoding="utf8") as fileObj:
            writeString = json.dumps(addVersions(data), sort_keys=True, indent=4, ensure_ascii=False)
            fileObj.write(str(writeString))
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
    version = [mod.bl_info["version"] for mod in addon_utils.modules() if mod.__name__ == const.NAME]
    if len(version):
        data["version"] = ".".join(str(i) for i in version[0])
    data["blenderVersion"] = bpy.app.version_string
    return data


def backupConfig(data):
    """Backup the given configuration.

    :param data: The configuration dictionary to back up.
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
    update = False

    if not "language" in data:
        data["language"] = const.LANGUAGE
        update = True

    # Cancel if no groups have been defined.
    if "groups" not in data:
        return data

    config = dict(data)

    updateItems = [("iconOnly", False)]

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
