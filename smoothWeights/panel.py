# <pep8 compliant>

from . import constants as const
from . import language

import bpy

import types


# Get the current language.
strings = language.getLanguage()


CLASS_ITEMS = {}


def hasWeights(context):
    """Return, if the current object is a mesh and has at least one
    vertex group.

    :param context: The current context.
    :type context: bpy.context

    :return: True, if the object is a mesh and has weights.
    :rtype: bool
    """
    obj = context.object
    if (obj is not None and
            obj.type == 'MESH' and
            len(obj.vertex_groups) > 1):
        return True
    return False


def buildPanelClass(attributes):
    """Build the panel class.

    :param attributes: The class attributes as a dictionary.
    :type attributes: dict

    :return: The class instance.
    :rtype: class
    """
    baseClass = bpy.types.Panel

    @classmethod
    def poll(cls, context):
        return hasWeights(context)

    # Create the draw method dynamically
    def draw(self, context):
        hasOrderMap = const.MAP_PROPERTY_NAME in context.object.data

        sw = context.object.smooth_weights

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        if context.object.mode in ['OBJECT', 'WEIGHT_PAINT']:
            row = layout.row()
            row.label(text=strings.PANEL_BRUSH_LABEL)

            box = layout.box()
            col = box.column(align=True)
            col.prop(sw, "curve")
            col.prop(sw, "radius")
            col.prop(sw, "strength")
            col.separator()
            col.prop(sw, "volume")
            col.prop(sw, "volumeRange")
            col.separator()
            col.prop(sw, "useSelection")
            col.prop(sw, "affectSelected")
            col.prop(sw, "ignoreBackside")
            col.prop(sw, "islands")
            col.prop(sw, "ignoreLock")
            col.prop(sw, "normalize")
            col.prop(sw, "oversampling")
            col.separator()
            col.prop(sw, "maxGroups")
            col.prop(sw, "vertexGroups")
            if sw.vertexGroups == "OTHER":
                col.prop(sw, "blend")
            if hasOrderMap:
                col.separator()
                col.prop(sw, "useSymmetry")
            col.separator()
            buttonCol = col.column(align=True)
            buttonCol.scale_y = 1.5
            buttonCol.operator("smoothweights.paint",
                               text=strings.PANEL_BRUSH_LABEL,
                               icon='BRUSH_DATA')
            col.separator()

        row = layout.row()
        row.label(text=strings.PANEL_TOOLS_LABEL)

        box = layout.box()
        col = box.column(align=True)
        if context.object.mode in ['OBJECT', 'WEIGHT_PAINT']:
            col.operator("smoothweights.flood", icon='IMAGE')
            col.separator()
        col.operator("smoothweights.limit_groups", icon='GROUP_VERTEX')
        if hasOrderMap:
            col.separator()
            col.operator("symmetryMap.mirror_weights", icon='MOD_MIRROR')

    # Define the class attributes.
    classAttrs = {key: value for key, value in attributes.items()}
    classAttrs.update({"bl_options": {'DEFAULT_CLOSED'},
                       "poll": poll,
                       "draw": draw})

    # Create the class.
    panelClass = type(const.PANEL_CLASS, (baseClass,), classAttrs)

    return panelClass


def register(area, name):
    """Register the tool panel.
    """
    # Get the class attributes and set the name.
    attrs = const.PANEL_AREAS[area]
    attrs["bl_label"] = name
    if area == "TAB":
        attrs["bl_category"] = name
    # Create the panel class.
    panelClass = buildPanelClass(attrs)
    # Register the panel.
    bpy.utils.register_class(panelClass)
    # Store the class instance for unregistering.
    CLASS_ITEMS[const.PANEL_CLASS] = panelClass


def unregister():
    """Register the tool panel.
    """
    for item in CLASS_ITEMS:
        try:
            bpy.utils.unregister_class(CLASS_ITEMS[item])
        except (NameError, RuntimeError):
            pass
