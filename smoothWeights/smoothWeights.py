# <pep8 compliant>

from . import constants as const
from . import preferences as prefs
from . import language, panel, symmetryMap, utils, weights

import blf
import bpy
from bpy_extras import view3d_utils
import bmesh
import gpu
from gpu_extras.batch import batch_for_shader

import math
from mathutils import Vector, kdtree
import time


# Get the current language.
strings = language.getLanguage()

# Version specific vars.
SHADER_TYPE = 'UNIFORM_COLOR'
if bpy.app.version < (3, 4, 0):
    SHADER_TYPE = '3D_UNIFORM_COLOR'


# ----------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------

def stateLabel(var):
    """Return the on- or off-string depending on the given bool state.

    :param var: The bool value.
    :type var: bool

    :return: The on- or off-string.
    :rtype: str
    """
    return strings.ON_LABEL if var else strings.OFF_LABEL


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
        self.blend_key = None
        self.clearSelection_key = None
        self.deselect_key = None
        self.ignoreBackside_key = None
        self.ignoreLock_key = None
        self.islands_key = None
        self.maxGroups_key = None
        self.normalize_key = None
        self.oversampling_key = None
        self.radius_key = None
        self.select_key = None
        self.strength_key = None
        self.useSelection_key = None
        self.useSymmetry_key = None
        self.vertexGroups_key = None
        self.volume_key = None
        self.volumeRange_key = None

    @classmethod
    def drawColor(cls, item):
        """Return the draw color defined in the preferences.

        :param item: The color item string.
        :type item: str

        :return: The drawing color for the brush circle and info.
        :rtype: list
        """
        if item == "brush":
            color = prefs.getPreferences().brush_color
        else:
            color = prefs.getPreferences().info_color
        # Gamma-correct the color.
        return [utils.linear_to_srgb(c) for c in color]

    def drawCallback(self, context):
        """Callback for drawing the brush.

        :param context: The current context.
        :type context: bpy.context
        """
        if self.center is None:
            return

        color = self.drawColor(item="brush")

        # Get the brush settings.
        radius = context.object.smooth_weights.radius

        # The number of points for the brush circle.
        numPoints = const.CIRCLE_POINTS

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

        shader = gpu.shader.from_builtin(SHADER_TYPE)
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

        color = self.drawColor(item="info")

        # The font size and positioning depends on the system's pixel
        # size.
        pixelSize = bpy.context.preferences.system.pixel_size
        fontSize = 11 * pixelSize

        # Get the brush settings.
        affectSelected = context.object.smooth_weights.affectSelected
        blend = context.object.smooth_weights.blend
        curve = context.object.smooth_weights.curve
        deselect = context.object.smooth_weights.deselect
        ignoreBackside = context.object.smooth_weights.ignoreBackside
        ignoreLock = context.object.smooth_weights.ignoreLock
        islands = context.object.smooth_weights.islands
        maxGroups = context.object.smooth_weights.maxGroups
        normalize = context.object.smooth_weights.normalize
        oversampling = context.object.smooth_weights.oversampling
        radius = context.object.smooth_weights.radius
        select = context.object.smooth_weights.select
        useSelection = context.object.smooth_weights.useSelection
        useSymmetry = context.object.smooth_weights.useSymmetry
        strength = context.object.smooth_weights.strength
        vertexGroups = context.object.smooth_weights.vertexGroups
        volume = context.object.smooth_weights.volume
        volumeRange = context.object.smooth_weights.volumeRange

        curveItems = {'NONE': 1, 'LINEAR': 2, 'SMOOTH': 3, 'NARROW': 4}

        selectState = strings.OFF_LABEL
        if select:
            selectState = strings.SELECT_LABEL
        elif deselect:
            selectState = strings.DESELECT_LABEL

        # Show the full tool info.
        if prefs.getPreferences().show_info:
            # Draw the settings in the lower left corner of the screen.
            lines = ["{}  {}: {}".format(curveItems[curve],
                                         strings.CURVE_LABEL,
                                         curve.lower().title()),
                     "{}  {}: {:.3f}".format(self.radius_key,
                                             strings.RADIUS_LABEL,
                                             radius),
                     "{}  {}: {:.3f}".format(self.strength_key,
                                             strings.STRENGTH_LABEL,
                                             strength),
                     "",
                     "{}  {}: {}".format(self.useSelection_key,
                                         strings.USE_SELECTION_LABEL,
                                         stateLabel(useSelection)),
                     "{}  {} {}".format(self.affectSelected_key,
                                        strings.AFFECT_SELECTED_LABEL,
                                        stateLabel(affectSelected)),
                     "{}  {}: {}".format(self.ignoreBackside_key,
                                         strings.IGNORE_BACKSIDE_LABEL,
                                         stateLabel(ignoreBackside)),
                     "{}  {}: {}".format(self.ignoreLock_key,
                                         strings.IGNORE_LOCK_LABEL,
                                         stateLabel(ignoreLock)),
                     "{}  {} {}".format(self.islands_key,
                                        strings.USE_ISLANDS_LABEL,
                                        stateLabel(islands)),
                     "{}  {}: {}".format(self.normalize_key,
                                         strings.NORMALIZE_LABEL,
                                         stateLabel(normalize)),
                     "{}  {}: {}".format(self.oversampling_key,
                                         strings.OVERSAMPLING_LABEL,
                                         oversampling),
                     "",
                     "{}  {}: {}".format(self.volume_key,
                                         strings.VOLUME_LABEL,
                                         stateLabel(volume)),
                     "{}  {}: {:.3f}".format(self.volumeRange_key,
                                             strings.VOLUME_RANGE_LABEL,
                                             volumeRange),
                     "",
                     "{}  {}: {}".format(self.maxGroups_key,
                                         strings.MAX_GROUPS_LABEL,
                                         maxGroups),
                     "    {}: {}".format(strings.CURRENT_MAX_GROUPS_LABEL, self.currentMaxGroups),
                     "{}  {}: {}".format(self.vertexGroups_key,
                                         strings.VERTEX_GROUPS_LABEL,
                                         vertexGroups.lower().title()),
                     "",
                     "{}: {}".format(strings.SELECTION_LABEL, selectState)]

            if vertexGroups == "OTHER":
                lines.insert(18, "{}  {}: {}".format(self.blend_key,
                                                     strings.BLEND_LABEL,
                                                     blend))
            if symmetryMap.hasMapProperty(context.object):
                lines.insert(len(lines) - 1, "{}  {}: {}".format(self.useSymmetry_key,
                                                                 strings.USE_SYMMETRY_LABEL,
                                                                 stateLabel(useSymmetry)))
                lines.insert(len(lines) - 1, "")

        # Show only the minimum tool info.
        else:
            label = strings.SMOOTH_LABEL if selectState == strings.OFF_LABEL else selectState
            lines = ["{}: {}".format(strings.MODE_LABEL, label)]

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

    @classmethod
    def updateView(cls):
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
        self.affectSelected_key = prefs.getPreferences().affectSelected_key.upper()
        self.blend_key = prefs.getPreferences().blend_key.upper()
        self.clearSelection_key = prefs.getPreferences().clearSelection_key.upper()
        self.deselect_key = prefs.getPreferences().deselect_key.upper()
        self.ignoreBackside_key = prefs.getPreferences().ignoreBackside_key.upper()
        self.ignoreLock_key = prefs.getPreferences().ignoreLock_key.upper()
        self.islands_key = prefs.getPreferences().islands_key.upper()
        self.maxGroups_key = prefs.getPreferences().maxGroups_key.upper()
        self.normalize_key = prefs.getPreferences().normalize_key.upper()
        self.oversampling_key = prefs.getPreferences().oversampling_key.upper()
        self.radius_key = prefs.getPreferences().radius_key.upper()
        self.select_key = prefs.getPreferences().select_key.upper()
        self.strength_key = prefs.getPreferences().strength_key.upper()
        self.useSelection_key = prefs.getPreferences().useSelection_key.upper()
        self.useSymmetry_key = prefs.getPreferences().useSymmetry_key.upper()
        self.vertexGroups_key = prefs.getPreferences().vertexGroups_key.upper()
        self.volume_key = prefs.getPreferences().volume_key.upper()
        self.volumeRange_key = prefs.getPreferences().volumeRange_key.upper()


