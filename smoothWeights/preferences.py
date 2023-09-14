# <pep8 compliant>

from . import constants as const
from . import keymap, strings

import bpy


def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons[const.NAME].preferences
    return prefs


class SMOOTHWEIGHTSPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = const.NAME

    extras: bpy.props.BoolProperty(name=strings.EXTRAS_LABEL,
                                   description=strings.ANN_EXTRAS,
                                   default=const.EXTRAS)
    brush_color: bpy.props.FloatVectorProperty(name=strings.BRUSH_COLOR_LABEL,
                                               description=strings.ANN_BRUSH_COLOR,
                                               subtype='COLOR',
                                               default=const.BRUSH_COLOR)
    info_color: bpy.props.FloatVectorProperty(name=strings.INFO_TEXT_COLOR_LABEL,
                                              description=strings.ANN_INFO_COLOR,
                                              subtype='COLOR',
                                              default=const.INFO_COLOR)
    keep_selection: bpy.props.BoolProperty(name=strings.KEEP_SELECTION_LABEL,
                                           description=strings.ANN_KEEP_SELECTION,
                                           default=const.KEEP_SELECTION)
    selected_color: bpy.props.FloatVectorProperty(name=strings.SELECTED_COLOR_LABEL,
                                                  description=strings.ANN_SELECTED_COLOR,
                                                  subtype='COLOR',
                                                  default=const.SELECTED_COLOR)
    show_info: bpy.props.BoolProperty(name=strings.SHOW_INFO_LABEL,
                                      description=strings.ANN_SHOW_INFO,
                                      default=const.SHOW_INFO)
    show_time: bpy.props.BoolProperty(name=strings.SHOW_TIME_LABEL,
                                      description=strings.ANN_SHOW_TIME,
                                      default=const.SHOW_TIME)
    undo_steps: bpy.props.IntProperty(name=strings.UNDO_STEPS_LABEL,
                                      description=strings.ANN_UNDO_STEPS,
                                      default=const.UNDO_STEPS,
                                      min=1,
                                      max=100)
    unselected_color: bpy.props.FloatVectorProperty(name=strings.UNSELECTED_COLOR_LABEL,
                                                    description=strings.ANN_UNSELECTED_COLOR,
                                                    subtype='COLOR',
                                                    default=const.UNSELECTED_COLOR)

    affectSelected_key: bpy.props.StringProperty(name=strings.AFFECT_SELECTED_LABEL,
                                                 description=strings.ANN_AFFECT_SELECTED,
                                                 default=keymap.AFFECTSELECTED_KEY)
    clearSelection_key: bpy.props.StringProperty(name=strings.CLEAR_SELECTION_LABEL,
                                                 description=strings.ANN_CLEAR_SELECTION,
                                                 default=keymap.CLEARSELECTION_KEY)
    deselect_key: bpy.props.StringProperty(name=strings.DESELECT_LABEL,
                                           description=strings.ANN_DESELECT,
                                           default=keymap.DESELECT_KEY)
    flood_key: bpy.props.StringProperty(name=strings.FLOOD_LABEL,
                                        description=strings.ANN_FLOOD,
                                        default=keymap.FLOOD_KEY)
    ignoreBackside_key: bpy.props.StringProperty(name=strings.IGNORE_BACKSIDE_LABEL,
                                                 description=strings.ANN_IGNORE_BACKSIDE,
                                                 default=keymap.IGNOREBACKSIDE_KEY)
    ignoreLock_key: bpy.props.StringProperty(name=strings.IGNORE_LOCK_LABEL,
                                             description=strings.ANN_IGNORE_LOCK,
                                             default=keymap.IGNORELOCK_KEY)
    islands_key: bpy.props.StringProperty(name=strings.USE_ISLANDS_LABEL,
                                          description=strings.ANN_USE_ISLANDS,
                                          default=keymap.ISLANDS_KEY)
    maxGroups_key: bpy.props.StringProperty(name=strings.MAX_GROUPS_LABEL,
                                            description=strings.ANN_MAX_GROUPS,
                                            default=keymap.MAXGROUPS_KEY)
    normalize_key: bpy.props.StringProperty(name=strings.NORMALIZE_LABEL,
                                            description=strings.ANN_NORMALIZE,
                                            default=keymap.NORMALIZE_KEY)
    oversampling_key: bpy.props.StringProperty(name=strings.OVERSAMPLING_LABEL,
                                               description=strings.ANN_OVERSAMPLING,
                                               default=keymap.OVERSAMPLING_KEY)
    radius_key: bpy.props.StringProperty(name=strings.RADIUS_LABEL,
                                         description=strings.ANN_RADIUS,
                                         default=keymap.RADIUS_KEY)
    select_key: bpy.props.StringProperty(name=strings.SELECT_LABEL,
                                         description=strings.ANN_SELECT,
                                         default=keymap.SELECT_KEY)
    strength_key: bpy.props.StringProperty(name=strings.STRENGTH_LABEL,
                                           description=strings.ANN_STRENGTH,
                                           default=keymap.STRENGTH_KEY)
    useSelection_key: bpy.props.StringProperty(name=strings.USE_SELECTION_LABEL,
                                               description=strings.ANN_USE_SELECTION,
                                               default=keymap.USESELECTION_KEY)
    useSymmetry_key: bpy.props.StringProperty(name=strings.USE_SYMMETRY_LABEL,
                                              description=strings.ANN_USE_SYMMETRY,
                                              default=keymap.USESYMMETRY_KEY)
    value_up_key: bpy.props.StringProperty(name=strings.INCREASE_VALUE_LABEL,
                                           description=strings.ANN_VALUE_UP,
                                           default=keymap.VALUE_UP_KEY)
    value_down_key: bpy.props.StringProperty(name=strings.DECREASE_VALUE_LABEL,
                                             description=strings.ANN_VALUE_DOWN,
                                             default=keymap.VALUE_DOWN_KEY)
    volume_key: bpy.props.StringProperty(name=strings.VOLUME_LABEL,
                                         description=strings.ANN_VOLUME,
                                         default=keymap.VOLUME_KEY)
    volumeRange_key: bpy.props.StringProperty(name=strings.VOLUME_RANGE_LABEL,
                                              description=strings.ANN_VOLUME_RANGE,
                                              default=keymap.VOLUMERANGE_KEY)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        box = col.box()
        colBox = box.column(align=True)
        colBox.label(text="General")
        colBox.prop(self, "show_info")
        colBox.prop(self, "keep_selection")
        colBox.prop(self, "undo_steps")
        colBox.prop(self, "extras")
        colBox.prop(self, "show_time")
        colBox.separator()
        colBox.prop(self, "brush_color")
        colBox.prop(self, "info_color")
        colBox.prop(self, "selected_color")
        colBox.prop(self, "unselected_color")

        box = col.box()
        colBox = box.column(align=True)
        colBox.label(text="Keymaps")
        colBox.prop(self, "radius_key")
        colBox.prop(self, "strength_key")
        colBox.prop(self, "useSelection_key")
        colBox.prop(self, "affectSelected_key")
        colBox.prop(self, "ignoreBackside_key")
        colBox.prop(self, "ignoreLock_key")
        colBox.prop(self, "islands_key")
        colBox.prop(self, "normalize_key")
        colBox.prop(self, "oversampling_key")
        colBox.prop(self, "useSymmetry_key")
        colBox.separator()
        colBox.prop(self, "volume_key")
        colBox.prop(self, "volumeRange_key")
        colBox.separator()
        colBox.prop(self, "maxGroups_key")
        colBox.separator()
        colBox.prop(self, "value_up_key")
        colBox.prop(self, "value_down_key")
        colBox.separator()
        colBox.prop(self, "select_key")
        colBox.prop(self, "deselect_key")
        colBox.prop(self, "clearSelection_key")
        colBox.separator()
        colBox.prop(self, "flood_key")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [SMOOTHWEIGHTSPreferences]


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
