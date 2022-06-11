# <pep8 compliant>

import bpy

from .. import var


ANN_AUTO_LABEL = "Set the label for property and shape key nodes based on the property name"
ANN_DEVELOPER = "Show developer extras"
ANN_LOG_DATA = "Write the RBF data to the command output"


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

    autoLabel : bpy.props.BoolProperty(name="Auto Label Property Nodes",
                                       description=ANN_AUTO_LABEL,
                                       default=var.AUTO_LABEL)
    developerMode : bpy.props.BoolProperty(name="Developer Mode",
                                           description=ANN_DEVELOPER,
                                           default=var.DEVELOPER_MODE)
    logData : bpy.props.BoolProperty(name="Log RBF Data",
                                     description=ANN_LOG_DATA,
                                     default=var.EXPOSE_DATA)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "autoLabel")
        col.separator(factor=1.5)
        col.prop(self, "developerMode")
        if self.developerMode:
            col.prop(self, "logData")
