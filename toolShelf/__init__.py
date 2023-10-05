"""
toolShelf
Copyright (C) 2021-2023, Ingo Clemens, brave rabbit, www.braverabbit.com

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

Tool Shelf provides a panel to create any number of grouped buttons to
execute custom code and scripts to optimize workflow.
The commands for each button can be either typed in directly or by
retrieving it from the text editor. This works with a complete text
document or any selection.
Groups and buttons can be edited afterwards, as well as having their
order changed.
Button commands can be extracted at any time by copying them to the text
editor.

------------------------------------------------------------------------
"""

from . import preferences, toolShelf


bl_info = {"name": "Tool Shelf",
           "author": "Ingo Clemens, braverabbit.com",
           "version": (0, 14, 1),
           "blender": (2, 92, 0),
           "category": "Interface",
           "location": "View3D",
           "description": "Save scripts as buttons and organize them in groups for easy access",
           "warning": "",
           "doc_url": "https://www.braverabbit.com/toolShelf",
           "tracker_url": ""}


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

def register():
    """Register the add-on.
    """
    preferences.register()
    toolShelf.register()


def unregister():
    """Unregister the add-on.
    """
    preferences.unregister()
    toolShelf.unregister()


if __name__ == "__main__":
    register()
