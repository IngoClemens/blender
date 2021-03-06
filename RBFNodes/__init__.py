"""
RBF Nodes
Copyright (C) 2022, Ingo Clemens, brave rabbit, www.braverabbit.com

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

0.4.0 - 2022-07-11
- Improved error messages when the number of storable values gets
  exceeded.
- Added an error label to the RBF node when activating the RBF fails.
- Added a short description to assist extending the number of pose
  values.
- Added a constant to define the number of properties to store the pose
  and weight values for better proceduralism.
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
           "version": (0, 4, 0),
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

    bpy.app.handlers.frame_change_pre.append(handler.refresh)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.append(handler.refresh)


def unregister():
    """Unregister the add-on.
    """
    editor.unregister()
    ui.unregister()

    bpy.app.handlers.frame_change_pre.remove(handler.refresh)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.remove(handler.refresh)


if __name__ == "__main__":
    register()
