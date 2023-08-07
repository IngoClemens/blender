"""
RBF Nodes
Copyright (C) 2022-2023, Ingo Clemens, brave rabbit, www.braverabbit.com

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

Node-based RBF solver for driving multiple properties with multiple
driver values.

------------------------------------------------------------------------

Changelog:

1.0.3 - 2023-08-07
      - Fixed that shading nodes cannot be linked due to python changes
        in Blender 3.6.

1.0.2 - 2023-07-03
      - Fixed an error related to the driver or driven object missing a
        material assignment when linking an input or output node.
      - Fixed that geometry nodes with a geometry socket don't get their
        value plugs listed.

1.0.1 - 2023-06-09
      - Fixed wrong unregistering of the PointerProperty.

1.0.0 - 2023-06-08
      - Because of some necessary changes new RBF setups are not
        compatible with older versions of the add-on. A message appears
        when loading a scene which contains an older setup and the side
        panel of the RBF editor also displays a message.
        The setup is updated when the RBF solver gets reset.
      - When adding a new pose with additional shape keys default values
        are added to existing poses. This works for shape keys only
        because a value of zero can be assumed for all other poses. It
        does not work with other properties.
      - Updated node names to differentiate between inputs and outputs.
      - Activating the RBF sets all input and output nodes to
        non-editable to prevent changes during the active state.
      - Improved the interpolation when using quaternion-based rotation.
      - Improved error message when a decomposition error occurs.
      - Added a search and replace option in the developer section to
        edit driver and driven data for poses.
      - Removed quaternion based rotation sub-types.
      - Fixed that the quaternion output rotation properties are
        depending on the selected euler axes.
      - Fixed that shape key drivers remain when resetting the RBF.
      - Fixed that the individual shape-key block name of a duplicated
        mesh isn't respected when activating the RBF.
      - Fixed that the RBF calculation is using driver values with an
        offset of one frame when used in an animation.

0.4.0 - 2022-07-11
      - Improved error messages when the number of storable values gets
        exceeded.
      - Added an error label to the RBF node when activating the RBF
        fails.
      - Added a short description to assist extending the number of pose
        values.
      - Added a constant to define the number of properties to store the
        pose and weight values for better proceduralism.
      - Fixed: A pose cannot be edited after the RBF has been reset.

0.3.0 - 2022-07-06
      - Various changes and improvements.
      - Added support for object properties and modifiers.
      - Added radius presets.

0.2.0 - 2022-05-26
      - Merged all individual property sockets into one.

0.1.0 - 2022-03-24

------------------------------------------------------------------------
"""

import bpy

from . import editor, ui
from . core import handler


bl_info = {"name": "RBF Nodes",
           "author": "Ingo Clemens",
           "version": (1, 0, 3),
           "blender": (3, 1, 0),
           "category": "Animation",
           "location": "Editors > RBF Nodes Editor",
           "description": "Node-based RBF solver for driving properties",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/RBF-Nodes",
           "tracker_url": ""}


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

def register():
    """Register the add-on.
    """
    editor.register()
    ui.register()

    bpy.app.handlers.frame_change_post.append(handler.refresh)
    bpy.app.handlers.load_post.append(handler.verifyVersion)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.append(handler.refresh)


def unregister():
    """Unregister the add-on.
    """
    editor.unregister()
    ui.unregister()

    bpy.app.handlers.frame_change_post.remove(handler.refresh)
    bpy.app.handlers.load_post.remove(handler.verifyVersion)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.remove(handler.refresh)


if __name__ == "__main__":
    register()
