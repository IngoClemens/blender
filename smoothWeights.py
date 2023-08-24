"""
smoothWeights
Copyright (C) 2023, Ingo Clemens, brave rabbit, www.braverabbit.com

    GNU GENERAL PUBLIC LICENSE Version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see <https://www.gnu.org/licenses/>.

------------------------------------------------------------------------

Description:

------------------------------------------------------------------------

Usage:

Requirements:
The mesh needs to have at least two vertex groups for the panel and menu
item to show.

1. Select the mesh in object mode. There is no need to enter weight
   painting mode.
2. From the side panel in the 3D view choose the tool tab.
3. Open the folder "Smooth Weights"
4. Press "Brush".

   or

   From the 3D view main menu choose Object > Smooth Weights.

   or

   From the 3D view Weight Paint menu choose Weights > Smooth Weights.

5. All settings can either be adjusted from the side panel before
   entering the tool or via keymaps while the tool is active.
6. LMB paint over the mesh to smooth the weights.
7. Press Enter to finish the tool or Esc/RMB to cancel.

The default keymaps are:

B: Brush size
   Hold B while dragging the cursor left/right to adjust the size.
   Hold Shift for faster adjustment and Ctrl for slower.
   Make sure to hover over the mesh.
S: Brush strength
   Hold S while dragging the cursor left/right to adjust the strength.
   Hold Shift for faster adjustment and Ctrl for slower.
   Make sure to hover over the mesh.
1/2/3/4: Brush Curve Falloff (None, Linear, Smooth, Narrow)
Q: Use Selection
A: Affect Selected
X: Ignore Backside
L: Ignore Lock
I: Use Islands
N: Normalize
V: Volume (off for surface smoothing)
R: Volume Range
   Hold R while dragging the cursor left/right to adjust the range.
   Hold Shift for faster adjustment and Ctrl for slower.
   Make sure to hover over the mesh.
M: Limit Max Groups
G: Groups
   Hold G while pressing + or - to increase or decrease the number of
   vertex groups.
F: Flood Smooth
Shift + RMB: Frame Change
   Change the current frame by dragging the mouse left or right.
W: Toggle Select mode.
E: Toggle Deselect mode.
C: Clear Selection

All keymaps, except the frame change, are customizable from the add-on
preferences.

While the tool is active the last brush stroke can be undone by pressing
the default key for undo, without any modifiers.
Currently only one stroke can be undone.

------------------------------------------------------------------------

Changelog:

1.0.0 - 2023-08-24
      - Increased brush value precision.
      - Public release.

0.0.6 - 2023-08-23
      - Ignore islands is now enabled for volume mode.
      - Added a selection and deselection mode.
      - Added a keymap for flooding in paint mode.
      - The paint mode undo queue has now a configurable length with a
        preference setting.
      - The tool is now only accessible when in Object or Weight Paint
        mode.

0.0.5 - 2023-08-18
      - Added the ability to drag the current frame while in paint
        mode with Shift + RMB.
      - Added the corresponding keymap to the in-view settings.
      - Fixed, that the brush circle briefly appears at the last
        position when starting a new stroke.
      - Fixed the wrong display of the max groups label in the in-view
        settings.

0.0.4 - 2023-08-18
      - Improvements to the smoothing algorithm.
      - Added the option to ignore backfaces while painting.
      - Included the volume option in the floor operator.
      - Removed the oversampling property, which was needed for the old
        smoothing process.
      - Fixed some issues related to the selection switches.
      - Fixed the strength value which was not working as expected.

0.0.3 - 2023-08-16
      - The tool is now also available in Blender's Weight Paint mode.
      - The paint cursor now shows as a target cross, to match it with
        the regular paint tool.
      - Fixed an undo-paint-related issue when using the flood operator.
      - Fixed the labels in the redo panel of the floor operator.

0.0.2 - 2023-08-16
      - Added a new option to disable any selection-based restriction.
      - Added a single undo operation while in paint mode.
      - Fixed the issue that any transformation affects the
        functionality of the tool.

0.0.1 - 2023-08-15

------------------------------------------------------------------------
"""

bl_info = {"name": "Smooth Weights",
           "author": "Ingo Clemens",
           "version": (0, 1, 0),
           "blender": (3, 6, 0),
           "category": "Rigging",
           "location": "View3D > Object",
           "description": "Smooth mesh weights by averaging neighbouring weights",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/Smooth-Weights",
           "tracker_url": ""}

import blf
import bpy
from bpy_extras import view3d_utils
import bmesh
import gpu
from gpu_extras.batch import batch_for_shader

import math
from mathutils import Vector, kdtree
import time


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

NAME = "smoothWeights"
# The name of the color attribute which stores the current selection.
SELECT_COLOR_ATTRIBUTE = "smoothWeights_selection"

# Switch for smoothing only selected vertices.
AFFECT_SELECTED = True
# The curve options.
CURVE_ITEMS = (("NONE", "None", ""),
               ("LINEAR", "Linear", ""),
               ("SMOOTH", "Smooth", ""),
               ("NARROW", "Narrow", ""))
# The deselection state.
DESELECT = False
# Switch for ignoring backside faces.
IGNORE_BACKSIDE = True
# Switch for ignoring any locked weights.
IGNORE_LOCK = False
# The number of weight group assignments.
MAX_GROUPS = 5
# Normalization switch.
NORMALIZE = True
# The default radius of the brush.
RADIUS = 0.25
# The selection state.
SELECT = False
# The default strength of the brush.
STRENGTH = 1.0
# The tolerance value for matching vertex positions.
TOLERANCE = 1e-6
# Value for skipping evaluation steps.
UNDERSAMPLING = 3
# Switch for handling islands as a continuous mesh.
USE_ISLANDS = False
# Switch for using a limited number of vertex groups.
USE_MAX_GROUPS = True
# Switch for using selected or unselected vertices.
USE_SELECTION = False
# Switch for toggling between a volume-based and a surface-based brush.
VOLUME = False
# The radius multiplier for finding close vertices in volume mode.
VOLUME_RANGE = 0.2

# Keymaps
AFFECTSELECTED_KEY = "A"
CLEARSELECTION_KEY = "C"
DESELECT_KEY = "E"
FLOOD_KEY = "F"
IGNOREBACKSIDE_KEY = "X"
IGNORELOCK_KEY = "L"
ISLANDS_KEY = "I"
MAXGROUPS_KEY = "G"
NORMALIZE_KEY = "N"
RADIUS_KEY = "B"
SELECT_KEY = "W"
USEMAXGROUPS_KEY = "M"
USESELECTION_KEY = "Q"
STRENGTH_KEY = "S"
VALUE_UP_KEY = "PLUS"
VALUE_DOWN_KEY = "MINUS"
VOLUME_KEY = "V"
VOLUMERANGE_KEY = "R"

# Preferences
BRUSH_COLOR = (0.263, 0.723, 0.0)
KEEP_SELECTION = True
SELECTED_COLOR = (0.03, 0.302, 1.0)
SHOW_INFO = True
UNDO_STEPS = 20
UNSELECTED_COLOR = (1.0, 1.0, 1.0)

# Labels
AFFECT_SELECTED_LABEL = "Affect Selected"
CURVE_LABEL = "Curve"
FLOOD_LABEL = "Flood"
IGNORE_BACKSIDE_LABEL = "Ignore Backside"
IGNORE_LOCK_LABEL = "Ignore Lock"
NORMALIZE_LABEL = "Normalize"
USE_ISLANDS_LABEL = "Use Islands"
USE_MAX_GROUPS_LABEL = "Limit Groups"
USE_SELECTION_LABEL = "Use Selection"
MAX_GROUPS_LABEL = "Max Groups"
RADIUS_LABEL = "Radius"
STRENGTH_LABEL = "Strength"
VOLUME_LABEL = "Use Volume"
VOLUME_RANGE_LABEL = "Volume Range"

# Annotations
ANN_AFFECT_SELECTED = "Smooth only the selected vertices"
ANN_BRUSH_COLOR = "Display color for the brush circle (not gamma corrected)"
ANN_CLEAR_SELECTION = "Clear the selection"
ANN_CURVE = "The brush falloff curve"
ANN_DESELECT = "Deselect vertices"
ANN_FLOOD = "Flood smooth the vertex weights"
ANN_IGNORE_BACKSIDE = "Ignore faces which are viewed from the back"
ANN_IGNORE_LOCK = "Ignore the lock status of a vertex group"
ANN_KEEP_SELECTION = "Keep the tool selection vertices as selected vertices after finishing the tool"
ANN_MAX_GROUPS = "The number of vertex groups a vertex can share weights with"
ANN_NORMALIZE = "Normalize the averaged weights to a sum of 1"
ANN_RADIUS = "The brush radius in generic Blender units"
ANN_SELECT = "Select vertices"
ANN_SELECTED_COLOR = "The color for selected vertices"
ANN_SHOW_INFO = "Display all tool settings and keymaps in the 3D view"
ANN_STRENGTH = "The strength of the smoothing stroke"
ANN_UNDO_STEPS = "Number of available undo steps"
ANN_UNSELECTED_COLOR = "The color for unselected vertices"
ANN_USE_ISLANDS = "Limit the smoothing to the current island when in surface mode"
ANN_USE_MAX_GROUPS = "Limit the weighting to a maximum number of vertex groups"
ANN_USE_SELECTION = "Use only selected or unselected vertices for smoothing"
ANN_VALUE_DOWN = "Decrease the maximum vertex groups"
ANN_VALUE_UP = "Increase the maximum vertex groups"
ANN_VOLUME = "Smooth weights within the brush volume. When off the weights are averaged based on linked vertices"
ANN_VOLUME_RANGE = "Scale factor for radius, determining neighboring vertices in volume mode"


# ----------------------------------------------------------------------
# Properties
# ----------------------------------------------------------------------

class SmoothWeights_Properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    affectSelected: bpy.props.BoolProperty(default=AFFECT_SELECTED,
                                           description=ANN_AFFECT_SELECTED)
    curve: bpy.props.EnumProperty(items=CURVE_ITEMS,
                                  default=2,
                                  description=ANN_CURVE)
    deselect: bpy.props.BoolProperty(default=DESELECT,
                                     description=ANN_DESELECT)
    ignoreBackside: bpy.props.BoolProperty(default=IGNORE_BACKSIDE,
                                           description=ANN_IGNORE_BACKSIDE)
    ignoreLock: bpy.props.BoolProperty(default=IGNORE_LOCK,
                                       description=ANN_IGNORE_LOCK)
    islands: bpy.props.BoolProperty(default=USE_ISLANDS,
                                    description=ANN_USE_ISLANDS)
    maxGroups: bpy.props.IntProperty(default=MAX_GROUPS,
                                     min=0,
                                     description=ANN_MAX_GROUPS)
    normalize: bpy.props.BoolProperty(default=NORMALIZE,
                                      description=ANN_NORMALIZE)
    radius: bpy.props.FloatProperty(default=RADIUS,
                                    min=0,
                                    description=ANN_RADIUS)
    strength: bpy.props.FloatProperty(default=STRENGTH,
                                      min=0.001,
                                      max=1,
                                      description=ANN_STRENGTH)
    select: bpy.props.BoolProperty(default=SELECT,
                                   description=ANN_SELECT)
    useMaxGroups: bpy.props.BoolProperty(default=USE_MAX_GROUPS,
                                         description=ANN_USE_MAX_GROUPS)
    useSelection: bpy.props.BoolProperty(default=USE_SELECTION,
                                         description=ANN_USE_SELECTION)
    volume: bpy.props.BoolProperty(default=VOLUME,
                                   description=ANN_VOLUME)
    volumeRange: bpy.props.FloatProperty(default=VOLUME_RANGE,
                                         min=0,
                                         max=1,
                                         description=ANN_VOLUME_RANGE)


