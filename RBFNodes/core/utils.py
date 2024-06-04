# <pep8 compliant>

import bpy

from .. import preferences, var

import json
import math


VERSION = None


def verifyVersion(node):
    """Check the node version against the version of the add-on.

    :param node: The node.
    :type node: bpy.types.Node or None

    :return: True, if the version is valid.
    :rtype: bool
    """
    if node.version is None or not len(node.version):
        return False
    versionList = json.loads(node.version)
    if versionList is None:
        return False
    return versionList[0] <= VERSION[0]


def setVersion(node):
    """Set the node version.

    :param node: The node.
    :type node: bpy.types.Node
    """
    node.version = json.dumps(VERSION)


def getVersion(node):
    """Return the node version as a string.

    :param node: The node.
    :type node: bpy.types.Node

    :return: The version string.
    :rtype: str
    """
    versionList = json.loads(node.version)
    return versionString(versionList)


def versionString(version):
    """Return the given version tuple as a string.

    :param version: The version tuple.
    :type version: tuple

    :return: The version string.
    :rtype: str
    """
    return ".".join([str(i) for i in version])


def displayMessage(title="", message="", icon='INFO'):
    """Display an info message window.

    :param title: The title of the window.
    :type title: str
    :param message: The message to display. This can also be a list of
                    multiple lines.
    :type message: str or list(str)
    :param icon: The icon to display.
    :type icon: str
    """
    if not isinstance(message, list):
        message = [message]

    def draw(self, context):
        """Draw the content of the window.

        :param context: The current context.
        :type context: bpy.context
        """
        for line in message:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def getMaxSize():
    """Return the maximum number of values.

    :return: The maximum number of values for poses and weights.
    :rtype: int
    """
    return preferences.getPreferences().propertyCount * var.MAX_LEN


def getArrayCount():
    """
    """
    config = preferences.readConfig()

    if "propertyCount" in config:
        return math.ceil(config["propertyCount"] / var.MAX_LEN)
    else:
        return var.NUM_ARRAYS