# Global instance.
drawInfo3d = DrawInfo3D()


# ----------------------------------------------------------------------
# Paint Operator
# ----------------------------------------------------------------------

class SMOOTHWEIGHTS_OT_Paint(bpy.types.Operator):
    """Operator class for the tool.
    """
    bl_idname = "smoothweights.paint"
    bl_label = strings.MENU_SMOOTH_WEIGHTS
    bl_description = strings.DESCR_PAINT
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
    Mesh = None
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
    # The switch for setting the vertex groups type.
    setVertexGroups = False
    # The switch for setting the oversampling value.
    setOversampling = False

    isModal = False

    # Settings
    affectSelected = const.AFFECT_SELECTED
    blend = const.BLEND
    curve = "SMOOTH"
    ignoreBackside = const.IGNORE_BACKSIDE
    ignoreLock = const.IGNORE_LOCK
    islands = const.USE_ISLANDS
    maxGroups = const.MAX_GROUPS
    normalize = const.NORMALIZE
    oversampling = const.OVERSAMPLING
    radius = const.RADIUS
    strength = const.STRENGTH
    useSelection = const.USE_SELECTION
    useSymmetry = const.USE_SYMMETRY
    vertexGroups = "DEFORM"
    volume = const.VOLUME
    volumeRange = const.VOLUME_RANGE

    # Keys
    affectSelected_key = None
    blend_key = None
    clearSelection_key = None
    deselect_key = None
    flood_key = None
    ignoreBackside_key = None
    ignoreLock_key = None
    islands_key = None
    maxGroups_key = None
    normalize_key = None
    oversampling_key = None
    radius_key = None
    select_key = None
    strength_key = None
    useSelection_key = None
    useSymmetry_key = None
    value_up_key = None
    value_down_key = None
    vertexGroups_key = None
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
        if not context.object:
            self.report({'WARNING'}, strings.WARNING_NO_OBJECT)
            return self.cancel(context)

        # Initialize the skin mesh.
        self.Mesh = Mesh()
        if not self.Mesh.setup(obj=context.object, allowModifiers=False):
            self.Mesh.reset()
            self.report({'WARNING'}, strings.WARNING_ACTIVE_MODIFIERS)
            return {'FINISHED'}

        self.isModal = True
        self.getKeymaps()

        context.window.cursor_set("PAINT_CROSS")
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set(self.getStatusInfo())

        # Get the brush settings.
        self.affectSelected = context.object.smooth_weights.affectSelected
        self.blend = context.object.smooth_weights.blend
        self.curve = context.object.smooth_weights.curve
        self.ignoreBackside = context.object.smooth_weights.ignoreBackside
        self.ignoreLock = context.object.smooth_weights.ignoreLock
        self.islands = context.object.smooth_weights.islands
        self.maxGroups = context.object.smooth_weights.maxGroups
        self.normalize = context.object.smooth_weights.normalize
        self.oversampling = context.object.smooth_weights.oversampling
        self.radius = context.object.smooth_weights.radius
        self.strength = context.object.smooth_weights.strength
        self.useSelection = context.object.smooth_weights.useSelection
        self.useSymmetry = context.object.smooth_weights.useSymmetry
        self.vertexGroups = context.object.smooth_weights.vertexGroups
        self.volume = context.object.smooth_weights.volume
        self.volumeRange = context.object.smooth_weights.volumeRange

        # Transfer the current selection to the selection color.
        self.Mesh.setSelection(self.Mesh.selectedVertices)

        # If the current selection should be used for smoothing, store
        # the current shading mode and switch to selection display.
        if self.useSelection:
            self.setSelectionMode(context, active=True)

        # Add the draw handler for the brush info.
        drawInfo3d.currentMaxGroups = self.Mesh.currentMaxGroups
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
        if context.object and self.Mesh is not None:
            # Reset the weights.
            # Process only the weights which have been smoothed.
            self.Mesh.revertWeights()

        # Reset the operator.
        self.reset(context)

        return {'CANCELLED'}

    def reset(self, context):
        """Reset the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        self.isModal = False

        if self.Mesh is not None:
            # Remove the selection colors.
            self.Mesh.deleteColorAttribute()

            # Reset the selection modes.
            self.setSelectionMode(context, active=False)

            self.Mesh.reset()
            self.Mesh = None

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
        smooth_weights = context.object.smooth_weights

        select = smooth_weights.select
        deselect = smooth_weights.deselect

        # --------------------------------------------------------------
        # Smooth and Selection
        # --------------------------------------------------------------

        # Set, if the tool should enter or leave dragging mode.
        if event.type == 'LEFTMOUSE' and not isModifier(event):
            if not self.isDragging:
                self.isDragging = True

                # Make sure that the object is in Object or WEIGHT_PAINT
                # mode.
                if self.Mesh.obj.mode not in ['OBJECT', 'WEIGHT_PAINT']:
                    bpy.ops.object.mode_set(mode='OBJECT')
                # Make sure the color attribute is current.
                self.Mesh.updateColorAttribute()

                if smooth_weights.vertexGroups != self.vertexGroups:
                    # Update the list with vertex group indices which
                    # don't belong to the given vertex group type.
                    self.Mesh.setUnaffectedGroupIndices()
                    self.vertexGroups = smooth_weights.vertexGroups

                # Update the keymaps.
                self.getKeymaps()
                # Init the undo list.
                # If the maximum size of the undo list has been reached
                # remove the last element.
                if prefs.getPreferences().undo_steps <= len(self.Mesh.undoIndices):
                    lastItem = len(self.Mesh.undoIndices) - 1
                    self.Mesh.undoIndices.pop(lastItem)
                    self.Mesh.undoWeights.pop(lastItem)
                self.Mesh.undoIndices.insert(0, [])
                self.Mesh.undoWeights.insert(0, {})
                drawInfo3d.addCircle()

        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # If the brush action has been performed refresh the point
            # positions.
            if self.isDragging:
                self.Mesh.getDeformedPointPositions()

            self.isDragging = False
            # Remove the brush circle.
            drawInfo3d.removeCircle()

        # Perform the smoothing or selecting action.
        if event.type == 'MOUSEMOVE' and self.isDragging:
            # Skip evaluation steps to improve performance.
            self.undersamplingSteps += 1
            if self.undersamplingSteps < const.UNDERSAMPLING:
                return {'RUNNING_MODAL'}
            self.undersamplingSteps = 0

            rangeVerts = self.getVerticesInRange(context, event)
            if rangeVerts is None:
                return {'RUNNING_MODAL'}

            if not select and not deselect:
                self.Mesh.performSmooth(rangeVerts, useColorAttr=True)
                # Update the max groups info.
                if drawInfo3d.currentMaxGroups != self.Mesh.currentMaxGroups:
                    drawInfo3d.currentMaxGroups = self.Mesh.currentMaxGroups
                    drawInfo3d.updateView()
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
            self.Mesh.getDeformedPointPositions()

        if event.type == 'MOUSEMOVE' and self.frameDrag:
            # Skip evaluation steps to improve performance.
            self.undersamplingSteps += 1
            if self.undersamplingSteps < const.UNDERSAMPLING:
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

        # Pie menu
        if event.type == self.pieMenu_key and event.value == 'PRESS':
            bpy.ops.wm.call_menu_pie(name="SMOOTHWEIGHTS_MT_pie")

        # Affect selected
        if event.type == self.affectSelected_key and event.value == 'PRESS':
            value = not smooth_weights.affectSelected
            smooth_weights.affectSelected = value
            self.affectSelected = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Use selection
        if event.type == self.useSelection_key and event.value == 'PRESS':
            value = not smooth_weights.useSelection
            smooth_weights.useSelection = value
            self.useSelection = value
            if value:
                self.setSelectionMode(context, active=True)
            else:
                self.setSelectionMode(context, active=False)
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Curve
        if event.type in ['ONE', 'TWO', 'THREE', 'FOUR'] and event.value == 'PRESS':
            values = {'ONE': 'NONE', 'TWO': 'LINEAR', 'THREE': 'SMOOTH', 'FOUR': 'NARROW'}
            smooth_weights.curve = values[event.type]
            self.curve = values[event.type]
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Ignore backside
        if event.type == self.ignoreBackside_key and event.value == 'PRESS':
            value = not smooth_weights.ignoreBackside
            smooth_weights.ignoreBackside = value
            self.ignoreBackside = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Ignore lock
        if event.type == self.ignoreLock_key and event.value == 'PRESS':
            value = not smooth_weights.ignoreLock
            smooth_weights.ignoreLock = value
            self.ignoreLock = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Radius and strength
        if event.type in [self.radius_key, self.strength_key, self.volumeRange_key]:
            self.setBrushValues(context, event)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Volume
        if event.type == self.volume_key and event.value == 'PRESS':
            value = not smooth_weights.volume
            smooth_weights.volume = value
            self.volume = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Use islands
        if event.type == self.islands_key and event.value == 'PRESS':
            value = not smooth_weights.islands
            smooth_weights.islands = value
            self.islands = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Normalize
        if event.type == self.normalize_key and event.value == 'PRESS':
            value = not smooth_weights.normalize
            smooth_weights.normalize = value
            self.normalize = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Max groups
        if event.type == self.maxGroups_key:
            if event.value == 'PRESS':
                self.setMaxGroups = True
            elif event.value == 'RELEASE':
                self.setMaxGroups = False

        if event.type == self.value_up_key and event.value == 'PRESS' and self.setMaxGroups:
            value = smooth_weights.maxGroups + 1
            smooth_weights.maxGroups = value
            self.maxGroups = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.value_down_key and event.value == 'PRESS' and self.setMaxGroups:
            value = smooth_weights.maxGroups - 1
            value = value if value >= 0 else 0
            smooth_weights.maxGroups = value
            self.maxGroups = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if self.setMaxGroups:
            return {'RUNNING_MODAL'}

        # Vertex groups
        if event.type == self.vertexGroups_key:
            if event.value == 'PRESS':
                self.setVertexGroups = True
            elif event.value == 'RELEASE':
                self.setVertexGroups = False

        if event.type == self.value_up_key and event.value == 'PRESS' and self.setVertexGroups:
            value = const.VERTEX_GROUPS_ITEMS.index(smooth_weights.vertexGroups) + 1
            value = value % 3
            smooth_weights.vertexGroups = const.VERTEX_GROUPS_ITEMS[value]
            self.vertexGroups = const.VERTEX_GROUPS_ITEMS[value]
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.value_down_key and event.value == 'PRESS' and self.setVertexGroups:
            value = const.VERTEX_GROUPS_ITEMS.index(smooth_weights.vertexGroups) - 1
            value = value % 3
            smooth_weights.vertexGroups = const.VERTEX_GROUPS_ITEMS[value]
            self.vertexGroups = const.VERTEX_GROUPS_ITEMS[value]
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if self.setVertexGroups:
            return {'RUNNING_MODAL'}

        # Blend vertex groups
        if event.type == self.blend_key and event.value == 'PRESS':
            value = not smooth_weights.blend
            smooth_weights.blend = value
            self.blend = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Oversampling
        if event.type == self.oversampling_key:
            if event.value == 'PRESS':
                self.setOversampling = True
            elif event.value == 'RELEASE':
                self.setOversampling = False

        if event.type == self.value_up_key and event.value == 'PRESS' and self.setOversampling:
            value = smooth_weights.oversampling + 1
            smooth_weights.oversampling = value
            self.oversampling = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.value_down_key and event.value == 'PRESS' and self.setOversampling:
            value = smooth_weights.oversampling - 1
            if value < 1:
                value = 1
            smooth_weights.oversampling = value
            self.oversampling = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if self.setOversampling:
            return {'RUNNING_MODAL'}

        # Flood
        if event.type == self.flood_key and event.value == 'PRESS':
            self.Mesh.floodSmooth(useSelection=self.useSelection,
                                  affectSelected=self.affectSelected,
                                  useColorAttr=True,
                                  strength=self.strength)
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Selection
        if event.type == self.select_key and event.value == 'PRESS':
            bpy.ops.object.mode_set(mode='OBJECT')
            smooth_weights.select = not smooth_weights.select
            smooth_weights.deselect = False
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.deselect_key and event.value == 'PRESS':
            bpy.ops.object.mode_set(mode='OBJECT')
            smooth_weights.deselect = not smooth_weights.deselect
            smooth_weights.select = False
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        if event.type == self.clearSelection_key and event.value == 'PRESS':
            self.Mesh.clearSelection()
            return {'RUNNING_MODAL'}

        # Use symmetry
        if event.type == self.useSymmetry_key and event.value == 'PRESS':
            value = not smooth_weights.useSymmetry
            smooth_weights.useSymmetry = value
            self.useSymmetry = value
            drawInfo3d.updateView()
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        # Undo
        if event.type == self.undo_key and event.value == 'PRESS':
            self.Mesh.undoStroke()
            return {'RUNNING_MODAL'}

        # --------------------------------------------------------------
        # Exit
        # --------------------------------------------------------------

        # End the operator.
        if event.type in {'RET', 'NUMPAD_ENTER'}:
            # Match the vertex selection with the selection colors.
            if prefs.getPreferences().keep_selection:
                self.Mesh.colorToSelection()
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

    @classmethod
    def mouse3d(cls, context, event):
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
        backside = self.ignoreBackside and utils.isBackface(viewVector, normal)
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
        closestIndex, closestDistance = self.Mesh.getClosestFaceVertex(pos, index, self.radius)

        if closestIndex is None:
            return

        if self.volume:
            radiusVerts = self.Mesh.getVerticesInVolume(pos, self.radius, local=False)
        else:
            radiusVerts = self.Mesh.getVerticesOnSurface(pos, closestIndex, self.radius)

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

    def getKeymaps(self):
        """Get the current key maps.
        """
        self.affectSelected_key = prefs.getPreferences().affectSelected_key.upper()
        self.blend_key = prefs.getPreferences().blend_key.upper()
        self.clearSelection_key = prefs.getPreferences().clearSelection_key.upper()
        self.deselect_key = prefs.getPreferences().deselect_key.upper()
        self.flood_key = prefs.getPreferences().flood_key.upper()
        self.ignoreBackside_key = prefs.getPreferences().ignoreBackside_key.upper()
        self.ignoreLock_key = prefs.getPreferences().ignoreLock_key.upper()
        self.islands_key = prefs.getPreferences().islands_key.upper()
        self.maxGroups_key = prefs.getPreferences().maxGroups_key.upper()
        self.normalize_key = prefs.getPreferences().normalize_key.upper()
        self.oversampling_key = prefs.getPreferences().oversampling_key.upper()
        self.pieMenu_key = prefs.getPreferences().pieMenu_key.upper()
        self.radius_key = prefs.getPreferences().radius_key.upper()
        self.select_key = prefs.getPreferences().select_key.upper()
        self.strength_key = prefs.getPreferences().strength_key.upper()
        self.useSelection_key = prefs.getPreferences().useSelection_key.upper()
        self.useSymmetry_key = prefs.getPreferences().useSymmetry_key.upper()
        self.value_up_key = prefs.getPreferences().value_up_key.upper()
        self.value_down_key = prefs.getPreferences().value_down_key.upper()
        self.vertexGroups_key = prefs.getPreferences().vertexGroups_key.upper()
        self.volume_key = prefs.getPreferences().volume_key.upper()
        self.volumeRange_key = prefs.getPreferences().volumeRange_key.upper()

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

        lines = ["{}: {}".format(strings.LMB_LABEL, strings.SMOOTH_LABEL),
                 "{}: {}".format(self.radius_key, strings.RADIUS_LABEL),
                 "{}: {}".format(self.strength_key, strings.STRENGTH_LABEL),
                 "{}+{}/{}/{}: {}".format(strings.CONTROL_LABEL,
                                          self.radius_key,
                                          self.strength_key,
                                          self.volumeRange_key,
                                          strings.SLOW_LABEL),
                 "{}+{}/{}/{}: {}".format(strings.SHIFT_LABEL,
                                          self.radius_key,
                                          self.strength_key,
                                          self.volumeRange_key,
                                          strings.FAST_LABEL),
                 "{}: {}".format(self.useSelection_key, strings.USE_SELECTION_LABEL),
                 "{}: {}".format(self.affectSelected_key, strings.AFFECT_SELECTED_LABEL),
                 "{}: {}".format(self.ignoreBackside_key, strings.IGNORE_BACKSIDE_LABEL),
                 "{}: {}".format(self.ignoreLock_key, strings.IGNORE_LOCK_LABEL),
                 "{}: {}".format(self.normalize_key, strings.NORMALIZE_LABEL),
                 "{}: {} {}/{}".format(self.oversampling_key, strings.OVERSAMPLING_LABEL, up, down),
                 "{}: {}".format(self.volume_key, strings.VOLUME_LABEL),
                 "{}: {}".format(self.islands_key, strings.USE_ISLANDS_LABEL),
                 "{}: {} {}/{}".format(self.maxGroups_key, strings.MAX_GROUPS_LABEL, up, down),
                 "{}: {} {}/{}".format(self.vertexGroups_key, strings.VERTEX_GROUPS_LABEL, up, down),
                 "{}: {}".format(self.blend_key, strings.BLEND_LABEL),
                 "{}: {}".format(self.useSymmetry_key, strings.USE_SYMMETRY_LABEL),
                 "{}: {}".format(self.select_key, strings.TOGGLE_SELECT_LABEL),
                 "{}: {}".format(self.deselect_key, strings.TOGGLE_DESELECT_LABEL),
                 "{}: {}".format(self.clearSelection_key, strings.CLEAR_SELECTION_LABEL),
                 "{}: {}".format(self.flood_key, strings.FLOOD_LABEL),
                 strings.TIME_CHANGE_LABEL,
                 strings.CANCEL_LABEL]

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
        if self.Mesh.obj.mode not in ['OBJECT', 'WEIGHT_PAINT']:
            bpy.ops.object.mode_set(mode='OBJECT')
        if active:
            # Store the current shading mode.
            self.shadingMode = context.space_data.shading.type
            self.shadingType = context.space_data.shading.color_type
            context.space_data.shading.type = 'SOLID'
            context.space_data.shading.color_type = 'VERTEX'
        else:
            # Turn off selection and deselection
            context.object.smooth_weights.select = False
            context.object.smooth_weights.deselect = False
            # Set the shading mode and type only if it has been stored
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
        self.Mesh.setSelection(indices)

    def paintDeselect(self, vertData):
        """Remove the selection color for all given vertices.

        :param vertData: The list with vertex data from the brush range.
        :type vertData: list(tuple(int, float, int/None))
        """
        indices = [index for index, dist, v in vertData]
        self.Mesh.removeSelection(indices)


# ----------------------------------------------------------------------
# Flood Operator
# ----------------------------------------------------------------------

class SMOOTHWEIGHTS_OT_Flood(bpy.types.Operator):
    """Operator class for flood-smoothing the object's weights.
    """
    bl_idname = "smoothweights.flood"
    bl_label = strings.FLOOD_SMOOTH_LABEL
    bl_description = strings.DESCR_FLOOD_SMOOTH
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty(name=strings.RADIUS_LABEL,
                                    default=const.RADIUS,
                                    min=0,
                                    description=strings.ANN_RADIUS)
    strength: bpy.props.FloatProperty(name=strings.STRENGTH_LABEL,
                                      default=const.STRENGTH,
                                      min=0.001,
                                      max=1,
                                      description=strings.ANN_STRENGTH)
    oversampling: bpy.props.IntProperty(name=strings.OVERSAMPLING_LABEL,
                                        default=const.OVERSAMPLING,
                                        min=1,
                                        description=strings.ANN_OVERSAMPLING)
    useSelection: bpy.props.BoolProperty(name=strings.USE_SELECTION_LABEL,
                                         default=const.USE_SELECTION,
                                         description=strings.ANN_USE_SELECTION)
    affectSelected: bpy.props.BoolProperty(name=strings.AFFECT_SELECTED_LABEL,
                                           default=const.AFFECT_SELECTED,
                                           description=strings.ANN_AFFECT_SELECTED)
    ignoreLock: bpy.props.BoolProperty(name=strings.IGNORE_LOCK_LABEL,
                                       default=const.IGNORE_LOCK,
                                       description=strings.ANN_IGNORE_LOCK)
    normalize: bpy.props.BoolProperty(name=strings.NORMALIZE_LABEL,
                                      default=const.NORMALIZE,
                                      description=strings.ANN_NORMALIZE)
    maxGroups: bpy.props.IntProperty(name=strings.MAX_GROUPS_LABEL,
                                     default=const.MAX_GROUPS,
                                     min=0,
                                     description=strings.ANN_MAX_GROUPS)
    vertexGroups: bpy.props.EnumProperty(name=strings.VERTEX_GROUPS_LABEL,
                                         items=const.VERTEX_GROUPS,
                                         default=1)
    blend: bpy.props.BoolProperty(name=strings.BLEND_LABEL,
                                  default=const.BLEND,
                                  description=strings.ANN_BLEND)
    volume: bpy.props.BoolProperty(name=strings.VOLUME_LABEL,
                                   default=const.VOLUME,
                                   description=strings.ANN_VOLUME)
    volumeRange: bpy.props.FloatProperty(name=strings.VOLUME_RANGE_LABEL,
                                         default=const.VOLUME_RANGE,
                                         min=0.001,
                                         max=1,
                                         description=strings.ANN_VOLUME_RANGE)
    useSymmetry: bpy.props.BoolProperty(name=strings.USE_SYMMETRY_LABEL,
                                        default=const.USE_SYMMETRY,
                                        description=strings.ANN_USE_SYMMETRY)

    Mesh = None
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
        self.Mesh = Mesh()
        self.Mesh.setup(obj=context.object, allowModifiers=True)

        start = time.time()
        self.Mesh.floodSmooth(useSelection=self.useSelection,
                              affectSelected=self.affectSelected,
                              useColorAttr=False,
                              strength=self.strength)
        duration = time.time() - start

        # Reset the mesh.
        self.Mesh.reset()

        # Copy the settings to the object properties.
        self.setSettings(context)
        # Mark the operator ready for redo.
        self.redo = True

        msg = strings.INFO_FLOOD_FINISHED
        timeInfo = ". "
        if prefs.getPreferences().show_time:
            timeInfo = " in {:.3f} seconds.".format(duration)
        self.report({'INFO'}, msg + timeInfo)

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
            self.Mesh.revertWeights()

        # Reset the mesh.
        self.Mesh.reset()

        return {'CANCELLED'}

    def invoke(self, context, event):
        """Invoke the operator.

        :param context: The current context.
        :type context: bpy.context
        :param event: The current event.
        :type event: bpy.types.Event
        """
        self.affectSelected = context.object.smooth_weights.affectSelected
        self.blend = context.object.smooth_weights.blend
        self.ignoreLock = context.object.smooth_weights.ignoreLock
        self.maxGroups = context.object.smooth_weights.maxGroups
        self.normalize = context.object.smooth_weights.normalize
        self.oversampling = context.object.smooth_weights.oversampling
        self.radius = context.object.smooth_weights.radius
        self.strength = context.object.smooth_weights.strength
        self.useSelection = context.object.smooth_weights.useSelection
        self.useSymmetry = context.object.smooth_weights.useSymmetry
        self.vertexGroups = context.object.smooth_weights.vertexGroups
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
        context.object.smooth_weights.blend = self.blend
        context.object.smooth_weights.ignoreLock = self.ignoreLock
        context.object.smooth_weights.maxGroups = self.maxGroups
        context.object.smooth_weights.normalize = self.normalize
        context.object.smooth_weights.oversampling = self.oversampling
        context.object.smooth_weights.radius = self.radius
        context.object.smooth_weights.strength = self.strength
        context.object.smooth_weights.useSelection = self.useSelection
        context.object.smooth_weights.useSymmetry = self.useSymmetry
        context.object.smooth_weights.vertexGroups = self.vertexGroups
        context.object.smooth_weights.volume = self.volume
        context.object.smooth_weights.volumeRange = self.volumeRange


# ----------------------------------------------------------------------
# Tool Operator Functions
# ----------------------------------------------------------------------

def limitGroups(obj, maxGroups=1, normalize=True, vertexGroups="DEFORM"):
    """Limit the weights of the current selection or all vertices to the
    given maximum number of vertex groups.

    :param obj: The mesh object.
    :type obj: bpy.types.Object
    :param maxGroups: The number of maximum groups per vertex.
    :type maxGroups: int
    :param normalize: True, if the weights across all groups should be
                      normalized.
    :type normalize: bool
    :param vertexGroups: The string defining which vertex groups are
                         affected. (ALL, DEFORM, OTHER)
    :type vertexGroups: str
    """
    # Nothing to do if there is no limit to the number of groups.
    if maxGroups == 0:
        return

    weightObj = weights.Weights(obj)

    verts = set()
    if obj.mode == 'EDIT':
        verts = utils.getVertexSelection(obj)
    else:
        # Get all vertices indices.
        for i in range(len(obj.data.vertices)):
            verts.add(i)

    # Get the weights for all indices.
    weightMap = weightObj.weightsForVertexIndices(list(verts))
    if weightMap is None:
        return strings.ERROR_NO_DEFORMATION

    # Get the group indices which don't match the current filter mode.
    skipGroupIds = utils.getUnaffectedGroupIndices(obj, vertexGroups=vertexGroups)

    weightData = {}

    for index in verts:
        weightList = weightMap[index]
        # Only edit the weights if the current number of groups exceeds
        # the max limit.
        if len(weightList) > maxGroups:
            weightList = utils.sortDict(data=weightList,
                                        reverse=True,
                                        maxCount=maxGroups,
                                        skipIndices=skipGroupIds)
            if normalize:
                weightList = weightObj.normalizeVertexGroup(weightData=weightList,
                                                            skipIndices=skipGroupIds)
            weightData[index] = weightList

    if weightData:
        weightObj.setVertexWeights(weightData, editMode=True)


# ----------------------------------------------------------------------
# Tool Operators
# ----------------------------------------------------------------------

class SMOOTHWEIGHTS_OT_LimitGroups(bpy.types.Operator):
    """Operator class for selecting mapped vertices.
    """
    bl_idname = "smoothweights.limit_groups"
    bl_label = strings.LIMIT_GROUPS_LABEL
    bl_description = strings.DESCR_LIMIT_GROUPS
    bl_options = {'REGISTER', 'UNDO'}

    maxGroups: bpy.props.IntProperty(name=strings.MAX_GROUPS_LABEL,
                                     default=const.MAX_GROUPS,
                                     min=0,
                                     description=strings.ANN_MAX_GROUPS)
    normalize: bpy.props.BoolProperty(name=strings.NORMALIZE_LABEL,
                                      default=const.NORMALIZE,
                                      description=strings.ANN_NORMALIZE)
    vertexGroups: bpy.props.EnumProperty(name=strings.VERTEX_GROUPS_LABEL,
                                         items=const.VERTEX_GROUPS,
                                         default=1)

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        limitGroups(context.object, self.maxGroups, self.normalize, self.vertexGroups)
        return {'FINISHED'}


# ----------------------------------------------------------------------
# Mesh Class
# ----------------------------------------------------------------------

class Mesh(object):
    """Class for evaluating the current mesh and storing relevant data
    for the smoothing process.
    """
    def __init__(self):
        """Initialize.
        """
        self.obj = None
        self.mat = None

        self.bm = None

        # The weights class instance.
        self.weightObj = None

        # The tool settings.
        self.props = None

        # The maximum number of groups a vertex currently has.
        self.currentMaxGroups = 0

        # The color value and channel index to use as the selection
        # identifier.
        self.colorValue = 0.0
        self.colorIndex = 0

        # The current selection.
        self.selectedVertices = None

        # The selection color attribute.
        self.userColorAttr = None
        self.selectionColors = None

        # The deformed positions.
        self.pointsDeformed = None

        # The group indices which don't match the current filter mode.
        self.skipGroupIds = None

        # The current weights.
        self.cancelWeights = None
        self.weightList = None

        # The list storing if a vertex has been smoothed.
        self.cancelIndices = None

        # The weights undo list.
        self.undoWeights = []
        self.undoIndices = []

        self.kdLocal = None
        self.kdDeformed = None

    def setup(self, obj, allowModifiers=True):
        """Prepare the mesh for smoothing.

        :param obj: The mesh object.
        :type obj: bpy.types.Object
        :param allowModifiers: True, if topology-changing modifiers are
                               allowed. For interactive paint mode this
                               needs to be False.
        :type allowModifiers: bool

        :return: True, if the setup was successful. False, if the
                 deformed points count doesn't match the base mesh.
        :rtype: bool
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
        self.bm.edges.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()

        # Create the weights class instance.
        self.weightObj = weights.Weights(obj)

        # The tool settings.
        self.props = self.obj.smooth_weights

        # Get the deformed positions.
        self.getDeformedPointPositions(allowModifiers=allowModifiers)
        if not allowModifiers and not len(self.pointsDeformed):
            return False

        # Get the current selection.
        self.getCurrentSelection()

        # Get the selection color attribute.
        self.selectionColors = self.getColorAttribute()
        # Store the color identifiers.
        self.setColorIdentifier()

        # Get the group indices which don't match the current filter
        # mode.
        self.setUnaffectedGroupIndices()

        self.weightList = self.allVertexWeights()
        if self.weightList is None:
            return False

        # The list storing if a vertex has been smoothed.
        self.cancelIndices = set()

        self.kdLocal = self.kdTree()
        self.kdDeformed = self.kdTree(local=False)

        return True

    def reset(self):
        """Free the bmesh memory.
        """
        self.bm.free()
        self.obj = None

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

    def getDeformedPointPositions(self, allowModifiers=True):
        """Get the deformed positions.

        During mesh setup this is also used to determine if the vertex
        count is different between the base mesh and the evaluated mesh
        including modifiers.
        If a modifier is active which affects the vertex count the brush
        won't be able to find the correct indices in relation to the
        base mesh.
        In this case the list of deformed points will be empty to
        indicate that topology related modifiers are active.

        :param allowModifiers: True, if topology-changing modifiers are
                               allowed. For interactive paint mode this
                               needs to be False.
        :type allowModifiers: bool
        """
        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        # If the object is in edit mode the depsgraph evaluation will
        # fail and cause a crash.
        bpy.ops.object.mode_set(mode='OBJECT')
        self.pointsDeformed = self.deformedPointPositions(allowModifiers=allowModifiers)
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

    def deformedPointPositions(self, allowModifiers=True):
        """Return a list with the deformed point positions rather than
        the local coordinates, by evaluating the despgraph.

        :param allowModifiers: True, if topology-changing modifiers are
                               allowed. For interactive paint mode this
                               needs to be False.
        :type allowModifiers: bool

        :return: A list with the deformed point positions.
        :rtype: list(Vector)
        """
        # Get the number of vertices for matching against the deformed
        # points count.
        vtxCount = self.numVertices()

        points = []
        depsgraph = bpy.context.evaluated_depsgraph_get()
        objEval = self.obj.evaluated_get(depsgraph)

        # If the vertex count doesn't match return an empty list.
        if not allowModifiers and vtxCount != len(objEval.data.vertices):
            depsgraph.update()
            return points

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

    def getVertexWeight(self, index, groupId):
        """Return the weight value of the given vertex and the given
        group.

        If the vertex or group index doesn't exist return a zero weight
        value.

        :param index: The vertex index.
        :type index: int
        :param groupId: The vertex group index.
        :type groupId: int

        :return: The weight of the vertex for the given group.
        :rtype: float
        """
        if index in self.weightList and groupId in self.weightList[index]:
            return self.weightList[index][groupId]
        return 0.0

    def allVertexWeights(self):
        """Return all weights for all vertices.

        :return: A list with all weights for all vertices.
        :rtype: list(list(tuple(float, int)))
        """
        allWeights = {}
        self.cancelWeights = {}

        indices = [i for i in range(self.numVertices())]
        maxGroups = [self.currentMaxGroups]
        weightMap = self.weightObj.weightsForVertexIndices(indices, maxGroups, self.skipGroupIds)
        if weightMap is None:
            return

        # Update the current max number of vertex groups.
        self.updateMaxGroups(maxGroups[0])

        for i in range(self.numVertices()):
            data = weightMap[i]
            allWeights[i] = data

            # Copy the weight data for undo.
            # This is much faster than having to copy the complete
            # weight dictionary later via deepcopy().
            self.cancelWeights[i] = data.copy()
        return allWeights

    def undoStroke(self):
        """Reset the weights for all indices which have been edited
        during the last brush stroke.
        """
        if len(self.undoIndices):
            indices = self.undoIndices.pop(0)
            weightList = self.undoWeights.pop(0)
            for i in indices:
                self.weightList[i] = weightList[i]
            self.weightObj.setWeightsFromVertexList(indices, weightList)

    def revertWeights(self):
        """Reset to the previous weights when cancelling the tool.
        """
        self.weightObj.setWeightsFromVertexList(list(self.cancelIndices), self.cancelWeights)

    def updateMaxGroups(self, count):
        """Update the current maximum number of vertex groups of the
        mesh.

        :param count: The new number of max groups.
        :type count: int
        """
        current = self.currentMaxGroups
        self.currentMaxGroups = count if current < count else current

    def setUnaffectedGroupIndices(self):
        """Store all vertex group indices which don't belong to the
        given vertex group type.
        """
        self.skipGroupIds = utils.getUnaffectedGroupIndices(self.obj,
                                                            vertexGroups=self.props.vertexGroups)

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
        :rtype: kdtree.KDTree()
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
        if not self.props.islands and self.bm.verts[centerIndex].is_boundary:
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
                    if not self.props.islands:
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

        edgeLength = utils.averageEdgeLength(self.bm.verts[vertIndex])

        connVerts = self.connectedVertices(vertIndex)

        # Search for vertices in range using the KDTree.
        pos = self.mat @ self.obj.data.vertices[vertIndex].co
        rangeVerts = self.kdLocal.find_range(pos, edgeLength)
        sortedVerts = sorted(rangeVerts, key=lambda x: x[2])
        # The found vertices are sorted by distance; the nearest first.
        # The first vertex should be of the given index, therefore the
        # next should be the opposite vertex.
        for i in range(len(sortedVerts)):
            if sortedVerts[i][1] != vertIndex and sortedVerts[i][1] not in connVerts:
                return sortedVerts[i][1]

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
        :param useColorAttr: True, if the color attribute should be used
                             for the selection (in paint mode), rather
                             than the current vertex selection.
        :type useColorAttr: bool
        :param strength: The smoothing strength.
        :type strength: float
        """
        # Needed for the paint operator but not for the flood operator.
        self.undoIndices.insert(0, [])
        self.undoWeights.insert(0, {})

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

        self.performSmooth(vertData, flood=True, useColorAttr=useColorAttr)

    def performSmooth(self, vertData, flood=False, useColorAttr=False):
        """Smooth all vertices within the brush radius.

        :param vertData: The list with vertex data from the brush range.
        :type vertData: list(tuple(int, float, int/None))
        :param flood: True, if flooding should be performed.
                      This disables the scale value being affected by
                      the curve falloff.
        :type flood: bool
        :param useColorAttr: True, if the color attribute should be used
                             for the selection (in paint mode), rather
                             than the current vertex selection.
        :type useColorAttr: bool
        """
        weightObj = weights.Weights(self.obj)

        # Get the symmetry map.
        orderMap = []
        if self.props.useSymmetry and symmetryMap.hasValidOrderMap(self.obj):
            orderMap = symmetryMap.getOrderMap(self.obj)

        # The smoothing is performed in three steps to increase
        # efficiency in relation to possible oversampling.
        # 1. Evaluate all vertices of the brush radius and collect their
        #    connected indices, or neighbours in volume mode.
        #    This way, the calculation intensive processing of the mesh
        #    only has to be performed once, no matter the number of
        #    oversampling steps.
        connectedData = []
        for index, value, indexBound in vertData:

            if useColorAttr:
                isSel = self.isSelected(index)
            else:
                isSel = self.obj.data.vertices[index].select
            affectState = isSel if self.props.affectSelected else not isSel

            # Only process affected vertices.
            if not self.props.useSelection or (self.props.useSelection and affectState):
                if index not in self.undoWeights[0]:
                    self.undoIndices[0].append(index)
                    self.undoWeights[0][index] = {key: value for key, value in self.weightList[index].items()}
                connectedData.append(self.getConnectedData(index, value, indexBound, flood))

        # 2. Perform the smoothing of the weights.
        #    When oversampling, the important part is to use the new
        #    weights as the base for the next oversampling pass.
        #    New and old weights shouldn't get mixed up because this
        #    would cause jitter, since the weights and indices are not
        #    in order.
        weightData = {}
        for sample in range(self.props.oversampling):
            smoothed = {}
            for index, scale, indexBound, connected, volumeScale in connectedData:
                self.computeWeights(index, scale, indexBound, connected, volumeScale, smoothed, self.skipGroupIds)

            # 3. Collect all processed vertices and their final weights
            #    for setting the values in the vertex groups.
            for index, scale, indexBound, connected, volumeScale in connectedData:
                mirrorIndex = self.getSymmetryIndex(index, orderMap)
                mirrorWeights = None
                if mirrorIndex:
                    mirrorWeights = weightObj.mirrorGroupAssignment(weightData=smoothed[index],
                                                                    weightDataMirror=self.weightList[mirrorIndex],
                                                                    skipIndices=self.skipGroupIds)
                if sample == self.props.oversampling - 1:
                    # Get the new weights for applying.
                    self.cancelIndices.add(index)
                    weightData[index] = smoothed[index]
                    # Update the current max number of vertex groups.
                    groupItems = [i for i in smoothed[index] if i not in self.skipGroupIds]
                    self.updateMaxGroups(len(groupItems))
                    if mirrorIndex:
                        self.cancelIndices.add(mirrorIndex)
                        weightData[mirrorIndex] = mirrorWeights
                self.weightList[index] = smoothed[index]
                if mirrorIndex:
                    self.weightList[mirrorIndex] = mirrorWeights
                # Add the boundary vertex if in surface mode and
                # islands should not be respected.
                if not self.props.islands and indexBound is not None:
                    mirrorIndex = self.getSymmetryIndex(indexBound, orderMap)
                    mirrorWeights = None
                    if mirrorIndex:
                        mirrorWeights = weightObj.mirrorGroupAssignment(weightData=smoothed[indexBound],
                                                                        weightDataMirror=self.weightList[mirrorIndex],
                                                                        skipIndices=self.skipGroupIds)
                    if sample == self.props.oversampling - 1:
                        self.cancelIndices.add(indexBound)
                        weightData[indexBound] = smoothed[indexBound]
                        if mirrorIndex:
                            self.cancelIndices.add(mirrorIndex)
                            weightData[mirrorIndex] = mirrorWeights
                    self.weightList[indexBound] = smoothed[indexBound]
                    if mirrorIndex:
                        self.weightList[mirrorIndex] = mirrorWeights

        # Apply the weights.
        self.weightObj.setVertexWeights(weightData, editMode=False)

    def getConnectedData(self, index, value, indexBound, flood=False):
        """Return the data of all connected vertices, either by surface
        or by volume, which are used as a source to calculate the
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
        if not self.props.volume:
            connected.extend(self.connectedVertices(index))
            if indexBound is not None:
                connected.extend(self.connectedVertices(indexBound))
        else:
            pos = self.mat @ self.obj.data.vertices[index].co
            vertData = self.getVerticesInVolume(pos,
                                                self.props.radius * self.props.volumeRange,
                                                local=True)
            connected = [i for i, v, b in vertData]
            volumeScale = [v for i, v, b in vertData]

        if not flood:
            scale = getFalloffValue(value, self.props.curve) * self.getStrength()
        else:
            scale = self.props.strength

        return index, scale, indexBound, connected, volumeScale

    def computeWeights(self, index, scale, indexBound, connected, volumeScale, smoothed,
                       skipIndices=[]):
        """Calculate an interpolated weight value from the weights of
        the connected vertices.

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
        :param smoothed: The dictionary of smoothed weights.
        :type smoothed: dict(dict())
        :param skipIndices: The list of group indices which should not
                            be considered.
        :type skipIndices: list(int)
        """
        numConnected = len(connected)

        maxWeight = 0.0
        maxWeightLocked = 0.0
        maxWeightUnlocked = 0.0
        hasLocks = False

        # Collect all group indices for the vertex.
        connectedGroups = set()

        # The number of affected vertex groups which belong to connected
        # vertices in filter mode 'OTHER'.
        includedCount = 0
        # The number of affected vertex groups which the current vertex
        # is not assigned to.
        unassignedCount = 0

        # Get the group indices the vertex is assigned to.
        for groupId in self.weightList[index]:
            connectedGroups.add(groupId)
        # Add all group indices of all connected vertices.
        for c in range(numConnected):
            for groupId in self.weightList[connected[c]]:
                connectedGroups.add(groupId)

                # The assignment comparison can be skipped if the group
                # index matches the helper index.
                if groupId == self.weightObj.numGroups:
                    continue

                # When the filter mode 'OTHER' is active, smoothing
                # should be limited to non-deforming vertex groups only.
                # Because in this case it's possible that connected
                # vertices are not part of any non-deforming groups.
                # If there is no limiting mechanism those vertices would
                # pick up the weights from connected vertices which are
                # assigned to such vertex groups.
                # Identifying these vertices is done by cross-
                # referencing:
                # - If the connected vertex group is part of the group
                #   indices which are included in the smoothing.
                # - If the connected vertex group is also influencing
                #   the current vertex.
                # If the number of participating vertex groups matches
                # the number of groups the vertex is not assigned to
                # exclude it from the smoothing process.
                # All other vertices which share at least one affected
                # vertex group can be smoothed.
                if self.props.vertexGroups == "OTHER":
                    if groupId not in skipIndices:
                        includedCount += 1
                        if groupId not in self.weightList[index]:
                            unassignedCount += 1

            # When smoothing 'OTHER' vertex groups, vertices on the edge
            # of a vertex group may need to get blended.
            # The connected vertices outside the group may not have any
            # group assignment or are not assigned to deforming groups.
            # In this case there are no groups affected by smoothing.
            # To be able to blend values some other value needs to
            # exist. This is accomplished by creating a virtual or
            # temporary group with an index matching the number of
            # groups. This extra group is used during the entire
            # smoothing process but ignored when setting any weight
            # values.
            if self.props.blend and self.props.vertexGroups == "OTHER":
                # Add the temporary group to the list of groups to be
                # processed.
                connectedGroups.add(self.weightObj.numGroups)
                # If the temporary group isn't already included in the
                # weight list of the connected vertex, add the group and
                # set it's weight to the remainder of the weight sum.
                if not self.weightObj.numGroups in self.weightList[connected[c]]:
                    self.addOffBorderWeight(connected[c], skipIndices)

        if self.props.vertexGroups == "OTHER" and unassignedCount == includedCount:
            # Copy the original weights to the smoothed weights
            # dictionary, so that the index exists for later processing.
            smoothed[index] = self.weightList[index]
            # Copy the vertex weights to the boundary vertex if in
            # surface mode and islands should not be respected.
            if not self.props.islands and indexBound is not None:
                smoothed[indexBound] = self.weightList[index]
            return

        # When blending the border of non-deforming groups the weight
        # list is missing the temporary group for correctly normalizing
        # the weights before applying.
        # As a result, the blending would snap back and start over for
        # all weights that already have been smoothed during a
        # previously executed stroke.
        # To be able to continue smoothing the temporary group weight
        # needs to be reconstructed from the existing weight values.
        # This is only necessary for the first evaluation sample when
        # the temporary group index is not yet included in the weight
        # list.
        # This means, that the temporary group has been included in the
        # connected groups but is not yet contained in the weight list.
        if (self.props.blend and
                self.props.vertexGroups == "OTHER" and
                self.weightObj.numGroups in connectedGroups and
                self.weightObj.numGroups not in self.weightList[index]):
            self.addOffBorderWeight(index, skipIndices)

        # --------------------------------------------------------------
        # Weight calculation
        # --------------------------------------------------------------

        weightList = {}

        for groupId in connectedGroups:
            # If blending open group borders is disabled ignore the
            # temporary group index.
            if not self.props.blend and groupId == self.weightObj.numGroups:
                continue

            weight = self.getVertexWeight(index, groupId)

            # Only smooth vertex groups which match the filter mode.
            if groupId in skipIndices:
                # Add the weight to the list.
                # The group assignment needs to be kept or it will lead
                # the vertex being removed from the group once the new
                # weights get applied.
                # But only keep the weight if it's not zero.
                # Otherwise it will lead to new group assignments which
                # are unintentional.
                # getVertexWeight() returns a 0 value, if the group
                # assignment doesn't exist for the vertex. This means,
                # if a vertex isn't assigned to the current group the
                # returned weight value is zero and would then get added
                # to the weight list, hence adding a new group to
                # the vertex.
                # This behaviour is needed for the smoothing process but
                # conflicts with distinguishing between deformation and
                # non-deformation groups.
                # Example:
                # A vertex is assigned to both deformation and non-
                # deformation groups.
                # Smoothing the non-deformation groups is working as
                # expected. After switching to smoothing of deformation
                # groups all connected groups are processed. One or more
                # of the connected groups are non-deforming but they
                # don't exist for the current vertex. Since
                # getVertexWeight() returns a zero weight for these
                # groups this zero value gets added to the resulting
                # weight list, adding the vertex to these groups.
                # As a result, when smoothing non-deforming groups
                # afterwards, it's not possible to detect this false
                # assignment and the smoothing is unable to exclude.
                if weight > 0:
                    weightList[groupId] = weight
                continue

            originalWeight = weight
            # Collect the weights per influence.
            # When in volume mode it's possible that the volume range is
            # too small and no vertices are found. In this case there
            # are no weights to average.
            if numConnected and not self.weightObj.isLocked(groupId, self.props.ignoreLock):
                # If there are connected vertices, ignore the current
                # weight to evaluate only the connected weights.
                weight = 0.0
                for c in range(numConnected):
                    mult = scale
                    if self.props.volume:
                        mult = volumeScale[c]
                    connectedWeight = self.getVertexWeight(connected[c], groupId)
                    weight += connectedWeight * mult + originalWeight * (1 - mult)

                weight = weight / numConnected

            maxWeight += weight
            if self.weightObj.isLocked(groupId, self.props.ignoreLock):
                maxWeightLocked += weight
                hasLocks = True
            else:
                maxWeightUnlocked += weight

            # Add the averaged weight to the list.
            weightList[groupId] = weight

        smoothed[index] = weightList

        # --------------------------------------------------------------
        # Set max influences
        # --------------------------------------------------------------

        if numConnected and self.props.maxGroups > 0:
            sortedWeights = utils.sortDict(smoothed[index], reverse=True)

            maxWeight = 0.0
            maxWeightLocked = 0.0
            maxWeightUnlocked = 0.0

            counter = 0
            for groupId in sortedWeights:
                # Only limit vertex groups which match the filter mode.
                if groupId in skipIndices:
                    continue

                weight = sortedWeights[groupId]
                if counter >= self.props.maxGroups:
                    weight = 0.0

                maxWeight += weight
                if self.weightObj.isLocked(groupId, self.props.ignoreLock):
                    maxWeightLocked += weight
                    hasLocks = True
                else:
                    maxWeightUnlocked += weight

                smoothed[index][groupId] = weight

                counter += 1

        # --------------------------------------------------------------
        # Normalize
        # --------------------------------------------------------------

        if self.props.normalize:
            for groupId in smoothed[index]:
                # Only smooth vertex groups which match the filter mode.
                if groupId in skipIndices:
                    continue

                weight = smoothed[index][groupId]

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
                    if not self.weightObj.isLocked(groupId, self.props.ignoreLock):
                        # Make sure the division is not by a zero
                        # weight.
                        if remainingWeight > 0:
                            if maxWeightUnlocked > 0:
                                weight *= remainingWeight / maxWeightUnlocked
                        else:
                            weight = 0.0

                # Clamp because of float precision.
                weight = utils.clamp(weight, 0.0, 1.0)

                smoothed[index][groupId] = weight

        # Copy the vertex weights to the boundary vertex if in surface
        # mode and islands should not be respected.
        if not self.props.islands and indexBound is not None:
            smoothed[indexBound] = smoothed[index]

    def getStrength(self):
        """Return the smoothing strength based on the oversampling.

        :return: The smoothing strength value.
        :rtype: float
        """
        return self.props.strength / self.props.oversampling

    def getSymmetryIndex(self, index, orderMap):
        """Return the symmetry index from the given order map.

        Returns None if the symmetry index doesn't exist or the order
        map is empty.

        :param index: The index of the vertex.
        :type index: int
        :param orderMap: The symmetry map.
        :type orderMap: list(int)

        :return: The symmetry index or None
        :rtype: int or None
        """
        if self.props.useSymmetry and len(orderMap):
            if orderMap[index] != -1:
                return orderMap[index]

    def addOffBorderWeight(self, index, skipIndices=[]):
        """Add the weight value for the virtual vertex group based on
        the existing weights.

        The weight list for the given index will be mutated.

        :param index: The index of the vertex.
        :type index: int
        :param skipIndices: The list of group indices which should not
                            be considered.
        :type skipIndices: list(int)
        """
        total = sum(value for key, value in self.weightList[index].items() if key not in skipIndices)

        if self.props.normalize:
            self.weightList[index][self.weightObj.numGroups] = 1.0 - total


    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def getColorAttribute(self):
        """Return the color attribute if it exists or create a new one.

        :return: The color attribute for the selection.
        :rtype: bpy.types.Attribute
        """
        colors = self.obj.data.color_attributes.get(const.SELECT_COLOR_ATTRIBUTE)
        if not colors:
            colors = self.obj.data.color_attributes.new(name=const.SELECT_COLOR_ATTRIBUTE,
                                                        type='FLOAT_COLOR',
                                                        domain='POINT')
            self.resetColors(colors)

        # Store the currently active colors.
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
            try:
                self.obj.data.color_attributes.remove(self.selectionColors)
            except (Exception,):
                pass
            self.selectionColors = None

        if self.userColorAttr is not None:
            self.obj.data.color_attributes.active_color = self.userColorAttr

    def setSelection(self, indices):
        """Set the selection color for the given list of vertices.

        :param indices: The list of vertex indices to color as selected.
        :type indices: list(int)
        """
        if self.selectionColors is None or not len(self.selectionColors.data):
            return

        # Store the current mode.
        mode = self.obj.mode
        # Set the object mode.
        bpy.ops.object.mode_set(mode="OBJECT")

        color = prefs.getPreferences().selected_color
        color = [utils.linear_to_srgb(c) for c in color]
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

        color = prefs.getPreferences().unselected_color
        color = [utils.linear_to_srgb(c) for c in color]
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

        self.resetColors(self.selectionColors)

        bpy.ops.object.mode_set(mode=mode)

    def resetColors(self, colorAttr):
        """Set all vertex colors in the selection attribute to the
        unselected color.

        :param colorAttr: The color attribute.
        :type colorAttr: bpy.types.Attribute
        """
        color = prefs.getPreferences().unselected_color
        color = [utils.linear_to_srgb(c) for c in color]
        for i in range(self.numVertices()):
            colorAttr.data[i].color = (color[0], color[1], color[2], 1.0)

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
        color = prefs.getPreferences().selected_color
        color = [utils.linear_to_srgb(c) for c in color]
        for c in range(len(color)):
            if self.colorValue < color[c] < 0.99:
                self.colorValue = color[c]
                self.colorIndex = c


# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

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


# ----------------------------------------------------------------------
# Properties
# ----------------------------------------------------------------------

class SmoothWeights_Properties(bpy.types.PropertyGroup):
    """Property group class to make the properties globally available.
    """
    affectSelected: bpy.props.BoolProperty(name=strings.AFFECT_SELECTED_LABEL,
                                           default=const.AFFECT_SELECTED,
                                           description=strings.ANN_AFFECT_SELECTED)
    blend: bpy.props.BoolProperty(name=strings.BLEND_LABEL,
                                  default=const.BLEND,
                                  description=strings.ANN_BLEND)
    curve: bpy.props.EnumProperty(name=strings.CURVE_LABEL,
                                  items=const.CURVE_ITEMS,
                                  default=2,
                                  description=strings.ANN_CURVE)
    deselect: bpy.props.BoolProperty(default=const.DESELECT,
                                     description=strings.ANN_DESELECT)
    ignoreBackside: bpy.props.BoolProperty(name=strings.IGNORE_BACKSIDE_LABEL,
                                           default=const.IGNORE_BACKSIDE,
                                           description=strings.ANN_IGNORE_BACKSIDE)
    ignoreLock: bpy.props.BoolProperty(name=strings.IGNORE_LOCK_LABEL,
                                       default=const.IGNORE_LOCK,
                                       description=strings.ANN_IGNORE_LOCK)
    islands: bpy.props.BoolProperty(name=strings.USE_ISLANDS_LABEL,
                                    default=const.USE_ISLANDS,
                                    description=strings.ANN_USE_ISLANDS)
    maxGroups: bpy.props.IntProperty(name=strings.MAX_GROUPS_LABEL,
                                     default=const.MAX_GROUPS,
                                     min=0,
                                     description=strings.ANN_MAX_GROUPS)
    normalize: bpy.props.BoolProperty(name=strings.NORMALIZE_LABEL,
                                      default=const.NORMALIZE,
                                      description=strings.ANN_NORMALIZE)
    oversampling: bpy.props.IntProperty(name=strings.OVERSAMPLING_LABEL,
                                        default=const.OVERSAMPLING,
                                        min=1,
                                        description=strings.ANN_OVERSAMPLING)
    radius: bpy.props.FloatProperty(name=strings.RADIUS_LABEL,
                                    default=const.RADIUS,
                                    min=0,
                                    description=strings.ANN_RADIUS)
    strength: bpy.props.FloatProperty(name=strings.STRENGTH_LABEL,
                                      default=const.STRENGTH,
                                      min=0.001,
                                      max=1,
                                      description=strings.ANN_STRENGTH)
    select: bpy.props.BoolProperty(default=const.SELECT,
                                   description=strings.ANN_SELECT)
    useSelection: bpy.props.BoolProperty(name=strings.USE_SELECTION_LABEL,
                                         default=const.USE_SELECTION,
                                         description=strings.ANN_USE_SELECTION)
    useSymmetry: bpy.props.BoolProperty(name=strings.USE_SYMMETRY_LABEL,
                                        default=const.USE_SYMMETRY,
                                        description=strings.ANN_USE_SYMMETRY)
    vertexGroups: bpy.props.EnumProperty(name=strings.VERTEX_GROUPS_LABEL,
                                         items=const.VERTEX_GROUPS,
                                         default=1,
                                         description=strings.ANN_VERTEX_GROUPS)
    volume: bpy.props.BoolProperty(name=strings.VOLUME_LABEL,
                                   default=const.VOLUME,
                                   description=strings.ANN_VOLUME)
    volumeRange: bpy.props.FloatProperty(name=strings.VOLUME_RANGE_LABEL,
                                         default=const.VOLUME_RANGE,
                                         min=0,
                                         max=1,
                                         description=strings.ANN_VOLUME_RANGE)


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

def menu_item(self, context):
    """Draw the menu item and it's sub-menu.

    :param context: The current context.
    :type context: bpy.context
    """
    if panel.hasWeights(context):
        if context.object.mode in ['OBJECT', 'WEIGHT_PAINT']:
            self.layout.separator()
            self.layout.operator(SMOOTHWEIGHTS_OT_Paint.bl_idname,
                                 text=strings.MENU_SMOOTH_WEIGHTS)
            self.layout.operator(SMOOTHWEIGHTS_OT_Flood.bl_idname,
                                 text=strings.MENU_FLOOD_SMOOTH)
            self.layout.operator(SMOOTHWEIGHTS_OT_LimitGroups.bl_idname,
                                 text=strings.MENU_LIMIT_GROUPS)
        if context.object.mode in ['EDIT']:
            self.layout.operator(SMOOTHWEIGHTS_OT_LimitGroups.bl_idname,
                                 text=menu.MENU_LIMIT_GROUPS)


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [SmoothWeights_Properties,
           SMOOTHWEIGHTS_OT_Paint,
           SMOOTHWEIGHTS_OT_Flood,
           SMOOTHWEIGHTS_OT_LimitGroups]


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
