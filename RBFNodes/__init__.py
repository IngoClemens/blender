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
"""

import bpy

from . import preferences, editor, ui
from . core import handler, utils


bl_info = {"name": "RBF Nodes",
           "author": "Ingo Clemens",
           "version": (1, 2, 1),
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
    preferences.register()
    editor.register()
    ui.register()

    utils.VERSION = bl_info["version"]

    bpy.app.handlers.frame_change_post.append(handler.refresh)
    bpy.app.handlers.load_post.append(handler.verifyVersion)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.append(handler.refresh)


def unregister():
    """Unregister the add-on.
    """
    preferences.unregister()
    editor.unregister()
    ui.unregister()

    bpy.app.handlers.frame_change_post.remove(handler.refresh)
    bpy.app.handlers.load_post.remove(handler.verifyVersion)
    if not bpy.app.background:
        bpy.app.handlers.depsgraph_update_post.remove(handler.refresh)


if __name__ == "__main__":
    register()
