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
O: Oversampling
   Hold O while pressing + or - to increase or decrease the oversampling
   value.
V: Volume (off for surface smoothing)
R: Volume Range
   Hold R while dragging the cursor left/right to adjust the range.
   Hold Shift for faster adjustment and Ctrl for slower.
   Make sure to hover over the mesh.
M: Limit Max Groups
G: Groups
   Hold G while pressing + or - to increase or decrease the number of
   vertex groups.
T: Use Symmetry
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

------------------------------------------------------------------------

Changelog:

2.1.0 - 2023-09-08
      - Added the Mirror Weights operator to the Smooth Weights panel.
      - Added icons for all tool buttons.
      - Fixed that mapping takes long if too many elements are selected.
        The selection is now limited to two edges maximum.
      - Fixed that mapping fails with simple objects if one of the faces
        has a zero index.
      - Fixed that Add Partial doesn't find center vertices if these are
        slightly on the negative side.

2.0.0 - 2023-09-07
      - Added symmetry mapping.
      - Added a symmetry option to the smooth operators to use the new
        symmetry map for mirrored smoothing.
      - Added a new operator to clamp the maximum number of vertex
        groups.
      - Added a new operator to mirror vertex weights based on the
        symmetry map.

1.2.0 - 2023-08-28
      - Added an oversampling property for smoothing in multiple
        iterations for a smoother result.
      - Added an additional color preference to control the color of the
        brush circle and the tool info separately.
      - Increased the drawing precision of the brush circle.
      - Fixed that the flood operator would not respect the current
        vertex selection.

1.1.0 - 2023-08-25
      - Disabling Use Selection also disables selection/deselection
        mode.
      - When exiting while in Blender's Weight Paint mode the mode is
        kept.
      - Fixed that undo is very slow with a large number of affected
        vertices.
      - The user defined color for unselected vertices is not used when
        entering the tool.

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

from . import smoothWeights, symmetryMap


bl_info = {"name": "Smooth Weights",
           "author": "Ingo Clemens",
           "version": (2, 1, 0),
           "blender": (3, 6, 0),
           "category": "Rigging",
           "location": "View3D > Object",
           "description": "Smooth mesh weights by averaging neighbouring weights",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/Smooth-Weights",
           "tracker_url": ""}


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

def register():
    """Register the add-on.
    """
    smoothWeights.register()
    symmetryMap.register()


def unregister():
    """Unregister the add-on.
    """
    smoothWeights.unregister()
    symmetryMap.unregister()


if __name__ == "__main__":
    register()
