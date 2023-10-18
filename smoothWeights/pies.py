# <pep8 compliant>

from . import constants as const
from . import preferences as prefs
from . import language

import bpy
from bpy.types import Menu


# Get the current language.
strings = language.getLanguage()


# ----------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------

class SMOOTHWEIGHTS_OT_pieIncreaseGroup(bpy.types.Operator):
    """Operator class for increasing the maximum vertex group count.
    """
    bl_idname = "smoothweights.pie_increase_group"
    bl_label = strings.PIE_GROUP_INCREASE_LABEL
    bl_description = strings.ANN_PIE_GROUP_INCREASE

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        value = context.object.smooth_weights.maxGroups + 1
        context.object.smooth_weights.maxGroups = value
        return {'FINISHED'}


class SMOOTHWEIGHTS_OT_pieDecreaseGroup(bpy.types.Operator):
    """Operator class for decreasing the maximum vertex group count.
    """
    bl_idname = "smoothweights.pie_decrease_group"
    bl_label = strings.PIE_GROUP_DECREASE_LABEL
    bl_description = strings.ANN_PIE_GROUP_DECREASE

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        value = context.object.smooth_weights.maxGroups - 1
        value = value if value >= 0 else 0
        context.object.smooth_weights.maxGroups = value
        return {'FINISHED'}


class SMOOTHWEIGHTS_OT_pieIncreaseSamples(bpy.types.Operator):
    """Operator class for increasing the oversample count.
    """
    bl_idname = "smoothweights.pie_increase_samples"
    bl_label = strings.PIE_SAMPLES_INCREASE_LABEL
    bl_description = strings.ANN_PIE_SAMPLES_INCREASE

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        value = context.object.smooth_weights.oversampling + 1
        context.object.smooth_weights.oversampling = value
        return {'FINISHED'}


class SMOOTHWEIGHTS_OT_pieDecreaseSamples(bpy.types.Operator):
    """Operator class for decreasing the oversample count.
    """
    bl_idname = "smoothweights.pie_decrease_samples"
    bl_label = strings.PIE_SAMPLES_DECREASE_LABEL
    bl_description = strings.ANN_PIE_SAMPLES_DECREASE

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        value = context.object.smooth_weights.oversampling - 1
        if value < 1:
            value = 1
        context.object.smooth_weights.oversampling = value
        return {'FINISHED'}


# ----------------------------------------------------------------------
# Pie Elements
# ----------------------------------------------------------------------

def addVertexGroups(context, pie, *args):
    """Add the layout items for the vertex groups to the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param pie: The pie menu.
    :type pie: bpy.types.Layout.menu_pie
    :param args: Optional arguments.
    :type args: None
    """
    sw = context.object.smooth_weights

    box = pie.box()
    col = box.column()
    row = col.row()
    row.label(text=strings.VERTEX_GROUPS_LABEL)
    row.operator(SMOOTHWEIGHTS_OT_pieDecreaseGroup.bl_idname, text="", icon='REMOVE')
    row.label(text="   {}".format(sw.maxGroups))
    row.operator(SMOOTHWEIGHTS_OT_pieIncreaseGroup.bl_idname, text="", icon='ADD')
    row = col.row()
    row.prop(sw, "vertexGroups", expand=True)
    subRow = col.row()
    subRow.prop(sw, "ignoreLock")
    if sw.vertexGroups == "OTHER":
        subRow.prop(sw, "blend")


def addProperty(context, pie, prop):
    """Add the given property to the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param pie: The pie menu.
    :type pie: bpy.types.Layout.menu_pie
    :param prop: The name of the property.
    :type prop: str
    """
    pie.prop(context.object.smooth_weights, prop)


def addSeparator(context, pie, *args):
    """Add a separator to the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param pie: The pie menu.
    :type pie: bpy.types.Layout.menu_pie
    :param args: Optional arguments.
    :type args: None
    """
    pie.separator()


def addSelection(context, pie, *args):
    """Add the selection items to the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param pie: The pie menu.
    :type pie: bpy.types.Layout.menu_pie
    :param args: Optional arguments.
    :type args: None
    """
    sw = context.object.smooth_weights

    box = pie.box()
    row = box.row()
    row.prop(sw, "useSelection")
    row.prop(sw, "affectSelected")


def addOversampling(context, pie, *args):
    """Add the oversampling items to the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param pie: The pie menu.
    :type pie: bpy.types.Layout.menu_pie
    :param args: Optional arguments.
    :type args: None
    """
    sw = context.object.smooth_weights

    box = pie.box()
    col = box.column()
    col.label(text=strings.OVERSAMPLING_LABEL)
    row = col.row()
    row.operator(SMOOTHWEIGHTS_OT_pieDecreaseSamples.bl_idname, text=" ", icon='REMOVE')
    row.label(text=" {} ".format(sw.oversampling))
    row.operator(SMOOTHWEIGHTS_OT_pieIncreaseSamples.bl_idname, text=" ", icon='ADD')


PIE_ITEMS = {"IGNORE_BACKSIDE": (addProperty, "ignoreBackside"),
             "USE_ISLANDS": (addProperty, "islands"),
             "NORMALIZE": (addProperty, "normalize"),
             "OVERSAMPLING": (addOversampling, "oversampling"),
             "SELECTION": (addSelection, "selection"),
             "USE_SYMMETRY": (addProperty, "useSymmetry"),
             "VERTEX_GROUPS": (addVertexGroups, "vertexGroups"),
             "VOLUME": (addProperty, "volume"),
             "NONE": (addSeparator, None)}


# ----------------------------------------------------------------------
# Pie Menu
# ----------------------------------------------------------------------

def buildPieMenu(context, layout):
    """Create the pie menu.

    :param context: The current context.
    :type context: bpy.context
    :param layout: The layout.
    :type layout: bpy.types.Layout
    """
    pie = layout.menu_pie()

    settings = prefs.getPreferences()

    for area in const.PIE_AREAS:
        listItem = getattr(settings, area)
        func, prop = PIE_ITEMS[listItem]
        func(context, pie, prop)


class SMOOTHWEIGHTS_MT_pie(Menu):
    """Pie menu class.
    """
    bl_idName = "smoothweights.pie"
    bl_label = strings.MENU_SMOOTH_WEIGHTS

    def draw(self, context):
        """Draw the menu.

        :param context: The current context.
        :type context: bpy.context
        """
        buildPieMenu(context, self.layout)


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [SMOOTHWEIGHTS_OT_pieIncreaseGroup,
           SMOOTHWEIGHTS_OT_pieDecreaseGroup,
           SMOOTHWEIGHTS_OT_pieIncreaseSamples,
           SMOOTHWEIGHTS_OT_pieDecreaseSamples,
           SMOOTHWEIGHTS_MT_pie]


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


if __name__ == "__main__":
    register()
