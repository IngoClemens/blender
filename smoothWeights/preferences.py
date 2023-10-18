# <pep8 compliant>

from . import constants as const
from . import language, panel

import bpy

import io
import json
import mathutils
import os


LOCAL_PATH = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(LOCAL_PATH, const.CONFIG_NAME)


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
        return const.DEFAULT_CONFIG
    else:
        config = const.DEFAULT_CONFIG
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


def updateConfig():
    """Update the current configuration.
    """
    props = {"language": "language",
             "extras": "extras",
             "brush_color": "brushColor",
             "info_color":  "infoColor",
             "keep_selection": "keepSelection",
             "panel_location": "panelLocation",
             "panel_name": "panelName",
             "pie_menu": "pieMenu",
             "selected_color": "selectedColor",
             "show_info": "showInfo",
             "show_time": "showTime",
             "undo_steps": "undoSteps",
             "unselected_color": "unselectedColor"}
    keys = {"affectSelected_key": "affectSelected",
            "blend_key": "blend",
            "clearSelection_key": "clearSelection",
            "deselect_key": "deselect",
            "flood_key": "flood",
            "ignoreBackside_key": "ignoreBackside",
            "ignoreLock_key": "ignoreLock",
            "islands_key": "islands",
            "maxGroups_key": "maxGroups",
            "normalize_key": "normalize",
            "oversampling_key": "oversampling",
            "pieMenu_key": "pieMenu",
            "radius_key": "radius",
            "select_key": "select",
            "strength_key": "strength",
            "useSelection_key": "useSelection",
            "useSymmetry_key": "useSymmetry",
            "value_up_key": "value_up",
            "value_down_key": "value_down",
            "vertexGroups_key": "vertexGroups",
            "volume_key": "volume",
            "volumeRange_key": "volumeRange"}

    prefs = getPreferences()
    config = {}

    # Get all regular properties.
    for prop in props:
        data = getattr(prefs, prop)
        # Convert the colors to a list.
        if isinstance(data, mathutils.Color):
            data = [i for i in data]
        config[props[prop]] = data

    # Get all keymaps
    keymap = {}
    for key in keys:
        keymap[keys[key]] = getattr(prefs, key)
    config["keymap"] = keymap

    # Get the pie areas.
    pieAreas = []
    for area in const.PIE_AREAS:
        pieAreas.append(getattr(prefs, area))

    # Compile the configuration.
    config["smoothPie"] = pieAreas

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
    prefs = bpy.context.preferences.addons[const.NAME].preferences
    return prefs


def updateConfiguration(self, context):
    """Property callback for updating the current configuration.

    :param context: The current context.
    :type context: bpy.context
    """
    updateConfig()


def updatePanelLocationCallback(self, context):
    """Property callback for changing the panel location and name.

    This is just a wrapper for calling the actual update function
    because of the necessary arguments used by the property callback.

    :param context: The current context.
    :type context: bpy.context
    """
    updateConfig()
    updatePanelLocation()


def updatePanelLocation():
    """Remove the current panel and create a new one with an updated
    location and name.
    """
    # Unregister the panel.
    panel.unregister()

    area = getPreferences().panel_location
    name = getPreferences().panel_name
    panel.register(area, name)


class SMOOTHWEIGHTSPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = const.NAME

    # Get the keymaps and pie menu.
    config = readConfig()
    keymap = config["keymap"]
    pieItems = config["smoothPie"]

    # Discard the mesh data properties location for the smooth panel
    # which has been introduced in version 2.4 but doesn't work due to
    # context restrictions.
    if config["panelLocation"] == "PROPERTIES":
        config["panelLocation"] = "TOOLS"

    extras: bpy.props.BoolProperty(name=strings.EXTRAS_LABEL,
                                   description=strings.ANN_EXTRAS,
                                   default=config["extras"],
                                   update=updateConfiguration)
    brush_color: bpy.props.FloatVectorProperty(name=strings.BRUSH_COLOR_LABEL,
                                               description=strings.ANN_BRUSH_COLOR,
                                               subtype='COLOR',
                                               default=config["brushColor"],
                                               update=updateConfiguration)
    info_color: bpy.props.FloatVectorProperty(name=strings.INFO_TEXT_COLOR_LABEL,
                                              description=strings.ANN_INFO_COLOR,
                                              subtype='COLOR',
                                              default=config["infoColor"],
                                              update=updateConfiguration)
    keep_selection: bpy.props.BoolProperty(name=strings.KEEP_SELECTION_LABEL,
                                           description=strings.ANN_KEEP_SELECTION,
                                           default=config["keepSelection"],
                                           update=updateConfiguration)
    language: bpy.props.EnumProperty(name=strings.LANGUAGE_LABEL,
                                     items=language.LANGUAGE_ITEMS,
                                     description=strings.ANN_LANGUAGE,
                                     default=config["language"],
                                     update=updateConfiguration)
    panel_location: bpy.props.EnumProperty(name=strings.PANEL_LOCATION_LABEL,
                                           items=const.PANEL_LOCATION_ITEMS,
                                           description=strings.ANN_PANEL_LOCATION,
                                           default=config["panelLocation"],
                                           update=updatePanelLocationCallback)
    panel_name: bpy.props.StringProperty(name=strings.PANEL_NAME_LABEL,
                                           description=strings.ANN_PANEL_NAME,
                                           default=config["panelName"],
                                           update=updatePanelLocationCallback)
    pie_menu: bpy.props.BoolProperty(name=strings.PIE_MENU_LABEL,
                                     description=strings.ANN_PIE_MENU,
                                     default=config["pieMenu"],
                                     update=updateConfiguration)
    selected_color: bpy.props.FloatVectorProperty(name=strings.SELECTED_COLOR_LABEL,
                                                  description=strings.ANN_SELECTED_COLOR,
                                                  subtype='COLOR',
                                                  default=config["selectedColor"],
                                                  update=updateConfiguration)
    show_info: bpy.props.BoolProperty(name=strings.SHOW_INFO_LABEL,
                                      description=strings.ANN_SHOW_INFO,
                                      default=config["showInfo"],
                                      update=updateConfiguration)
    show_time: bpy.props.BoolProperty(name=strings.SHOW_TIME_LABEL,
                                      description=strings.ANN_SHOW_TIME,
                                      default=config["showTime"],
                                      update=updateConfiguration)
    undo_steps: bpy.props.IntProperty(name=strings.UNDO_STEPS_LABEL,
                                      description=strings.ANN_UNDO_STEPS,
                                      default=config["undoSteps"],
                                      min=1,
                                      max=100,
                                      update=updateConfiguration)
    unselected_color: bpy.props.FloatVectorProperty(name=strings.UNSELECTED_COLOR_LABEL,
                                                    description=strings.ANN_UNSELECTED_COLOR,
                                                    subtype='COLOR',
                                                    default=config["unselectedColor"],
                                                    update=updateConfiguration)

    affectSelected_key: bpy.props.StringProperty(name=strings.AFFECT_SELECTED_LABEL,
                                                 description=strings.ANN_AFFECT_SELECTED,
                                                 default=keymap["affectSelected"],
                                                 update=updateConfiguration)
    blend_key: bpy.props.StringProperty(name=strings.BLEND_LABEL,
                                        description=strings.ANN_BLEND,
                                        default=keymap["blend"],
                                        update=updateConfiguration)
    clearSelection_key: bpy.props.StringProperty(name=strings.CLEAR_SELECTION_LABEL,
                                                 description=strings.ANN_CLEAR_SELECTION,
                                                 default=keymap["clearSelection"],
                                                 update=updateConfiguration)
    deselect_key: bpy.props.StringProperty(name=strings.DESELECT_LABEL,
                                           description=strings.ANN_DESELECT,
                                           default=keymap["deselect"],
                                           update=updateConfiguration)
    flood_key: bpy.props.StringProperty(name=strings.FLOOD_LABEL,
                                        description=strings.ANN_FLOOD,
                                        default=keymap["flood"],
                                        update=updateConfiguration)
    ignoreBackside_key: bpy.props.StringProperty(name=strings.IGNORE_BACKSIDE_LABEL,
                                                 description=strings.ANN_IGNORE_BACKSIDE,
                                                 default=keymap["ignoreBackside"],
                                                 update=updateConfiguration)
    ignoreLock_key: bpy.props.StringProperty(name=strings.IGNORE_LOCK_LABEL,
                                             description=strings.ANN_IGNORE_LOCK,
                                             default=keymap["ignoreLock"],
                                             update=updateConfiguration)
    islands_key: bpy.props.StringProperty(name=strings.USE_ISLANDS_LABEL,
                                          description=strings.ANN_USE_ISLANDS,
                                          default=keymap["islands"],
                                          update=updateConfiguration)
    maxGroups_key: bpy.props.StringProperty(name=strings.MAX_GROUPS_LABEL,
                                            description=strings.ANN_MAX_GROUPS,
                                            default=keymap["maxGroups"],
                                            update=updateConfiguration)
    normalize_key: bpy.props.StringProperty(name=strings.NORMALIZE_LABEL,
                                            description=strings.ANN_NORMALIZE,
                                            default=keymap["normalize"],
                                            update=updateConfiguration)
    oversampling_key: bpy.props.StringProperty(name=strings.OVERSAMPLING_LABEL,
                                               description=strings.ANN_OVERSAMPLING,
                                               default=keymap["oversampling"],
                                               update=updateConfiguration)
    pieMenu_key: bpy.props.StringProperty(name=strings.PIE_MENU_LABEL,
                                          description=strings.ANN_PIE_MENU,
                                          default=keymap["pieMenu"],
                                          update=updateConfiguration)
    radius_key: bpy.props.StringProperty(name=strings.RADIUS_LABEL,
                                         description=strings.ANN_RADIUS,
                                         default=keymap["radius"],
                                         update=updateConfiguration)
    select_key: bpy.props.StringProperty(name=strings.SELECT_LABEL,
                                         description=strings.ANN_SELECT,
                                         default=keymap["select"],
                                         update=updateConfiguration)
    strength_key: bpy.props.StringProperty(name=strings.STRENGTH_LABEL,
                                           description=strings.ANN_STRENGTH,
                                           default=keymap["strength"],
                                           update=updateConfiguration)
    useSelection_key: bpy.props.StringProperty(name=strings.USE_SELECTION_LABEL,
                                               description=strings.ANN_USE_SELECTION,
                                               default=keymap["useSelection"],
                                               update=updateConfiguration)
    useSymmetry_key: bpy.props.StringProperty(name=strings.USE_SYMMETRY_LABEL,
                                              description=strings.ANN_USE_SYMMETRY,
                                              default=keymap["useSymmetry"],
                                              update=updateConfiguration)
    value_up_key: bpy.props.StringProperty(name=strings.INCREASE_VALUE_LABEL,
                                           description=strings.ANN_VALUE_UP,
                                           default=keymap["value_up"],
                                           update=updateConfiguration)
    value_down_key: bpy.props.StringProperty(name=strings.DECREASE_VALUE_LABEL,
                                             description=strings.ANN_VALUE_DOWN,
                                             default=keymap["value_down"],
                                             update=updateConfiguration)
    vertexGroups_key: bpy.props.StringProperty(name=strings.VERTEX_GROUPS_LABEL,
                                               description=strings.ANN_VERTEX_GROUPS,
                                               default=keymap["vertexGroups"],
                                               update=updateConfiguration)
    volume_key: bpy.props.StringProperty(name=strings.VOLUME_LABEL,
                                         description=strings.ANN_VOLUME,
                                         default=keymap["volume"],
                                         update=updateConfiguration)
    volumeRange_key: bpy.props.StringProperty(name=strings.VOLUME_RANGE_LABEL,
                                              description=strings.ANN_VOLUME_RANGE,
                                              default=keymap["volumeRange"],
                                              update=updateConfiguration)

    pie_north: bpy.props.EnumProperty(name=strings.PIE_NORTH_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[5],
                                      update=updateConfiguration)
    pie_north_east: bpy.props.EnumProperty(name=strings.PIE_NORTH_EAST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[1],
                                      update=updateConfiguration)
    pie_east: bpy.props.EnumProperty(name=strings.PIE_EAST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[3],
                                      update=updateConfiguration)
    pie_south_east: bpy.props.EnumProperty(name=strings.PIE_SOUTH_EAST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[2],
                                      update=updateConfiguration)
    pie_south: bpy.props.EnumProperty(name=strings.PIE_SOUTH_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[7],
                                      update=updateConfiguration)
    pie_south_west: bpy.props.EnumProperty(name=strings.PIE_SOUTH_WEST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[0],
                                      update=updateConfiguration)
    pie_west: bpy.props.EnumProperty(name=strings.PIE_WEST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[6],
                                      update=updateConfiguration)
    pie_north_west: bpy.props.EnumProperty(name=strings.PIE_NORTH_WEST_LABEL,
                                      items=const.PIE_ENUMS,
                                      default=const.PIE_ITEMS[4],
                                      update=updateConfiguration)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        box = col.box()
        colBox = box.column(align=True)
        colBox.label(text=strings.PREFS_GENERAL_LABEL)
        colBox.prop(self, "language")
        colBox.prop(self, "panel_location")
        colBox.prop(self, "panel_name")
        colBox.separator()
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
        colBox.label(text=strings.PREFS_KEYMAPS_LABEL)
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
        colBox.prop(self, "vertexGroups_key")
        colBox.prop(self, "blend_key")
        colBox.separator()
        colBox.prop(self, "value_up_key")
        colBox.prop(self, "value_down_key")
        colBox.separator()
        colBox.prop(self, "select_key")
        colBox.prop(self, "deselect_key")
        colBox.prop(self, "clearSelection_key")
        colBox.separator()
        colBox.prop(self, "flood_key")

        box = col.box()

        colBox = box.column(align=True)
        colBox.label(text=strings.PREFS_PIE_LABEL)
        colBox.prop(self, "pie_menu")
        colBox.prop(self, "pieMenu_key")
        colBox.separator()

        colFlow = box.column_flow(columns=3)
        colFlow.separator_spacer()
        colFlow.prop(self, "pie_north", text="")
        colFlow.separator_spacer()

        colFlow = box.column_flow(columns=2)
        colFlow.prop(self, "pie_north_west", text="")
        colFlow.prop(self, "pie_north_east", text="")

        colFlow = box.column_flow(columns=2)
        colFlow.prop(self, "pie_west", text="")
        colFlow.prop(self, "pie_east", text="")

        colFlow = box.column_flow(columns=2)
        colFlow.prop(self, "pie_south_west", text="")
        colFlow.prop(self, "pie_south_east", text="")

        colFlow = box.column_flow(columns=3)
        colFlow.separator_spacer()
        colFlow.prop(self, "pie_south", text="")
        colFlow.separator_spacer()


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

    # Discard the mesh data properties location for the smooth panel
    # which has been introduced in version 2.4 but doesn't work due to
    # context restrictions.
    if not len(getPreferences().panel_location):
        getPreferences().panel_location = "TOOLS"
        updateConfig()


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)