# ----------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------

class DrawInfo3D(object):
    """Class for drawing the brush.
    """
    def __init__(self):
        """Variable initialization.
        """
        # The brush center. This is set when the brush is dragged across
        # the surface.
        # When the left mouse button is released the value is reset to
        # None and the circle is not drawn anymore.
        self.center = None
        # The surface normal when dragging.
        self.normal = Vector((1.0, 0.0, 0.0))
        # The draw handler.
        self.handleCircle = None
        self.handleInfo = None

        # The maximum number of groups a vertex currently has.
        self.currentMaxGroups = 0

        # Keys
        self.affectSelected_key = None
        self.clearSelection_key = None
        self.deselect_key = None
        self.ignoreBackside_key = None
        self.ignoreLock_key = None
        self.islands_key = None
        self.maxGroups_key = None
        self.normalize_key = None
        self.radius_key = None
        self.select_key = None
        self.strength_key = None
        self.useMaxGroups_key = None
        self.useSelection_key = None
        self.volume_key = None
        self.volumeRange_key = None

    def drawColor(self):
        """Return the draw color defined in the preferences.

        :return: The drawing color for the brush circle and info.
        :rtype: list
        """
        color = getPreferences().brush_color
        # Gamma-correct the color.
        return [linear_to_srgb(c) for c in color]

    def drawCallback(self, context):
        """Callback for drawing the brush.

        :param context: The current context.
        :type context: bpy.context
        """
        if self.center is None:
            return

        color = self.drawColor()

        # Get the brush settings.
        radius = context.object.smooth_weights.radius

        # The number of points for the brush circle.
        numPoints = 32

        # The default normal for the brush circle.
        baseNormal = Vector((0.0, 0.0, 1.0))
        # Calculate the quaternion to rotate the circle to the surface
        # normal.
        normalQuat = baseNormal.rotation_difference(self.normal)

        circlePoints = []
        for i in range(numPoints):
            angle = 2.0 * math.pi * float(i) / float(numPoints)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 0.0
            # Orient the circle to the normal of the mesh.
            pos = (normalQuat @ Vector((x, y, z))) + self.center
            circlePoints.append(pos)

        # Duplicate the first point to close the circle.
        circlePoints.append(circlePoints[0])

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": circlePoints})
        shader.bind()
        shader.uniform_float("color", (color[0], color[1], color[2], 1.0))
        batch.draw(shader)

    def drawCallbackInfo(self, context):
        """Callback for drawing the brush info.

        :param context: The current context.
        :type context: bpy.context
        """
        fontId = 0

        color = self.drawColor()

        # The font size and positioning depends on the system's pixel
        # size.
        pixelSize = bpy.context.preferences.system.pixel_size
        fontSize = 11 * pixelSize

        # Get the brush settings.
        affectSelected = context.object.smooth_weights.affectSelected
        curve = context.object.smooth_weights.curve
        deselect = context.object.smooth_weights.deselect
        ignoreBackside = context.object.smooth_weights.ignoreBackside
        ignoreLock = context.object.smooth_weights.ignoreLock
        islands = context.object.smooth_weights.islands
        maxGroups = context.object.smooth_weights.maxGroups
        useMaxGroups = context.object.smooth_weights.useMaxGroups
        normalize = context.object.smooth_weights.normalize
        radius = context.object.smooth_weights.radius
        select = context.object.smooth_weights.select
        useSelection = context.object.smooth_weights.useSelection
        strength = context.object.smooth_weights.strength
        volume = context.object.smooth_weights.volume
        volumeRange = context.object.smooth_weights.volumeRange

        curveItems = {'NONE': 1, 'LINEAR': 2, 'SMOOTH': 3, 'NARROW': 4}

        selectState = "Off"
        if select:
            selectState = "Select"
        elif deselect:
            selectState = "Deselect"

        # Show the full tool info.
        if getPreferences().show_info:
            # Draw the settings in the lower left corner of the screen.
            lines = ["{}  {}: {}".format(curveItems[curve], CURVE_LABEL, curve.lower().title()),
                     "{}  {}: {:.3f}".format(self.radius_key, RADIUS_LABEL, radius),
                     "{}  {}: {:.3f}".format(self.strength_key, STRENGTH_LABEL, strength),
                     "",
                     "{}  {}: {}".format(self.useSelection_key, USE_SELECTION_LABEL, "On" if useSelection else "Off"),
                     "{}  {} {}".format(self.affectSelected_key, AFFECT_SELECTED_LABEL, "On" if affectSelected else "Off"),
                     "{}  {}: {}".format(self.ignoreBackside_key, IGNORE_BACKSIDE_LABEL, "On" if ignoreBackside else "Off"),
                     "{}  {}: {}".format(self.ignoreLock_key, IGNORE_LOCK_LABEL, "On" if ignoreLock else "Off"),
                     "{}  {} {}".format(self.islands_key, USE_ISLANDS_LABEL, "On" if islands else "Off"),
                     "{}  {}: {}".format(self.normalize_key, NORMALIZE_LABEL, "On" if normalize else "Off"),
                     "",
                     "{}  {}: {}".format(self.volume_key, VOLUME_LABEL, "On" if volume else "Off"),
                     "{}  {}: {:.3f}".format(self.volumeRange_key, VOLUME_RANGE_LABEL, volumeRange),
                     "",
                     "{}  {}: {}".format(self.useMaxGroups_key, USE_MAX_GROUPS_LABEL, "On" if useMaxGroups else "Off"),
                     "{}  {}: {}".format(self.maxGroups_key, MAX_GROUPS_LABEL, maxGroups),
                     "Current Max Groups: {}".format(self.currentMaxGroups),
                     "",
                     "Selection: {}".format(selectState)]
        # Show only the minimum tool info.
        else:
            lines = ["Mode: {}".format("Smooth" if selectState == "Off" else selectState)]

        lineHeight = fontSize * 1.45
        xPos = 20 * pixelSize
        yPos = 20 * pixelSize
        blf.color(fontId, color[0], color[1], color[2], 1.0)
        for i in reversed(range(len(lines))):
            blf.position(fontId, xPos, yPos, 0)
            blf.draw(fontId, lines[i])
            if len(lines[i]):
                yPos += lineHeight
            else:
                yPos += lineHeight / 2

    def addCircle(self):
        """Add the brush circle to the 3d view and store the handler for
        later removal.
        """
        if not self.handleCircle:
            self.handleCircle = bpy.types.SpaceView3D.draw_handler_add(self.drawCallback,
                                                                       (bpy.context,),
                                                                       'WINDOW',
                                                                       'POST_VIEW')
        self.updateView()

    def removeCircle(self):
        """Remove the brush circle from the 3d view.
        """
        if self.handleCircle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handleCircle, 'WINDOW')
            self.handleCircle = None
            self.updateView()
        self.center = None

    def addInfo(self):
        """Add the brush info to the 3d view and store the handler for
        later removal.
        """
        if not self.handleInfo:
            self.handleInfo = bpy.types.SpaceView3D.draw_handler_add(self.drawCallbackInfo,
                                                                     (bpy.context,),
                                                                     'WINDOW',
                                                                     'POST_PIXEL')
        self.getKeymaps()
        self.updateView()

    def removeInfo(self):
        """Remove the brush info from the 3d view.
        """
        if self.handleInfo:
            bpy.types.SpaceView3D.draw_handler_remove(self.handleInfo, 'WINDOW')
            self.handleInfo = None
            self.updateView()

    def updateView(self):
        """Force a redraw of the current 3d view.
        """
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()

    def getKeymaps(self):
        """Get the current key maps.
        """
        self.affectSelected_key = getPreferences().affectSelected_key.upper()
        self.clearSelection_key = getPreferences().clearSelection_key.upper()
        self.deselect_key = getPreferences().deselect_key.upper()
        self.ignoreBackside_key = getPreferences().ignoreBackside_key.upper()
        self.ignoreLock_key = getPreferences().ignoreLock_key.upper()
        self.islands_key = getPreferences().islands_key.upper()
        self.maxGroups_key = getPreferences().maxGroups_key.upper()
        self.normalize_key = getPreferences().normalize_key.upper()
        self.radius_key = getPreferences().radius_key.upper()
        self.select_key = getPreferences().select_key.upper()
        self.strength_key = getPreferences().strength_key.upper()
        self.useMaxGroups_key = getPreferences().useMaxGroups_key.upper()
        self.useSelection_key = getPreferences().useSelection_key.upper()
        self.volume_key = getPreferences().volume_key.upper()
        self.volumeRange_key = getPreferences().volumeRange_key.upper()


# Global instance.
drawInfo3d = DrawInfo3D()


# ----------------------------------------------------------------------
# Paint Operator
# ----------------------------------------------------------------------

