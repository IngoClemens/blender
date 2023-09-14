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
"""

from . import preferences, smoothWeights, symmetryMap


bl_info = {"name": "Smooth Weights",
           "author": "Ingo Clemens, braverabbit.com",
           "version": (2, 3, 0),
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
    preferences.register()
    smoothWeights.register()
    symmetryMap.register()


def unregister():
    """Unregister the add-on.
    """
    preferences.unregister()
    smoothWeights.unregister()
    symmetryMap.unregister()


if __name__ == "__main__":
    register()
