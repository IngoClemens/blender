"""
placeReflection
Copyright (C) 2021, Ingo Clemens, brave rabbit, www.braverabbit.com

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

bl_info = {"name": "Place Reflection",
           "author": "Ingo Clemens",
           "version": (0, 3, 0),
           "blender": (2, 92, 0),
           "category": "Lighting",
           "location": "View3D > Object",
           "description": "Place lights and reflected objects by dragging over a target surface",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/Place-Reflection",
           "tracker_url": ""}

import bpy

import os

from . import placeReflection as pr


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

class PlaceReflection_MT_MenuItem(bpy.types.Menu):
    """Class for creating a menu item with sub-menu items.
    """
    # An all uppercase prefix is required for the idname.
    bl_idname = "PLACEREFLECTION_MT_menuItem"
    bl_label = "Place Reflection"

    def draw(self, context):
        """Draw the menu.

        :param context: The current context.
        :type context: bpy.context
        """
        # Get the icon from the preview collection.
        prevColl = preview_collections["main"]
        icon = prevColl["placeReflection_icon"]

        layout = self.layout
        # Main menu item.
        layout.label(text="Place Reflection")
        # Sub-menu items.
        layout.operator(pr.OBJECT_OT_PlaceReflection.bl_idname,
                        text="Place Reflection",
                        icon_value=icon.icon_id)
        layout.operator(pr.OBJECT_OT_PlaceReflection_options.bl_idname,
                        text="Toggle Tool Panel")


def draw_menu(self, context):
    """Draw the menu item and it's sub-menu.

    :param context: The current context.
    :type context: bpy.context
    """
    # Get the icon from the preview collection.
    prevColl = preview_collections["main"]
    icon = prevColl["placeReflection_icon"]

    self.layout.menu(PlaceReflection_MT_MenuItem.bl_idname,
                     icon_value=icon.icon_id)


# Top level menu items.
'''
def menu_item(self, context):
    """Create the menu item.

    :param context: The current context.
    :type context: bpy.context
    """
    # Get the icon from the preview collection.
    prevColl = preview_collections["main"]
    icon = prevColl["placeReflection_icon"]

    self.layout.operator(OBJECT_OT_PlaceReflection.bl_idname,
                         text="Place Reflection",
                         icon_value=icon.icon_id)
    self.layout.operator(OBJECT_OT_PlaceReflection_options.bl_idname,
                         text="Place Reflection Panel")
'''

# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Main dictionary for storing the menu icons.
preview_collections = {}

# Collect all classes in a list for easier access.
classes = [pr.PlaceReflection_properties,
           pr.OBJECT_OT_PlaceReflection,
           pr.VIEW3D_PT_PlaceReflection,
           pr.OBJECT_OT_PlaceReflection_options,
           PlaceReflection_MT_MenuItem]


def register():
    """Register the add-on.
    """
    # Setup the preview collection for giving access to the icon.
    import bpy.utils.previews
    prevColl = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    prevColl.load("placeReflection_icon", os.path.join(icons_dir, "placeReflection.png"), 'IMAGE')
    preview_collections["main"] = prevColl

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.place_reflection = bpy.props.PointerProperty(type=pr.PlaceReflection_properties)
    # Add only top level menu items.
    # bpy.types.VIEW3D_MT_object.append(menu_item)
    bpy.types.VIEW3D_MT_object.append(draw_menu)


def unregister():
    """Unregister the add-on.
    """
    # Remove the preview collection.
    for prevColl in preview_collections.values():
        bpy.utils.previews.remove(prevColl)
    preview_collections.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.place_reflection
    # Remove only top level menu items.
    # bpy.types.VIEW3D_MT_object.remove(menu_item)
    bpy.types.VIEW3D_MT_object.remove(draw_menu)


if __name__ == "__main__":
    register()