class OBJECT_OT_SmoothWeights(bpy.types.Operator):
    """Operator class for the tool.
    """
    bl_idname = "object.smooth_weights"
    bl_label = "Smooth Weights"
    bl_description = "Drag over a surface to smooth the skin weights"
    bl_options = {'REGISTER', 'UNDO'}

    # True, if the brush is currently active.
    isDragging = False
    # True, if time dragging is active.
    frameDrag = False
    # The time the frame dragging ended. Intended to prohibit cancelling
    # the tool because of the shared RMB.
    frameDragTimer = None
    # The base frame for dragging the time.
    baseFrame = 1

    # The mesh class instance.
    mesh = None
    # The weight lists.
    weights = []
    # The selected vertices when entering the tool for undo.
    prevSelection = None
    # The current vertex selection.
    selection = []
    # The user defined shading mode.
    shadingMode = None
    shadingType = None

    undersamplingSteps = 0
    # The initial position for setting the brush radius.
    adjustPos = None
    # The drag distance when setting the brush radius.
    adjustDist = 1.0
    # The brush size or strength when beginning to set the brush values.
    adjustValue = None
    # The switch for setting the max groups value.
    setMaxGroups = False

    isModal = False

    # Settings
    affectSelected = AFFECT_SELECTED
    curve = "SMOOTH"
    ignoreBackside = IGNORE_BACKSIDE
    ignoreLock = IGNORE_LOCK
    islands = USE_ISLANDS
    maxGroups = MAX_GROUPS
    normalize = NORMALIZE
    radius = RADIUS
    strength = STRENGTH
    useMaxGroups = USE_MAX_GROUPS
    useSelection = USE_SELECTION
    volume = VOLUME
    volumeRange = VOLUME_RANGE

    # Keys
    affectSelected_key = None
    clearSelection_key = None
    deselect_key = None
    flood_key = None
    ignoreBackside_key = None
    ignoreLock_key = None
    islands_key = None
    maxGroups_key = None
    normalize_key = None
    radius_key = None
    select_key = None
    strength_key = None
    useMaxGroups_key = None
    useSelection_key = None
    value_up_key = None
    value_down_key = None
    volume_key = None
    volumeRange_key = None
    undo_key = None

    # ------------------------------------------------------------------
    # General operator methods.
    # ------------------------------------------------------------------

    def execute(self, context):
        """Execute the operator.

        This method is mandatory for displaying the redo panel.

        :param context: The current context.
        :type context: bpy.context
        """
        drawInfo3d.removeCircle()
        drawInfo3d.removeInfo()

        self.isModal = False
        return {'FINISHED'}

    def modal(self, context, event):
        """Modal operator function.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        return self.eventSelector(context, event)

    def invoke(self, context, event):
        """Invoke the operator.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        self.isModal = True
        self.getKeymaps()

        if not context.object:
            self.report({'WARNING'}, "No object selected to place")
            return self.cancel(context)

        context.window.cursor_set("PAINT_CROSS")
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(self.getStatusInfo())

        # Get the brush settings.
        self.affectSelected = context.object.smooth_weights.affectSelected
        self.curve = context.object.smooth_weights.curve
        self.ignoreBackside = context.object.smooth_weights.ignoreBackside
        self.ignoreLock = context.object.smooth_weights.ignoreLock
        self.islands = context.object.smooth_weights.islands
        self.maxGroups = context.object.smooth_weights.maxGroups
        self.normalize = context.object.smooth_weights.normalize
        self.radius = context.object.smooth_weights.radius
        self.strength = context.object.smooth_weights.strength
        self.useMaxGroups = context.object.smooth_weights.useMaxGroups
        self.useSelection = context.object.smooth_weights.useSelection
        self.volume = context.object.smooth_weights.volume
        self.volumeRange = context.object.smooth_weights.volumeRange

        # Initialize the skin mesh.
        self.mesh = Mesh(context.object)

        # Transfer the current selection to the selection color.
        self.mesh.setSelection(self.mesh.selectedVertices)

        # If the current selection should be used for smoothing, store
        # the current shading mode and switch to selection display.
        if self.useSelection:
            self.setSelectionMode(context, active=True)

        # Add the draw handler for the brush info.
        drawInfo3d.currentMaxGroups = self.mesh.currentMaxGroups
        drawInfo3d.addInfo()

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        """Reset and cancel the current operation.

        :param context: The current context.
        :type context: bpy.context

        :return: The enum for cancelling the operator.
        :rtype: enum
        """
        self.isModal = False

        # Reset the weights and selection.
        if context.object:
            # Reset the weights.
            # Process only the weights which have been smoothed.
            indices = [i for i, vertex in enumerate(self.mesh.obj.data.vertices) if self.mesh.cancelIndices[i]]
            self.mesh.setWeightsFromVertexList(indices, self.mesh.cancelWeights)

        # Reset the operator.
        self.reset(context)

        return {'CANCELLED'}

    def reset(self, context):
        """Reset the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        self.isModal = False

        # Remove the selection colors.
        self.mesh.deleteColorAttribute()

        self.mesh.reset()

        # Reset the selection modes.
        context.object.smooth_weights.select = False
        context.object.smooth_weights.deselect = False
        self.setSelectionMode(context, active=False)

        self.isDragging = False
        context.workspace.status_text_set(None)

        # Remove the draw handler.
        drawInfo3d.removeCircle()
        drawInfo3d.removeInfo()

    def eventSelector(self, context, event):
        """Event-based switches to define the current action.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        select = context.object.smooth_weights.select
        deselect = context.object.smooth_weights.deselect

        # --------------------------------------------------------------
        # Smooth and Selection
        # --------------------------------------------------------------

        # Set, if the tool should enter or leave dragging mode.
        if event.type == 'LEFTMOUSE' and not isModifier(event):
            if not self.isDragging:
                self.isDragging = True

                # Make sure that the object is in Object or WEIGHT_PAINT
                # mode.
                if self.mesh.obj.mode not in ['OBJECT', 'WEIGHT_PAINT']:
                    bpy.ops.object.mode_set(mode='OBJECT')
                # Make sure the color attribute is current.
                self.mesh.updateColorAttribute()
                # Update the keymaps.
                self.getKeymaps()
                # Update the current tool settings for the mesh class.
                self.updateSettings()
                # Init the undo list.
                # If the maximum size of the undo list has been reached
                # remove the last element.
                if getPreferences().undo_steps <= len(self.mesh.undoIndices):
                    lastItem = len(self.mesh.undoIndices) - 1
                    self.mesh.undoIndices.pop(lastItem)
                    self.mesh.undoWeights.pop(lastItem)
                self.mesh.undoIndices.insert(0, [])
                self.mesh.undoWeights.insert(0, [None] * self.mesh.numVertices())
                drawInfo3d.addCircle()

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # If the brush action has been performed refresh the point
            # positions.
            if self.isDragging:
                self.mesh.getDeformedPointPositions()

            self.isDragging = False
            # Remove the brush circle.
            drawInfo3d.removeCircle()

        # Perform the smoothing or selecting action.
        if event.type == 'MOUSEMOVE' and self.isDragging:
            # Skip evaluation steps to improve performance.
            self.undersamplingSteps += 1
            if self.undersamplingSteps < UNDERSAMPLING:
                return {'RUNNING_MODAL'}
            self.undersamplingSteps = 0

            rangeVerts = self.getVerticesInRange(context, event)
            if rangeVerts is None:
                return {'RUNNING_MODAL'}

            if not select and not deselect:
                self.mesh.performSmooth(rangeVerts)
            else:
                # Paint selection only if the selection should be used.
                if self.useSelection:
                    if select:
                        self.paintSelect(rangeVerts)
                    elif deselect:
                        self.paintDeselect(rangeVerts)

        # --------------------------------------------------------------
        # Current Frame
        # --------------------------------------------------------------

        if event.type == 'RIGHTMOUSE' and event.shift:
            if event.value == 'PRESS':
                self.frameDrag = True

        if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            self.frameDrag = False
            self.adjustPos = None
            self.frameDragTimer = time.time()
            self.mesh.getDeformedPointPositions()

        if event.type == 'MOUSEMOVE' and self.frameDrag:
            # Skip evaluation steps to improve performance.
            self.undersamplingSteps += 1
            if self.undersamplingSteps < UNDERSAMPLING:
                return {'RUNNING_MODAL'}
            self.undersamplingSteps = 0

            self.setCurrentFrame(context, event)
            return {'RUNNING_MODAL'}

        '''
        # Draw the circle when the mouse moves.
        # Problem: The circle stays in the 3d view during scene
        # navigation. To implement off-object drawing it's required to
        # find out when scene navigation occurs.
        if event.type == "MOUSEMOVE":
            viewOrigin, viewVector, vector3d = self.mouse3d(context, event)
            drawInfo3d.center = viewOrigin + vector3d
            drawInfo3d.normal = normal
            drawInfo3d.updateView()
        '''

        # --------------------------------------------------------------
        # Toggles
        # --------------------------------------------------------------

        # Affect selected
        if event.type == self.affectSelected_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.affectSelected
            context.object.smooth_weights.affectSelected = value
            self.affectSelected = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Use Selection
        if event.type == self.useSelection_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.useSelection
            context.object.smooth_weights.useSelection = value
            self.useSelection = value
            if value:
                self.setSelectionMode(context, active=True)
            else:
                self.setSelectionMode(context, active=False)
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Curve
        if event.type in ['ONE', 'TWO', 'THREE', 'FOUR'] and event.value == 'PRESS':
            values = {'ONE': 'NONE', 'TWO': 'LINEAR', 'THREE': 'SMOOTH', 'FOUR': 'NARROW'}
            context.object.smooth_weights.curve = values[event.type]
            self.curve = values[event.type]
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Ignore backside
        if event.type == self.ignoreBackside_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.ignoreBackside
            context.object.smooth_weights.ignoreBackside = value
            self.ignoreBackside = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Ignore lock
        if event.type == self.ignoreLock_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.ignoreLock
            context.object.smooth_weights.ignoreLock = value
            self.ignoreLock = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Radius and strength
        if event.type in [self.radius_key, self.strength_key, self.volumeRange_key]:
            self.setBrushValues(context, event)
            self.updateSettings()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Volume
        if event.type == self.volume_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.volume
            context.object.smooth_weights.volume = value
            self.volume = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Use islands
        if event.type == self.islands_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.islands
            context.object.smooth_weights.islands = value
            self.islands = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Normalize
        if event.type == self.normalize_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.normalize
            context.object.smooth_weights.normalize = value
            self.normalize = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Max groups
        if event.type == self.useMaxGroups_key and event.value == 'PRESS':
            value = not context.object.smooth_weights.useMaxGroups
            context.object.smooth_weights.useMaxGroups = value
            self.useMaxGroups = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.maxGroups_key:
            if event.value == 'PRESS':
                self.setMaxGroups = True
            elif event.value == 'RELEASE':
                self.setMaxGroups = False

        if event.type == self.value_up_key and event.value == 'PRESS' and self.setMaxGroups:
            value = context.object.smooth_weights.maxGroups + 1
            context.object.smooth_weights.maxGroups = value
            self.maxGroups = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.value_down_key and event.value == 'PRESS' and self.setMaxGroups:
            value = context.object.smooth_weights.maxGroups - 1
            if value < 1:
                value = 1
            context.object.smooth_weights.maxGroups = value
            self.maxGroups = value
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if self.setMaxGroups:
            return {'RUNNING_MODAL'}

        # Flood
        if event.type == self.flood_key and event.value == 'PRESS':
            self.mesh.floodSmooth(useSelection=self.useSelection,
                                  affectSelected=self.affectSelected,
                                  useColorAttr=True,
                                  strength=self.strength)
            self.updateSettings()
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Selection
        if event.type == self.select_key and event.value == 'PRESS':
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.smooth_weights.select = not context.object.smooth_weights.select
            context.object.smooth_weights.deselect = False
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.deselect_key and event.value == 'PRESS':
            bpy.ops.object.mode_set(mode='OBJECT')
            context.object.smooth_weights.deselect = not context.object.smooth_weights.deselect
            context.object.smooth_weights.select = False
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.clearSelection_key and event.value == 'PRESS':
            self.mesh.clearSelection()
            return {'RUNNING_MODAL'}

        # Undo
        if event.type == self.undo_key and event.value == 'PRESS':
            self.mesh.undoStroke()
            return {'RUNNING_MODAL'}

        # --------------------------------------------------------------
        # Exit
        # --------------------------------------------------------------

        # End the operator.
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            # Match the vertex selection with the selection colors.
            if getPreferences().keep_selection:
                self.mesh.colorToSelection()
            self.reset(context)
            return {'FINISHED'}

        # Cancel the operator.
        if event.type in {'RIGHTMOUSE', 'ESC'} and not isModifier(event):
            if event.type == 'ESC':
                return self.cancel(context)
            else:
                # If no frame dragging has been performed, cancel.
                if self.frameDragTimer is None:
                    return self.cancel(context)
                else:
                    duration = time.time() - self.frameDragTimer
                    # If a safe time passed, exit the tool.
                    # Necessary to prevent that the tool is cancelled
                    # after releasing the RMB for frame dragging.
                    if duration > 0.2:
                        return self.cancel(context)
                    else:
                        return {'RUNNING_MODAL'}

        # --------------------------------------------------------------
        # Passing
        # --------------------------------------------------------------

        # Allow for navigation while not dragging to smooth.
        if not self.isDragging and not self.frameDrag:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    # ------------------------------------------------------------------
    # Brush position and settings
    # ------------------------------------------------------------------

    def mouse3d(self, context, event):
        """Return the 3d position of the mouse and the view vector.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event

        :return: The view origin, the view vector and the 3d position of
                 the mouse cursor as a tuple.
        :rtype: tuple(Vector, Vector, Vector)
        """
        region = context.region
        regionView3d = context.region_data
        viewPos = event.mouse_region_x, event.mouse_region_y

        # Convert the screen position of the cursor to a world view
        # position and vector.
        # By default, the vector is already normalized.
        viewVector = view3d_utils.region_2d_to_vector_3d(region, regionView3d, viewPos)
        viewOrigin = view3d_utils.region_2d_to_origin_3d(region, regionView3d, viewPos)

        position3d = view3d_utils.region_2d_to_vector_3d(region, regionView3d, viewPos)

        return viewOrigin, viewVector, position3d

    def castViewRay(self, context, event):
        """Cast a ray from the current view position into the scene and
        return the hit data if the hit object matches the context
        object.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event

        :return: A tuple with the world hit position, the normal, the
                 face index, the hit object and the view origin.
                 None, if nothing has been hit or the object doesn't
                 match.
        :rtype: tuple(Vector, Vector, int, bpy.types.Object, Vector)
                or None
        """
        viewOrigin, viewVector, position3d = self.mouse3d(context, event)

        # Cast a ray into the view and return the hit object and related
        # data.
        result, pos, normal, index, obj, mat = context.scene.ray_cast(context.view_layer.depsgraph,
                                                                      viewOrigin,
                                                                      viewVector)

        # Discontinue if no intersection can be found or if the
        # intersected object is not the current object.
        backside = self.ignoreBackside and isBackface(viewVector, normal)
        if not result or obj != context.object or backside:
            return

        return pos, normal, index, obj, viewOrigin

    def getVerticesInRange(self, context, event):
        """Return a list of the vertices and their data which are inside
        the brush radius for processing.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event

        :return: A list with tuples containing the vertex index, the
                 distance and the opposite boundary index.
                 None, if the closest index cannot be found.
        :rtype: list(int, float, int/None) or None
        """
        # Cast a ray into the view and return the hit object and related
        # data.
        result = self.castViewRay(context, event)
        if result is None:
            return
        pos, normal, index, obj, viewOrigin = result

        # Get the vertex which is closest to the brush center.
        closestIndex, closestDistance = self.mesh.getClosestFaceVertex(pos, index, self.radius)

        if closestIndex is None:
            return

        if self.volume:
            radiusVerts = self.mesh.getVerticesInVolume(pos, self.radius, local=False)
        else:
            radiusVerts = self.mesh.getVerticesOnSurface(pos, closestIndex, self.radius)

        drawInfo3d.center = pos
        drawInfo3d.normal = normal
        drawInfo3d.updateView()

        return radiusVerts

    def setBrushValues(self, context, event):
        """Set the brush radius or strength.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        # Initialize setting the brush radius or strength.
        if event.value == 'PRESS' and self.adjustPos is None:
            # Cast a ray into the view and return the hit object and
            # related data.
            result = self.castViewRay(context, event)
            if result is None:
                return
            pos, normal, index, obj, viewOrigin = result
            # Define the adjust distance to the mesh which controls the
            # sensitivity of the adjustment.
            self.adjustDist = (pos - viewOrigin).length
            # Store the initial position to calculate the distance of
            # the mouse movement.
            self.adjustPos = Vector((event.mouse_x, event.mouse_y))
            # Store the initial adjust values.
            if event.type == self.radius_key:
                self.adjustValue = self.radius
            elif event.type == self.strength_key:
                self.adjustValue = self.strength
            else:
                self.adjustValue = self.volumeRange
            self.adjustValue = round(self.adjustValue, 3)

            # Draw the brush circle at the initial position when
            # starting to set the values.
            # The circle doesn't need to move with the cursor.
            drawInfo3d.center = pos
            drawInfo3d.normal = normal
            drawInfo3d.addCircle()
        elif event.value == 'RELEASE':
            # Reset the position to be able to start over.
            self.adjustPos = None
            drawInfo3d.removeCircle()
            return

        if self.adjustPos is None:
            return

        # Adjust the movement speed depending on the view distance to
        # the mesh.
        speed = pow(0.025 * self.adjustDist, 0.9)

        # Adjust the speed depending on the modifier key.
        if event.shift:
            speed *= 1.25
        elif event.ctrl:
            speed *= 0.25

        # Calculate the amount of cursor movement.
        currentPos = Vector((event.mouse_x, event.mouse_y))
        deltaPos = currentPos - self.adjustPos
        adjustDist = deltaPos.x * speed

        # Calculate the value based on the start value and the cursor
        # distance.
        value = self.adjustValue + adjustDist * speed
        # Limit the value range.
        value = value if value > 0.0 else 0.001
        if event.type in ['S', 'R']:
            value = 1.0 if value > 1.0 else value

        value = round(value, 3)

        if event.type == self.radius_key:
            context.object.smooth_weights.radius = value
            self.radius = value
        elif event.type == self.strength_key:
            context.object.smooth_weights.strength = value
            self.strength = value
        else:
            context.object.smooth_weights.volumeRange = value
            self.volumeRange = value

        # Update the brush settings info and circle.
        drawInfo3d.updateView()

    def setCurrentFrame(self, context, event):
        """Set the current frame based on the mouse drag distance.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        # Initialize.
        if self.adjustPos is None:
            # Store the initial position to calculate the distance of
            # the mouse movement.
            self.adjustPos = Vector((event.mouse_x, event.mouse_y))
            self.baseFrame = context.scene.frame_current

        # Calculate the amount of cursor movement.
        currentPos = Vector((event.mouse_x, event.mouse_y))
        deltaPos = int((currentPos - self.adjustPos)[0] * 0.05)

        bpy.context.scene.frame_set(self.baseFrame + deltaPos)

    def updateSettings(self):
        """Transfer the current tool settings to the instanced mesh
        class.
        """
        self.mesh.affectSelected = self.affectSelected
        self.mesh.curve = self.curve
        self.mesh.ignoreBackside = self.ignoreBackside
        self.mesh.ignoreLock = self.ignoreLock
        self.mesh.islands = self.islands
        self.mesh.maxGroups = self.maxGroups
        self.mesh.normalize = self.normalize
        self.mesh.radius = self.radius
        self.mesh.strength = self.strength
        self.mesh.useMaxGroups = self.useMaxGroups
        self.mesh.useSelection = self.useSelection
        self.mesh.volume = self.volume
        self.mesh.volumeRange = self.volumeRange

    def getKeymaps(self):
        """Get the current key maps.
        """
        self.affectSelected_key = getPreferences().affectSelected_key.upper()
        self.clearSelection_key = getPreferences().clearSelection_key.upper()
        self.deselect_key = getPreferences().deselect_key.upper()
        self.flood_key = getPreferences().flood_key.upper()
        self.ignoreBackside_key = getPreferences().ignoreBackside_key.upper()
        self.ignoreLock_key = getPreferences().ignoreLock_key.upper()
        self.islands_key = getPreferences().islands_key.upper()
        self.maxGroups_key = getPreferences().maxGroups_key.upper()
        self.normalize_key = getPreferences().normalize_key.upper()
        self.radius_key = getPreferences().radius_key.upper()
        self.select_key = getPreferences().select_key.upper()
        self.strength_key = getPreferences().strength_key.upper()
        self.useMaxGroups_key = getPreferences().useMaxGroups_key.upper()
        self.useSelection_key = getPreferences().useSelection_key.upper()
        self.value_up_key = getPreferences().value_up_key.upper()
        self.value_down_key = getPreferences().value_down_key.upper()
        self.volume_key = getPreferences().volume_key.upper()
        self.volumeRange_key = getPreferences().volumeRange_key.upper()

        # Get the undo keymap.
        config = bpy.context.window_manager.keyconfigs.default.keymaps
        item = config["Screen"].keymap_items.get("ed.undo")
        if item:
            self.undo_key = item.type
        else:
            self.undo_key = 'Z'

    def getStatusInfo(self):
        """Return the string for the status info.
        """
        up = "+" if self.value_up_key == 'PLUS' else self.value_up_key
        down = "-" if self.value_down_key == 'MINUS' else self.value_down_key

        lines = ["LMB-Drag: Smooth",
                 "{}: {}".format(self.radius_key, RADIUS_LABEL),
                 "{}: {}".format(self.strength_key, STRENGTH_LABEL),
                 "Ctrl+{}/{}/{}: Slow".format(self.radius_key, self.strength_key, self.volumeRange_key),
                 "Shift+{}/{}/{}: Fast".format(self.radius_key, self.strength_key, self.volumeRange_key),
                 "{}: {}".format(self.useSelection_key, USE_SELECTION_LABEL),
                 "{}: {}".format(self.affectSelected_key, AFFECT_SELECTED_LABEL),
                 "{}: {}".format(self.ignoreBackside_key, IGNORE_BACKSIDE_LABEL),
                 "{}: {}".format(self.ignoreLock_key, IGNORE_LOCK_LABEL),
                 "{}: {}".format(self.normalize_key, NORMALIZE_LABEL),
                 "{}: {}".format(self.volume_key, VOLUME_LABEL),
                 "{}: {}".format(self.islands_key, USE_ISLANDS_LABEL),
                 "{}: {}".format(self.useMaxGroups_key, USE_MAX_GROUPS_LABEL),
                 "{}: {} {}/{}".format(self.maxGroups_key, MAX_GROUPS_LABEL, up, down),
                 "{}: Toggle Select".format(self.select_key),
                 "{}: Toggle Deselect".format(self.deselect_key),
                 "{}: Clear Selection".format(self.clearSelection_key),
                 "{}: {}".format(self.flood_key, FLOOD_LABEL),
                 "Shift+RMB-Drag: Change Time",
                 "Esc/RMB: Cancel"]

        return ", ".join(lines)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def setSelectionMode(self, context, active=True):
        """Enable or disable the selection mode and change the shading
        type of the current view accordingly.

        :param context: The current context.
        :type context: bpy.context
        :param active: True, if the selection mode should be activated.
        :type active: bool
        """
        bpy.ops.object.mode_set(mode='OBJECT')
        if active:
            # Store the current shading mode.
            self.shadingMode = context.space_data.shading.type
            self.shadingType = context.space_data.shading.color_type
            context.space_data.shading.type = 'SOLID'
            context.space_data.shading.color_type = 'VERTEX'
        else:
            # Set the shaing mode and type only if it has been stored
            # before.
            if self.shadingMode is not None:
                context.space_data.shading.type = self.shadingMode
            if self.shadingType is not None:
                context.space_data.shading.color_type = self.shadingType

    def paintSelect(self, vertData):
        """Set the selection color for all given vertices.

        :param vertData: The list with vertex data from the brush range.
        :type vertData: list(tuple(int, float, int/None))
        """
        indices = [index for index, dist, v in vertData]
        self.mesh.setSelection(indices)

    def paintDeselect(self, vertData):
        """Remove the selection color for all given vertices.

        :param vertData: The list with vertex data from the brush range.
        :type vertData: list(tuple(int, float, int/None))
        """
        indices = [index for index, dist, v in vertData]
        self.mesh.removeSelection(indices)


