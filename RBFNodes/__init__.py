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

Node based RBF Solver.

------------------------------------------------------------------------

Changelog:

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
           "version": (0, 2, 0),
           "blender": (3, 1, 0),
           "category": "Animation",
           "location": "",
           "description": "",
           "warning": "",
           "doc_url": "",
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
