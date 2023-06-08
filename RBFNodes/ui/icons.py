# <pep8 compliant>

import bpy
import bpy.utils.previews

import os


class Icons(object):
    """Class for handling the tool icons.
    """
    def __init__(self):
        # Main dictionary for storing the icons.
        self.preview_collections = {}

    def create(self):
        """Set up the preview collection for giving access to the icons.
        """
        basePath = os.path.dirname(os.path.dirname(__file__))
        iconsDir = os.path.join(basePath, "icons")

        pcoll = bpy.utils.previews.new()
        pcoll.load("tool_icon", os.path.join(iconsDir, "RBFNodes.png"), 'IMAGE', True)
        self.preview_collections["icons"] = pcoll

    def delete(self):
        """Remove the preview collection.
        """
        for pcoll in self.preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        self.preview_collections.clear()

    def getIcon(self, name):
        """Return the icon with the given name.

        :param name: The name of the icon.
        :type name: str

        :return: The icon.
        :rtype: bpy.types.ImagePreview
        """
        return self.preview_collections["icons"][name]


toolIcons = Icons()
