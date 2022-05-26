# <pep8 compliant>

import bpy

from .. import var


ANN_DEVELOPER = "Show developer extras"


def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons["RBFNodes"].preferences
    return prefs


class RBFNODESPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = "RBFNodes"

    developerMode: bpy.props.BoolProperty(name="Developer Mode",
                                          description=ANN_DEVELOPER,
                                          default=var.DEVELOPER_MODE)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "developerMode")
