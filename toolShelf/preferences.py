# <pep8 compliant>

from . import constants as const
from . import language

import bpy


# Get the current language.
strings = language.getLanguage()


# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------

def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons[const.NAME].preferences
    return prefs


def updateLanguageCallback(self, context):
    """Property callback for changing the active language.

    :param context: The current context.
    :type context: bpy.context
    """
    reload()


def reload():
    """Reload the dependencies and the add-on.

    Also used for updating the panel when adding, editing or removing
    groups or tools.
    """
    language.reloadDependencies()
    # Reload the add-on.
    bpy.ops.script.reload()


class TOOLSHELFPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = const.NAME

    language: bpy.props.EnumProperty(name=strings.LANGUAGE_LABEL,
                                     items=language.LANGUAGE_ITEMS,
                                     description=strings.ANN_LANGUAGE,
                                     default=const.LANGUAGE,
                                     update=updateLanguageCallback)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "language")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [TOOLSHELFPreferences]


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