# ----------------------------------------------------------------------
# Flood Operator
# ----------------------------------------------------------------------

class OBJECT_OT_SmoothWeightsFlood(bpy.types.Operator):
    """Operator class for flood-smoothing the object's weights.
    """
    bl_idname = "object.smooth_weights_flood"
    bl_label = "Flood Smooth Weights"
    bl_description = "Smooth the weights of all selected or unselected vertices"
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty(name=RADIUS_LABEL,
                                    default=RADIUS,
                                    min=0,
                                    description=ANN_RADIUS)
    strength: bpy.props.FloatProperty(name=STRENGTH_LABEL,
                                      default=STRENGTH,
                                      min=0.001,
                                      max=1,
                                      description=ANN_STRENGTH)
    useSelection: bpy.props.BoolProperty(name=USE_SELECTION_LABEL,
                                         default=USE_SELECTION,
                                         description=ANN_USE_SELECTION)
    affectSelected: bpy.props.BoolProperty(name=AFFECT_SELECTED_LABEL,
                                           default=AFFECT_SELECTED,
                                           description=ANN_AFFECT_SELECTED)
    ignoreLock: bpy.props.BoolProperty(name=IGNORE_LOCK_LABEL,
                                       default=IGNORE_LOCK,
                                       description=ANN_IGNORE_LOCK)
    normalize: bpy.props.BoolProperty(name=NORMALIZE_LABEL,
                                      default=NORMALIZE,
                                      description=ANN_NORMALIZE)
    useMaxGroups: bpy.props.BoolProperty(name=USE_MAX_GROUPS_LABEL,
                                         default=USE_MAX_GROUPS,
                                         description=ANN_USE_MAX_GROUPS)
    maxGroups: bpy.props.IntProperty(name=MAX_GROUPS_LABEL,
                                     default=MAX_GROUPS,
                                     min=0,
                                     description=ANN_MAX_GROUPS)
    volume: bpy.props.BoolProperty(name=VOLUME_LABEL,
                                   default=VOLUME,
                                   description=ANN_VOLUME)
    volumeRange: bpy.props.FloatProperty(name=VOLUME_RANGE_LABEL,
                                         default=VOLUME_RANGE,
                                         min=0.001,
                                         max=1,
                                         description=ANN_VOLUME_RANGE)

    mesh = None
    prevSelection = None
    redo = True

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        # When redoing, set the object properties to the operator
        # properties. Setting the properties only after execution alone
        # doesn't seem to work for using the redo panel and adjusting
        # the settings.
        if self.redo:
            self.setSettings(context)

        # Initialize the skin mesh.
        self.mesh = Mesh(context.object)

        self.mesh.floodSmooth(useSelection=self.useSelection,
                              affectSelected=self.affectSelected,
                              useColorAttr=False,
                              strength=self.strength)

        # Copy the settings to the object properties.
        self.setSettings(context)
        # Mark the operator ready for redo.
        self.redo = True

        return {'FINISHED'}

    def cancel(self, context):
        """Reset and cancel the current operation.

        :param context: The current context.
        :type context: bpy.context

        :return: The enum for cancelling the operator.
        :rtype: enum
        """
        # Reset the weights and selection.
        if context.object:
            # Reset the weights.
            # Process only the weights which have been smoothed.
            indices = [i for i, vertex in enumerate(self.mesh.obj.data.vertices) if self.mesh.cancelIndices[i]]
            self.mesh.setWeightsFromVertexList(indices, self.mesh.cancelWeights)

        # Reset the mesh.
        self.mesh.reset()

        return {'CANCELLED'}

    def invoke(self, context, event):
        """Invoke the operator.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        self.affectSelected = context.object.smooth_weights.affectSelected
        self.ignoreLock = context.object.smooth_weights.ignoreLock
        self.maxGroups = context.object.smooth_weights.maxGroups
        self.normalize = context.object.smooth_weights.normalize
        self.radius = context.object.smooth_weights.radius
        self.strength = context.object.smooth_weights.strength
        self.useMaxGroups = context.object.smooth_weights.useMaxGroups
        self.useSelection = context.object.smooth_weights.useSelection
        self.volume = context.object.smooth_weights.volume
        self.volumeRange = context.object.smooth_weights.volumeRange
        # Set the redo flag to False to indicate that the settings
        # should be taken from the global object properties.
        self.redo = False
        return self.execute(context)

    def setSettings(self, context):
        """Copy the settings to the object properties.

        :param context: The current context.
        :type context: bpy.context
        """
        context.object.smooth_weights.affectSelected = self.affectSelected
        context.object.smooth_weights.ignoreLock = self.ignoreLock
        context.object.smooth_weights.maxGroups = self.maxGroups
        context.object.smooth_weights.normalize = self.normalize
        context.object.smooth_weights.radius = self.radius
        context.object.smooth_weights.strength = self.strength
        context.object.smooth_weights.useMaxGroups = self.useMaxGroups
        context.object.smooth_weights.useSelection = self.useSelection
        context.object.smooth_weights.volume = self.volume
        context.object.smooth_weights.volumeRange = self.volumeRange


# ----------------------------------------------------------------------
# Mesh Class
# ----------------------------------------------------------------------

class Mesh(object):
    """Class for evaluating the current mesh and storing relevant data
    for the smoothing process.
    """

    def __init__(self, obj):
        """Initialize.
        """
        # Set the object mode.
        # If the object is in edit mode the depsgraph evaluation will
        # fail and cause a crash.
        if obj.mode not in ['OBJECT', 'WEIGHT_PAINT']:
            bpy.ops.object.mode_set(mode='OBJECT')

        self.obj = obj
        self.mat = obj.matrix_world

        self.bm = bmesh.new()
        self.bm.from_mesh(obj.data)
        self.bm.verts.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        # The tool settings.
        self.affectSelected = self.obj.smooth_weights.affectSelected
        self.curve = self.obj.smooth_weights.curve
        self.ignoreLock = self.obj.smooth_weights.ignoreLock
        self.islands = self.obj.smooth_weights.islands
        self.maxGroups = self.obj.smooth_weights.maxGroups
        self.normalize = self.obj.smooth_weights.normalize
        self.radius = self.obj.smooth_weights.radius
        self.strength = self.obj.smooth_weights.strength
        self.useMaxGroups = self.obj.smooth_weights.useMaxGroups
        self.useSelection = self.obj.smooth_weights.useSelection
        self.volume = self.obj.smooth_weights.volume
        self.volumeRange = self.obj.smooth_weights.volumeRange

        self.groupLocks = self.locks()
        self.numGroups = len(self.allVertexGroups())

        # The maximum number of groups a vertex currently has.
        self.currentMaxGroups = 0

        # The color value and channel index to use as the selection
        # identifier.
        self.colorValue = 0.0
        self.colorIndex = 0

        # Get the current selection.
        self.selectedVertices = None
        self.getCurrentSelection()

        # Get the selection color attribute.
        self.userColorAttr = None
        self.selectionColors = self.getColorAttribute()
        # Store the color identifiers.
        self.setColorIdentifier()

        # Get the deformed positions.
        self.pointsDeformed = None
        self.getDeformedPointPositions()

        # Get the current weights.
        self.cancelWeights = None
        self.weights = self.allVertexWeights()

        # The list storing if a vertex has been smoothed.
        self.cancelIndices = None
        self.initSmoothed()

        # The weights undo list.
        self.undoWeights = []
        self.undoIndices = []

        self.kdLocal = self.kdTree()
        self.kdDeformed = self.kdTree(local=False)

    def reset(self):
        """Free the bmesh memory.
        """
        self.bm.free()

    def numVertices(self):
        """Return the number of vertices for the current mesh.

        :return: The number of vertices.
        :rtype: int
        """
        return len(self.obj.data.vertices)

    def connectedVertices(self, index):
        """Return the list of vertices which are connected to the given
        index.

        :param index: The vertex index.
        :type index: int

        :return: A list with the connected vertex indices.
        :rtype: list(int)
        """
        verts = []
        vertex = self.bm.verts[index]
        for edge in vertex.link_edges:
            verts.append(edge.other_vert(vertex).index)
        return verts

    def getDeformedPointPositions(self):
        """Get the deformed positions.
        """
        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        # If the object is in edit mode the depsgraph evaluation will
        # fail and cause a crash.
        bpy.ops.object.mode_set(mode='OBJECT')
        self.pointsDeformed = self.deformedPointPositions()
        # Reset the object's mode.
        bpy.ops.object.mode_set(mode=mode)

    def getCurrentSelection(self):
        """Get the current vertex selection for the selection tool and
        define the list which indicates the affected status for
        smoothing.

        This gets called when initializing the tool with the current
        mesh as well as when toggling the Affect Selected property.
        """
        self.selectedVertices = self.vertexSelection()

    def vertexSelection(self):
        """Return a list with the currently selected vertex indices.

        :return: A list with selected vertex indices.
        :rtype: list(int)
        """
        indices = []
        for vert in self.obj.data.vertices:
            if vert.select:
                indices.append(vert.index)
        return indices

    def deformedPointPositions(self):
        """Return a list with the deformed point positions rather than
        the local coordinates, by evaluating the despgraph.

        :return: A list with the deformed point positions.
        :rtype: list(Vector)
        """
        points = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        objEval = self.obj.evaluated_get(depsgraph)
        for i, vert in enumerate(self.bm.verts):
            pos = self.mat @ objEval.data.vertices[i].co.copy()
            points.append(pos)
        depsgraph.update()
        return points

    def selectVertices(self, indices):
        """Select the vertices with the given indices.

        For selecting vertices for undo.

        :param indices: The list of vertex indices to select.
        :type indices: list(int)

        :param indices: The list of vertex indices to select.
        :type indices: list(int)
        """
        # Store the current mode.
        mode = self.obj.mode
        # Switch to edit mode to deselect all vertices.
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        for index in indices:
            self.obj.data.vertices[index].select = True

        # Reset the object's mode.
        bpy.ops.object.mode_set(mode=mode)

    def allVertexGroups(self):
        """Return a list with the names of all vertex groups.

        :return: A list with the vertex group names.
        :rtype: list(str)
        """
        return [i.name for i in self.obj.vertex_groups]

    def locks(self):
        """Return a list with the lock state of all vertex groups.

        :return: A list with the vertex group locks.
        :rtype: list(bool)
        """
        return [i.lock_weight for i in self.obj.vertex_groups]

    def isLocked(self, groupIndex):
        """Return, if the group with the given index is locked, while
        considering to ignore locks.

        :param groupIndex: The vertex group index.
        :type groupIndex: int

        :return: True, if the group is considered to be locked.
        :rtype: bool
        """
        return self.groupLocks[groupIndex] and not self.ignoreLock

    def vertexGroups(self, index):
        """Return a list with the vertex groups indices which influence
        the given vertex.

        :param index: The vertex index.
        :type index: int

        :return: A list with the vertex group indices for the vertex.
        :rtype: list(int)
        """
        indices = []
        for i, element in self.obj.data.vertices[index].groups.items():
            indices.append(self.obj.data.vertices[index].groups[i].group)
        return indices

    def allVertexWeights(self):
        """Return all weights for all vertices.

        :return: A list with all weights for all vertices.
        :rtype: list(list(tuple(float, int)))
        """
        w = [None] * self.numVertices()
        self.cancelWeights = [None] * self.numVertices()
        for i in range(self.numVertices()):
            data = self.vertexWeights(i)
            w[i] = data
            # Copy the weight data for undo.
            # This is much faster than having to copy the complete
            # weight list later via deepcopy().
            self.cancelWeights[i] = data.copy()
        return w

    def vertexWeights(self, index):
        """Return a list with the vertex groups weights for the given
        vertex.

        :param index: The vertex index.
        :type index: int

        :return: A full list with the vertex weights and the group index
                 for all vertex groups.
        :rtype: list(tuple(float, int))
        """
        w = []
        for i, element in self.obj.data.vertices[index].groups.items():
            value = self.obj.data.vertices[index].groups[i].weight
            groupId = self.obj.data.vertices[index].groups[i].group
            w.append((value, groupId))

        # Update the current max number of vertex groups.
        if len(w) > self.currentMaxGroups:
            self.currentMaxGroups = len(w)

        weightList = [(0.0, i) for i in range(self.numGroups)]

        for item in w:
            value, groupId = item
            weightList[groupId] = value, groupId

        return weightList

    def setVertexWeight(self, index, groupId, weight):
        """Set the weight for the given vertex and vertex group.

        :param index: The vertex index.
        :type index: int
        :param groupId: The vertex group index.
        :type groupId: int
        :param weight: The vertex weight.
        :type weight: float
        """
        names = self.allVertexGroups()
        group = self.obj.vertex_groups.get(names[groupId])
        group.remove([index])
        if weight > 0:
            group.add([index], weight, 'REPLACE')

    def setWeightsForVertex(self, index, weightList):
        """Set the weight for the given vertex for all vertex groups.

        :param index: The vertex index.
        :type index: int
        :param weightList: The list of vertex weight tuples, with the
                           weight and vertex group index.
        :type weightList: list(tuple(float, int))
        """
        for groupIndex in range(len(weightList)):
            value, groupId = weightList[groupIndex]
            self.setVertexWeight(index, groupIndex, value)

    def setVertexWeights(self, indices, weightData):
        """Set the weights for the given list of vertex indices.

        :param indices: The list of vertex indices.
        :type indices: list(int)
        :param weightData: The list of vertex weight tuples, with the
                           weight and vertex group index for each given
                           vertex index.
        :type weightData: list(list(tuple(float, int)))

        :return: True, if setting the weights was successful. False if
                 the object is in edit mode.
        :rtype: bool
        """
        if self.obj.mode == 'EDIT':
            return False

        for i in range(len(weightData)):
            weightList = weightData[i]
            self.setWeightsForVertex(indices[i], weightList)

        return True

    def setWeightsFromVertexList(self, indices, allWeightData):
        """Set the weights for the given list of vertex indices.

        This is used to reset the previous weights when cancelling.
        The weight data list contains all previous weights but the given
        indices are only from the processed vertices.

        :param indices: The list of vertex indices.
        :type indices: list(int)
        :param allWeightData: The list of all vertex weight tuples, with
                              the  weight and vertex group index for
                              each vertex index.
        :type allWeightData: list(list(tuple(float, int)))

        :return: True, if setting the weights was successful. False if
                 the object is in edit mode.
        :rtype: bool
        """
        if self.obj.mode == 'EDIT':
            return False

        for i in range(len(indices)):
            weightList = allWeightData[indices[i]]
            self.setWeightsForVertex(indices[i], weightList)

        return True

    def undoStroke(self):
        """Reset the weights for all indices which have been edited
        during the last brush stroke.
        """
        if len(self.undoIndices):
            indices = self.undoIndices.pop(0)
            weights = self.undoWeights.pop(0)
            for i in indices:
                self.weights[i] = weights[i]
                self.setWeightsFromVertexList(indices, weights)

    def initSmoothed(self):
        """Initialize the list for holding the smoothed status for undo.
        """
        self.cancelIndices = [False] * self.numVertices()

    def getClosestFaceVertex(self, position, faceIndex, radius=1.0):
        """Return the index of the closest vertex to the given position.

        :param position: The 3d position to match the vertex to.
        :type position: Vector
        :param faceIndex: The index of the face to get the vertices
                          from.
        :type faceIndex: int
        :param radius: The search radius of the given position.
        :type radius: float

        :return: The index of the closest vertex and it's distance to
                 the reference point.
        :rtype: tuple(int, float)
        """
        index = None
        distance = 0.0

        for v in self.obj.data.polygons[faceIndex].vertices:
            # Get the delta vector between the center point and the
            # world position of the vertex.
            delta = position - self.pointsDeformed[v]
            # Get the world distance.
            dist = delta.length

            # Find which index is closest and store it along with the
            # distance.
            if index is None or distance > dist:
                # Only indices which are within the brush radius are of
                # interest.
                if dist <= radius:
                    index = v
                    distance = dist

        return index, distance

    # ------------------------------------------------------------------
    # Vertices in radius
    # ------------------------------------------------------------------

    def kdTree(self, local=True):
        """Build a KDTree for a fast volume search.

        :param local: True, if the local, non-deformed positions should
                      be used.
        :type local: bool

        :return: The kdtree.
        :rtype: kdtree instance
        """
        kd = kdtree.KDTree(len(self.pointsDeformed))
        for i in range(len(self.pointsDeformed)):
            if local:
                pos = self.mat @ self.obj.data.vertices[i].co
                kd.insert(pos, i)
            else:
                kd.insert(self.pointsDeformed[i], i)
        kd.balance()
        return kd

    def getVerticesInVolume(self, position, radius, local=False):
        """Return all vertices which are within the given volume radius
        based on the given center vertex.

        :param position: The world position of the radius center.
        :type position: Vector
        :param radius: The radius to search.
        :type radius: float
        :param local: True, if the local points should be used, False to
                      use the deformed points.
        :type local: bool

        :return: A list with tuples containing the vertex index, the
                 distance and the opposite boundary index.
        :rtype: list(int, float, int/None)
        """
        vertData = []

        # Search for vertices in range using the KDTree.
        if local:
            rangeVerts = self.kdLocal.find_range(position, radius)
        else:
            rangeVerts = self.kdDeformed.find_range(position, radius)

        for pos, index, dist in rangeVerts:
            value = 1 - (dist / radius)
            vertData.append((index, value, None))

        return vertData

    def getVerticesOnSurface(self, position, centerIndex, radius):
        """Return all vertices which are within the given surface radius
        based on the given center vertex.

        :param position: The world position of the radius center.
        :type position: Vector
        :param centerIndex: The index of the vertex at the radius
                            center.
        :type centerIndex: int
        :param radius: The radius to search.
        :type radius: float

        :return: A list with tuples containing the vertex index, the
                 distance and the opposite boundary index.
        :rtype: list(int, float, int/None)
        """
        visited = {centerIndex}

        dist = (self.pointsDeformed[centerIndex] - position).length

        # If the selection should span across the shell boundary get the
        # opposite vertex.
        oppositeIndex = None
        if not self.islands and self.bm.verts[centerIndex].is_boundary:
            oppositeIndex = self.getOppositeBoundaryIndex(centerIndex)

        value = 1 - (dist / radius)
        vertData = [(centerIndex, value, oppositeIndex)]

        # This array holds the indices which should be processed for
        # each iteration, walking outward from the center vertex.
        # The first time it only includes the center vertex which is
        # closest to the cursor. The next time it holds all the vertices
        # which are connected to the center vertex, and so on.
        walkVerts = [self.bm.verts[centerIndex]]
        # Add the opposite vertex to the process list.
        if oppositeIndex is not None:
            walkVerts.append(self.bm.verts[oppositeIndex])

        while walkVerts:
            currentVert = walkVerts.pop(0)

            # Get the connected vertices through the connected edges.
            for edge in currentVert.link_edges:
                connectedVert = edge.other_vert(currentVert)
                index = connectedVert.index

                if index in visited:
                    continue

                oppositeIndex = None

                dist = (self.pointsDeformed[index] - position).length
                if dist <= radius:
                    # If the selection should span across the shell
                    # boundary get the opposite vertex.
                    if not self.islands:
                        oppositeIndex = self.getOppositeBoundaryIndex(index)
                    value = 1 - (dist / radius)
                    vertData.append((index, value, oppositeIndex))

                # Mark the index as visited.
                visited.add(index)

                # Store the index for the next walk iteration.
                walkVerts.append(connectedVert)
                # Add the opposite vertex to the process list.
                if oppositeIndex is not None:
                    walkVerts.append(self.bm.verts[oppositeIndex])

            # Break from the loop in case the brush radius includes all
            # vertices.
            if len(vertData) == len(self.bm.verts):
                break

        return vertData

    # ------------------------------------------------------------------
    # Boundary
    # ------------------------------------------------------------------

    def getOppositeBoundaryIndex(self, vertIndex):
        """Return the index of the vertex which lies on the opposite
        side of the boundary of the given vertex.

        :param vertIndex: The index of the vertex.
        :type vertIndex: int

        :return: The opposite vertex index.
        :rtype: int or None
        """
        if not self.bm.verts[vertIndex].is_boundary:
            return

        edgeLength = self.averageEdgeLength(vertIndex)

        # Search for vertices in range using the KDTree.
        pos = self.mat @ self.obj.data.vertices[vertIndex].co
        rangeVerts = self.kdLocal.find_range(pos, edgeLength)
        sortedVerts = sorted(rangeVerts, key=lambda x: x[2])
        # The found vertices are sorted by distance; the nearest first.
        # The first vertex should be of the given index, therefore the
        # next should be the opposite vertex.
        for i in sortedVerts:
            if i[1] != vertIndex:
                return i[1]

    def edgeLength(self, edge):
        """Return the length of the given edge.

        :param edge: The edge to get the length from.
        :type edge: bmesh.types.BMEdge

        :return: The edge length.
        :rtype: float
        """
        verts = edge.verts
        pos1 = self.obj.data.vertices[verts[0].index].co
        pos2 = self.obj.data.vertices[verts[1].index].co
        return (pos1 - pos2).length

    def averageEdgeLength(self, index):
        """Return the average length of all edges connected to the given
        vertex index.

        :param index: The index of the connecting vertex.
        :type index: int

        :return: The average length of all edges.
        :rtype: float
        """
        edges = self.bm.verts[index].link_edges
        numEdges = len(edges)

        length = 0.0
        for edge in edges:
            length += self.edgeLength(edge) / numEdges

        return length

    # ------------------------------------------------------------------
    # Smoothing
    # ------------------------------------------------------------------

    def floodSmooth(self, useSelection=True, affectSelected=True, useColorAttr=False, strength=1.0):
        """Flood smooth the current selection.

        :param useSelection: True, if the selection should be used.
        :type useSelection: bool
        :param affectSelected: True, if only selected vertices should be
                               affected.
        :type affectSelected: bool
        :param strength: The smoothing strength.
        :type strength: float
        :param useColorAttr: True, if the color attribute should be used
                             for the selection (in paint mode), rather
                             than the current vertex selection.
        :type useColorAttr: bool
        """
        # Needed for the paint operator but not for the flood operator.
        self.undoIndices.insert(0, [])
        self.undoWeights.insert(0, [None] * self.numVertices())

        floodSelection = []
        floodUnselection = []

        if useColorAttr:
            for i in range(self.numVertices()):
                if self.isSelected(i):
                    floodSelection.append(i)
                else:
                    floodUnselection.append(i)
        else:
            floodSelection = self.selectedVertices

        if useSelection:
            if affectSelected:
                vertData = [None] * len(floodSelection)
                for i, index in enumerate(floodSelection):
                    oppositeIndex = self.getOppositeBoundaryIndex(index)
                    vertData[i] = index, strength, oppositeIndex
            else:
                if useColorAttr:
                    vertData = [None] * len(floodUnselection)
                    for i, index in enumerate(floodUnselection):
                        oppositeIndex = self.getOppositeBoundaryIndex(index)
                        vertData[i] = index, strength, oppositeIndex
                else:
                    vertData = [None] * (self.numVertices() - len(floodSelection))
                    v = 0
                    for i, vert in enumerate(self.obj.data.vertices):
                        if not vert.select:
                            oppositeIndex = self.getOppositeBoundaryIndex(vert.index)
                            vertData[v] = vert.index, strength, oppositeIndex
                            v += 1
        else:
            vertData = [None] * self.numVertices()
            for vert in self.obj.data.vertices:
                oppositeIndex = self.getOppositeBoundaryIndex(vert.index)
                vertData[vert.index] = vert.index, strength, oppositeIndex

        self.performSmooth(vertData, flood=True)

    def performSmooth(self, vertData, flood=False):
        """Smooth all vertices within the brush radius.

        :param vertData: The list with vertex data from the brush range.
        :type vertData: list(tuple(int, float, int/None))
        :param flood: True, if flooding should be performed.
                      This disables the scale value being affected by
                      the curve falloff.
        :type flood: bool
        """
        # The smoothing is performed in three steps to increase
        # efficiency in relation to possible oversampling.
        # 1. Evaluate all vertices of the brush radius and collect their
        #    connected indices, or neighbours in volume mode.
        #    This way, the calculation intensive processing of the mesh
        #    only has to be performed once, no matter the number of
        #    oversampling steps.
        connectedData = []
        for index, value, indexBound in vertData:

            isSel = self.isSelected(index)
            affectState = isSel if self.affectSelected else not isSel

            # Only process affected vertices.
            if not self.useSelection or (self.useSelection and affectState):
                if self.undoWeights[0][index] is None:
                    self.undoIndices[0].append(index)
                    self.undoWeights[0][index] = [tuple(item) for item in self.weights[index]]
                connectedData.append(self.getConnectedData(index, value, indexBound, flood))

        # 2. Perform the smoothing of the weights.
        #    If oversampling is required, this would be placed inside
        #    the oversampling loop.
        #    When oversampling, the important part is to use the new
        #    weights as the base for the next oversampling pass.
        #    New and old weights shouldn't get mixed up because this
        #    would cause jitter, since the weights and indices are not
        #    in order.
        smoothed = [None] * self.numVertices()
        for index, scale, indexBound, connected, volumeScale in connectedData:
            self.computeWeights(index, scale, indexBound, connected, volumeScale, smoothed)

        # 3. Collect all processed vertices and their final weights for
        #    setting the values in the vertex groups.
        indices = []
        weightData = []
        for index, scale, indexBound, connected, volumeScale in connectedData:
            # Get the new weights for applying.
            indices.append(index)
            self.cancelIndices[index] = True
            weightData.append(smoothed[index])
            self.weights[index] = smoothed[index]
            # Add the boundary vertex if in surface mode and
            # islands should not be respected.
            if not self.islands and indexBound is not None:
                indices.append(indexBound)
                self.cancelIndices[indexBound] = True
                weightData.append(smoothed[indexBound])
                self.weights[indexBound] = smoothed[indexBound]

        # Apply the weights.
        self.setVertexWeights(indices, weightData)

    def getConnectedData(self, index, value, indexBound, flood=False):
        """Return the data of all connected vertices, either by surface
        or by volume, which are used as a source to calculcate the
        smoothing.

        :param index: The index of the vertex to smooth.
        :type index: int
        :param value: The scale value for the smoothing.
        :type value: float
        :param indexBound: The index of the opposite boundary vertex.
        :type indexBound: None/int
        :param flood: True, if flooding should be performed.
                      This disables the scale value being affected by
                      the curve falloff.
        :type flood: bool

        :return: A tuple with all data necessary to calculate the
                 weights.
                 index: The vertex index.
                 scale: The scale value for the smoothing.
                 indexBound: The opposite boundary index.
                 connected: The list of connected vertices.
                 volumeScale: The list of scale values for volume
                              neighbours.
        :rtype: tuple(int, float, int, list(int), list(float)/None)
        """
        # Get the connected vertices.
        connected = []
        # The distance-depending scale values for volume vertices.
        volumeScale = None
        if not self.volume:
            connected.extend(self.connectedVertices(index))
            if indexBound is not None:
                connected.extend(self.connectedVertices(indexBound))
        else:
            pos = self.mat @ self.obj.data.vertices[index].co
            vertData = self.getVerticesInVolume(pos,
                                                self.radius * self.volumeRange,
                                                local=True)
            connected = [i for i, v, b in vertData]
            volumeScale = [v for i, v, b in vertData]

        if not flood:
            scale = getFalloffValue(value, self.curve) * self.strength
        else:
            scale = self.strength

        return index, scale, indexBound, connected, volumeScale

    def computeWeights(self, index, scale, indexBound, connected, volumeScale, smoothed):
        """Calculate an interpolated weight value from the current
        weight and the weights of the connected vertices.

        :param index: The index of the vertex to smooth.
        :type index: int
        :param scale: The scale value for the smoothing.
        :type scale: float
        :param indexBound: The index of the opposite boundary vertex.
        :type indexBound: None/int
        :param connected: The list of connected vertices to draw weights
                          from.
        :type connected: list(int)
        :param volumeScale: The list of scale values for volume
                            neighbours. None, if not in volume mode.
        :type volumeScale: list(float)/None
        :param smoothed: The list of smoothed weights, which contains
                         None for the first oversampling pass.
        :type smoothed: list(tuple(float, int) or None)
        """
        numConnected = len(connected)

        maxWeight = 0.0
        maxWeightLocked = 0.0
        maxWeightUnlocked = 0.0
        hasLocks = False

        # --------------------------------------------------------------
        # Weight calculation
        # --------------------------------------------------------------

        # Declared just for safety. It will get overwritten when getting
        # the weights from the list.
        groupId = 0
        # The pre-allocated list of weights. This gets updated with each
        # evaluated group.
        weightList = [0.0] * len(self.weights[index])

        for i in range(len(self.weights[index])):
            weight, groupId = self.weights[index][i]

            originalWeight = weight

            # Collect the weights per influence.
            # When in volume mode it's possible that the volume range is
            # too small and no vertices are found. In this case there
            # are no weights to average.
            if numConnected and not self.isLocked(i):
                # If there are connected vertices, ignore the current
                # weight to evaluate only the connected weights.
                weight = 0.0
                for c in range(numConnected):
                    mult = scale
                    if self.volume:
                        mult = volumeScale[c]
                    weight += self.weights[connected[c]][i][0] * mult + originalWeight * (1 - mult)

                weight = weight / numConnected

            maxWeight += weight
            if self.isLocked(i):
                maxWeightLocked += weight
                hasLocks = True
            else:
                maxWeightUnlocked += weight

            # Add the averaged weight to the list.
            weightList[i] = weight, groupId

        smoothed[index] = weightList

        # --------------------------------------------------------------
        # Set max influences
        # --------------------------------------------------------------

        if numConnected and self.useMaxGroups:
            sortedWeights = sorted(smoothed[index], key=lambda x: x[0], reverse=True)

            maxWeight = 0.0
            maxWeightLocked = 0.0
            maxWeightUnlocked = 0.0

            for i in range(len(sortedWeights)):
                weight, groupId = sortedWeights[i]
                if i >= self.maxGroups:
                    weight = 0.0

                maxWeight += weight
                if self.isLocked(groupId):
                    maxWeightLocked += weight
                    hasLocks = True
                else:
                    maxWeightUnlocked += weight

                smoothed[index][groupId] = weight, groupId

        # --------------------------------------------------------------
        # Normalize
        # --------------------------------------------------------------

        if self.normalize:
            for i in range(len(smoothed[index])):
                weight, groupId = smoothed[index][i]

                # In case there aren't any locked influences the
                # normalization can consider all weights.
                if not hasLocks:
                    if maxWeight > 0:
                        weight /= maxWeight
                    else:
                        weight = 0.0
                # If one or more influences are locked keep the weights
                # of the locked and calculate a scaling factor for the
                # unlocked based on the unlocked weight sum and the
                # remaining weight range.
                else:
                    remainingWeight = 1 - maxWeightLocked
                    if not self.isLocked(i):
                        # Make sure the division is not by a zero
                        # weight.
                        if remainingWeight > 0:
                            if maxWeightUnlocked > 0:
                                weight *= remainingWeight / maxWeightUnlocked
                        else:
                            weight = 0.0

                # Clamp because of float precision.
                weight = clamp(weight, 0.0, 1.0)

                smoothed[index][i] = weight, groupId

        # Copy the vertex weights to the boundary vertex if in surface
        # mode and islands should not be respected.
        if not self.islands and indexBound is not None:
            smoothed[indexBound] = smoothed[index]

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def getColorAttribute(self):
        """Return the color attribute if it exists or create a new one.

        :return: The color attribute for the selection.
        :rtype: bpy.types.Attribute
        """
        colors = self.obj.data.color_attributes.get(SELECT_COLOR_ATTRIBUTE)
        if not colors:
            colors = self.obj.data.color_attributes.new(name=SELECT_COLOR_ATTRIBUTE,
                                                        type='FLOAT_COLOR',
                                                        domain='POINT')
        # Store the currenly active colors.
        self.userColorAttr = self.obj.data.color_attributes.active_color
        # Set the active colors.
        self.obj.data.color_attributes.active_color = colors
        return colors

    def updateColorAttribute(self):
        """Refresh the reference to the color attribute in case it is
        empty after switching modes.

        :return: The color attribute for the selection.
        :rtype: bpy.types.Attribute
        """
        if not len(self.selectionColors.data):
            self.selectionColors = self.getColorAttribute()

    def deleteColorAttribute(self):
        """Remove the color attribute for the selection.
        """
        if self.selectionColors is not None:
            # When finishing the tool the attributes name is empty.
            # The cause for this is unknown, especially since this
            # doesn't happen when cancelling.
            # To make sure that the removal doesn't throw an error
            # because of a missing name, the name is checked and the
            # attribute reference updated.
            if not len(self.selectionColors.name):
                self.selectionColors = self.getColorAttribute()
            self.obj.data.color_attributes.remove(self.selectionColors)
            self.selectionColors = None

        if self.userColorAttr is not None:
            self.obj.data.color_attributes.active_color = self.userColorAttr

    def setSelection(self, indices):
        """Set the selection color for the given list of vertices.

        :param indices: The list of vertex indices to color as selected.
        :type indices: list(int)
        """
        if self.selectionColors is None:
            return

        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        bpy.ops.object.mode_set(mode="OBJECT")

        color = getPreferences().selected_color
        color = [linear_to_srgb(c) for c in color]
        for index in indices:
            self.selectionColors.data[index].color = (color[0], color[1], color[2], 1.0)

        bpy.ops.object.mode_set(mode=mode)

    def removeSelection(self, indices):
        """Remove the selection color for the given list of vertices.

        :param indices: The list of vertex indices to remove the color
                        from.
        :type indices: list(int)
        """
        if self.selectionColors is None:
            return

        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        bpy.ops.object.mode_set(mode="OBJECT")

        color = getPreferences().unselected_color
        color = [linear_to_srgb(c) for c in color]
        for index in indices:
            self.selectionColors.data[index].color = (color[0], color[1], color[2], 1.0)

        bpy.ops.object.mode_set(mode=mode)

    def clearSelection(self):
        """Clear the selection color for all vertices.
        """
        if self.selectionColors is None:
            return

        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        bpy.ops.object.mode_set(mode="OBJECT")

        color = getPreferences().unselected_color
        color = [linear_to_srgb(c) for c in color]
        for i in range(self.numVertices()):
            self.selectionColors.data[i].color = (color[0], color[1], color[2], 1.0)

        bpy.ops.object.mode_set(mode=mode)

    def colorToSelection(self):
        """Select all vertices which have their selection color set.
        """
        if self.selectionColors is None:
            return

        indices = []
        for i, data in enumerate(self.selectionColors.data):
            vertValue = data.color[self.colorIndex]
            if math.isclose(vertValue, self.colorValue, rel_tol=0.01):
                indices.append(i)
        self.selectVertices(indices)

    def isSelected(self, index):
        """Return, if the vertex with the given index has its selection
        color set.

        :param index: The vertex index.
        :type index: int

        :return: True, if the vertex is colored as selected.
        :rtype: bool
        """
        if self.selectionColors is None:
            return False

        vertValue = self.selectionColors.data[index].color[self.colorIndex]

        return math.isclose(vertValue, self.colorValue, rel_tol=0.01)

    def setColorIdentifier(self):
        """Set the identifying color value and channel based on the
        preferences selection color.

        The values are stored in the class variables.
        """
        color = getPreferences().selected_color
        color = [linear_to_srgb(c) for c in color]
        for c in range(len(color)):
            if self.colorValue < color[c] < 0.99:
                self.colorValue = color[c]
                self.colorIndex = c


# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def srgb_to_linear(value):
    """Convert the given sRGB value to a linear value.

    :param value: The sRGB value to convert.
    :type value: float

    :return: The linear value.
    :rtype: float
    """
    if value <= 0.0404482362771082:
        return value / 12.92
    else:
        return pow(((value + 0.055) / 1.055), 2.4)


def linear_to_srgb(value):
    """Convert the given linear value to a sRGB value.

    :param value: The linear value to convert.
    :type value: float

    :return: The sRGB value.
    :rtype: float
    """
    if value > 0.0031308:
        return 1.055 * (pow(value, (1.0 / 2.4))) - 0.055
    else:
        return 12.92 * value


def isEquivalent(vector1, vector2, tolerance=1e-6):
    """Return, if the given vectors are equivalent to each other.

    :param vector1: The first vector to compare.
    :type vector1: Vector
    :param vector2: The second vector to compare.
    :type vector2: Vector
    :param tolerance: The allowed tolerance between the vectors.
    :type tolerance: float

    :return: True, if the vectors are equivalent to each other.
    :rtype: bool
    """
    return (vector1 - vector2).length_squared <= tolerance * tolerance


def isModifier(event):
    """Return if the event contains a modifier key

    :param event: The current event.
    :type event: bpy.types.Event

    :return: True, if the even contains a modifier key.
    :rtype: bool
    """
    return event.alt or event.shift or event.ctrl or event.oskey


def getFalloffValue(value, curve):
    """Return the falloff value based on the given curve.

    :param value: The value to scale.
    :type value: float
    :param curve: The curve type.
    :type curve: str

    :return: The scaled value.
    :rtype: float
    """
    if curve == 'NONE':
        return 1.0
    elif curve == 'SMOOTH':
        return value * value * (3 - 2 * value)
    elif curve == 'NARROW':
        return 1 - pow((1 - value) / 1, 0.4)
    else:
        return value


def clamp(value, minVal, maxVal):
    """Clamp to given value to the min and max range.

    :param value: The value to clamp.
    :type value: float
    :param minVal: The minimum allowed value.
    :type minVal: float
    :param maxVal: The maximum allowed value.
    :type maxVal: float

    :return: The clamped value.
    :rtype: float
    """
    value = max(min(value, maxVal), minVal)
    return value


def isBackface(viewVector, faceNormal):
    """Return, if the given face normal is pointing away from the view.

    :param viewVector: The viewing vector.
    :type viewVector: Vector
    :param faceNormal: The normal of the face.
    :type faceNormal: Vector

    :return: True, if the face is pointing away.
    :rtype: bool
    """
    viewVector.normalize()
    faceNormal.normalize()
    return viewVector.dot(faceNormal) > 0


# ----------------------------------------------------------------------
# Tool Panel
# ----------------------------------------------------------------------

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
            obj.mode in ['OBJECT', 'WEIGHT_PAINT'] and
            len(obj.vertex_groups) > 1):
        return True
    return False


class SMOOTHWEIGHTS_PT_settings(bpy.types.Panel):
    """Panel class.
    """
    bl_label = "Smooth Weights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        """Returns, if the panel is visible.

        :param context: The current context.
        :type context: bpy.context

        :return: True, if the panel should be visible.
        :rtype: bool
        """
        return hasWeights(context)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        sw = context.object.smooth_weights

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(sw, "curve", text=CURVE_LABEL)
        col.prop(sw, "radius", text=RADIUS_LABEL)
        col.prop(sw, "strength", text=STRENGTH_LABEL)
        col.separator()
        col.prop(sw, "volume", text=VOLUME_LABEL)
        col.prop(sw, "volumeRange", text=VOLUME_RANGE_LABEL)
        col.separator()
        col.prop(sw, "useSelection", text=USE_SELECTION_LABEL)
        col.prop(sw, "affectSelected", text=AFFECT_SELECTED_LABEL)
        col.prop(sw, "ignoreBackside", text=IGNORE_BACKSIDE_LABEL)
        col.prop(sw, "islands", text=USE_ISLANDS_LABEL)
        col.prop(sw, "ignoreLock", text=IGNORE_LOCK_LABEL)
        col.prop(sw, "normalize", text=NORMALIZE_LABEL)
        col.prop(sw, "useMaxGroups", text=USE_MAX_GROUPS_LABEL)
        col.prop(sw, "maxGroups", text=MAX_GROUPS_LABEL)
        col.separator()
        col.operator("object.smooth_weights", text="Brush")
        col.separator()
        col.operator("object.smooth_weights_flood", text="Flood")


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

def menu_item(self, context):
    """Draw the menu item and it's sub-menu.

    :param context: The current context.
    :type context: bpy.context
    """
    if hasWeights(context):
        self.layout.separator()
        self.layout.operator(OBJECT_OT_SmoothWeights.bl_idname,
                             text="Smooth Weights")
        self.layout.operator(OBJECT_OT_SmoothWeightsFlood.bl_idname,
                             text="Flood Smooth Weights")


# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------

def getPreferences():
    """Return the preferences of the add-on.

    :return: The add-on preferences.
    :rtype: bpy.types.AddonPreferences
    """
    prefs = bpy.context.preferences.addons[NAME].preferences
    return prefs


class SMOOTHWEIGHTSPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = NAME

    brush_color: bpy.props.FloatVectorProperty(name="Brush Color",
                                               description=ANN_BRUSH_COLOR,
                                               subtype='COLOR',
                                               default=BRUSH_COLOR)
    keep_selection: bpy.props.BoolProperty(name="Keep Selection After Finishing",
                                           description=ANN_KEEP_SELECTION,
                                           default=KEEP_SELECTION)
    selected_color: bpy.props.FloatVectorProperty(name="Selected Color",
                                                  description=ANN_SELECTED_COLOR,
                                                  subtype='COLOR',
                                                  default=SELECTED_COLOR)
    show_info: bpy.props.BoolProperty(name="Show Tool Info",
                                      description=ANN_SHOW_INFO,
                                      default=SHOW_INFO)
    undo_steps: bpy.props.IntProperty(name="Undo Steps",
                                      description=ANN_UNDO_STEPS,
                                      default=UNDO_STEPS,
                                      min=1,
                                      max=100)
    unselected_color: bpy.props.FloatVectorProperty(name="Unselected Color",
                                                    description=ANN_UNSELECTED_COLOR,
                                                    subtype='COLOR',
                                                    default=UNSELECTED_COLOR)

    affectSelected_key: bpy.props.StringProperty(name="Affect Selected",
                                                 description=ANN_AFFECT_SELECTED,
                                                 default=AFFECTSELECTED_KEY)
    clearSelection_key: bpy.props.StringProperty(name="Clear Selection",
                                                 description=ANN_CLEAR_SELECTION,
                                                 default=CLEARSELECTION_KEY)
    deselect_key: bpy.props.StringProperty(name="Deselect",
                                           description=ANN_DESELECT,
                                           default=DESELECT_KEY)
    flood_key: bpy.props.StringProperty(name="Flood",
                                        description=ANN_FLOOD,
                                        default=FLOOD_KEY)
    ignoreBackside_key: bpy.props.StringProperty(name="Ignore Backside",
                                                 description=ANN_IGNORE_BACKSIDE,
                                                 default=IGNOREBACKSIDE_KEY)
    ignoreLock_key: bpy.props.StringProperty(name="Ignore Lock",
                                             description=ANN_IGNORE_LOCK,
                                             default=IGNORELOCK_KEY)
    islands_key: bpy.props.StringProperty(name="Use Islands",
                                          description=ANN_USE_ISLANDS,
                                          default=ISLANDS_KEY)
    maxGroups_key: bpy.props.StringProperty(name="Max Groups",
                                            description=ANN_MAX_GROUPS,
                                            default=MAXGROUPS_KEY)
    normalize_key: bpy.props.StringProperty(name="Normalize",
                                            description=ANN_NORMALIZE,
                                            default=NORMALIZE_KEY)
    radius_key: bpy.props.StringProperty(name="Radius",
                                         description=ANN_RADIUS,
                                         default=RADIUS_KEY)
    select_key: bpy.props.StringProperty(name="Select",
                                         description=ANN_SELECT,
                                         default=SELECT_KEY)
    strength_key: bpy.props.StringProperty(name="Strength",
                                           description=ANN_STRENGTH,
                                           default=STRENGTH_KEY)
    useMaxGroups_key: bpy.props.StringProperty(name="Use Max Groups",
                                               description=ANN_USE_MAX_GROUPS,
                                               default=USEMAXGROUPS_KEY)
    useSelection_key: bpy.props.StringProperty(name="Use Selection",
                                               description=ANN_USE_SELECTION,
                                               default=USESELECTION_KEY)
    value_up_key: bpy.props.StringProperty(name="Increase Value",
                                           description=ANN_VALUE_UP,
                                           default=VALUE_UP_KEY)
    value_down_key: bpy.props.StringProperty(name="Decrease Value",
                                             description=ANN_VALUE_DOWN,
                                             default=VALUE_DOWN_KEY)
    volume_key: bpy.props.StringProperty(name="Use Volume",
                                         description=ANN_VOLUME,
                                         default=VOLUME_KEY)
    volumeRange_key: bpy.props.StringProperty(name="Volume Range",
                                              description=ANN_VOLUME_RANGE,
                                              default=VOLUMERANGE_KEY)

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
        colBox.separator()
        colBox.prop(self, "brush_color")
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
        colBox.separator()
        colBox.prop(self, "volume_key")
        colBox.prop(self, "volumeRange_key")
        colBox.separator()
        colBox.prop(self, "useMaxGroups_key")
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
classes = [SmoothWeights_Properties,
           OBJECT_OT_SmoothWeights,
           OBJECT_OT_SmoothWeightsFlood,
           SMOOTHWEIGHTS_PT_settings,
           SMOOTHWEIGHTSPreferences]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.smooth_weights = bpy.props.PointerProperty(type=SmoothWeights_Properties)

    # Add the menu items.
    bpy.types.VIEW3D_MT_object.append(menu_item)
    bpy.types.VIEW3D_MT_paint_weight.append(menu_item)


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.smooth_weights

    # Remove the menu items.
    bpy.types.VIEW3D_MT_object.remove(menu_item)
    bpy.types.VIEW3D_MT_paint_weight.remove(menu_item)

    # Remove the brush circle and info from the 3d view if any.
    drawInfo3d.removeCircle()
    drawInfo3d.removeInfo()


if __name__ == "__main__":
    register()
