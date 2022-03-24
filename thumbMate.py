"""
thumbMate
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

Thumb Mate helps with creating customizable thumbnail previews for
object assets in the asset browser.
By default these asset previews are only rendered using the workbench
render engine and therefore are often insufficient for representing the
object due to it's limitations.
Thumb Mate renders the asset preview using Eevee with full control over
the used environment and viewing angle. The previews can either be
created upon marking an object as an asset or when updating the image.

------------------------------------------------------------------------

Usage:

Thumb Mate is accessible through the Render menu item in the Asset
Browser's main menu:
Render Custom Preview: Creates a rendered preview for all selected mesh
                       objects in the scene. If nothing is selected all
                       objects of the currently active collection will
                       be rendered.
                       All rendered objects will automatically be marked
                       as assets.
Update Custom Preview: Re-renders the preview image for the currently
                       selected asset.

Additionally the metadata panel of the asset browser features a new
button in the preview folder which allows for updating the custom
preview for the selected asset.

All settings responsible for the rendering of the previews can be found
in the add-on preferences in the Blender preferences window.
By default the city.exr of the built-in environment images of Blender is
used for the background, but any custom image can be used as well.
Other settings include the camera angle, focus length, clipping and
frame padding.

------------------------------------------------------------------------

Changelog:

0.1.0 - 2022-03-24
      - First public release

------------------------------------------------------------------------
"""

bl_info = {"name": "Thumb Mate",
           "author": "Ingo Clemens",
           "version": (0, 1, 0),
           "blender": (3, 0, 0),
           "category": "Import-Export",
           "location": "Asset Browser",
           "description": "Create rendered beauty previews for the asset browser",
           "warning": "",
           "doc_url": "https://github.com/IngoClemens/blender/wiki/Thumb-Mate",
           "tracker_url": ""}

import bpy
from bpy_extras.asset_utils import AssetMetaDataPanel, SpaceAssetInfo
from bl_operators.assets import AssetBrowserMetadataOperator
import bl_ui

import inspect
import os
import math
from mathutils import Euler, Vector
import shutil
import types


# ----------------------------------------------------------------------
# Defaults
# ----------------------------------------------------------------------

NAME = "thumbMate"
IMAGE_NAME = "{}_render".format(NAME)
IMAGE_SIZE = 256
CAM_NAME = "camera_{}".format(NAME)
CAM_ANGLE = (60, 0, 25)
CLIP_START = 0.001
CLIP_END = 1000
FOCAL_LENGTH = 85
WORLD_NAME = "world_{}".format(NAME)
HDRI = "city.exr"
ROTATION = 0
PADDING = 5


ANN_RENDER_OPERATOR = "Render custom preview for the selected objects or active collection"
ANN_UPDATE_OPERATOR = "Create a custom preview for the selected data-block"
ANN_PATH = ("The path containing HDRI images to be used for the rendering environment.\n"
            "The default is the built-in world images path.")
ANN_IMAGE = "The image used for the rendering environment"
ANN_CAM_ANGLE = "The viewing angle of the camera. Tilt, Roll and Orientation"
ANN_FOCAL = ("The focal length for rendering the previews.\n"
             "The effective focal length is slightly reduced to allow for border padding\n"
             "and depends on the frame padding value.")
ANN_CLIP_START = ("The min clip distance for the camera.\n"
                  "Should be small enough to not cut-off smaller objects.")
ANN_CLIP_END = "The max clip distance for the camera"
ANN_WORLD_ROTATION = "The orientation of the environment image"
ANN_PADDING = ("The frame padding in percent to allow some space between the images.\n"
               "Effectively reduces the camera focal length.")


# ----------------------------------------------------------------------
# Storage
# ----------------------------------------------------------------------

class Cache(object):
    """Class for storing the scene state in order to be able to revert
    it back after rendering.
    """
    def __init__(self):
        self.values = {}


cache = Cache()


# ----------------------------------------------------------------------
# General
# ----------------------------------------------------------------------

def currentSelection():
    """Return the current object selection. If nothing is selected
    return all mesh objects from the current collection.

    :return: A list with selected objects or collection objects.
    :rtype: list(bpy.types.Object) or None
    """
    sel = bpy.context.selected_objects
    if sel:
        return sel
    else:
        col = bpy.context.view_layer.active_layer_collection
        if col:
            # If the selected collection is the master scene collection
            # it cannot be queried directly since it's of type
            # LayerCollection.
            # In this case get the wrapped collection which then can
            # be queried just like any other collection.
            if type(col) is bpy.types.LayerCollection:
                col = col.collection
            # Filter only mesh objects.
            return [o for o in col.all_objects if o.type == 'MESH']


def environmentImagesPath():
    """Return the built-in images path for studio light world HDRIs.

    Since this path depends on the current system it's procedurally
    retrieved through the location of the application binary file.

    :return: The absolute path to the included world HDRIs.
    :rtype: str or None
    """
    # A recursion counter to make sure that the loop ends.
    count = 0
    # Get the path to the Blender executable.
    filePath = os.path.dirname(bpy.app.binary_path)
    # Find the lowest path level which contains Blender.
    while "blender" not in os.path.basename(filePath).lower():
        filePath = os.path.dirname(filePath)
        if not filePath or count == 20:
            break
        count += 1

    # Search all subpaths for the datafiles folder. Based on this folder
    # the path can be completed.
    for dirPath, dirs, fileList in os.walk(filePath):
        if os.path.basename(dirPath) == "datafiles":
            return os.path.join(os.path.join(dirPath, "studiolights"), "world")


def environmentImages(dirPath):
    """Return a list of images which are located at the given path.

    :param dirPath: The file path to search for images.
    :type dirPath: str

    :return: The list of images at the given path.
    :rtype: list(str)
    """
    images = []
    for f in os.listdir(dirPath):
        if os.path.isfile(os.path.join(dirPath, f)):
            name, ext = os.path.splitext(f)
            if ext.lower().replace(".", "") in ["hdr", "exr", "rad", "tif", "tiff"]:
                images.append(f)
    return sorted(images)


def setRenderable(objects, hidden=True):
    """Set all given objects to be invisible when rendering.

    :param objects: The list of objects to process.
    :type objects: list(bpy.types.Object)
    :param hidden: The hidden state for rendering.
    :type hidden: bool

    :return: A list of tuples with the object and the previous
             visibility setting.
    :rtype: list(tuple(bpy.types.Object, bool))
    """
    state = []
    for obj in objects:
        state.append((obj, obj.hide_render))
        obj.hide_render = hidden
    return state


def resetRenderable(objects):
    """Set the rendering visibility for each object based on their given
    state.

    :param objects: A list of tuples with the object and the visibility
                    setting.
    :rtype: list(tuple(bpy.types.Object, bool))
    """
    for obj, state in objects:
        obj.hide_render = state


# ----------------------------------------------------------------------
# Render settings
# ----------------------------------------------------------------------

def outputPath():
    """Return the output path based on the current scene path.

    :return: The absolute render output path.
    :rtype: str
    """
    scenePath = bpy.data.filepath
    # If the scene hasn't been saved yet the path is empty.
    # Returning an empty path promps the user for saving the scene.
    if not scenePath:
        return
    renderPath = os.path.join(os.path.dirname(scenePath), "{}_thumbs".format(NAME))
    return renderPath


def deleteOutputPath(filePath):
    """Delete the given directory and all of it's content.

    :param filePath: The path to the directory to delete.
    :type filePath: str
    """
    if os.path.exists(filePath):
        shutil.rmtree(filePath)


def setRenderSettings(filePath):
    """Store the previous render settings and define the settings for
    rendering the previews.

    :param filePath: The path to render the images to.
    :type filePath: str
    """
    cache.values["engine"] = bpy.context.scene.render.engine
    cache.values["transparent"] = bpy.context.scene.render.film_transparent

    cache.values["filepath"] = bpy.context.scene.render.filepath
    cache.values["format"] = bpy.context.scene.render.image_settings.file_format
    cache.values["mode"] = bpy.context.scene.render.image_settings.color_mode
    cache.values["depth"] = bpy.context.scene.render.image_settings.color_depth

    cache.values["resolutionX"] = bpy.context.scene.render.resolution_x
    cache.values["resolutionY"] = bpy.context.scene.render.resolution_y
    cache.values["percentage"] = bpy.context.scene.render.resolution_percentage
    cache.values["aspectX"] = bpy.context.scene.render.pixel_aspect_x
    cache.values["aspectY"] = bpy.context.scene.render.pixel_aspect_y

    # Define the necessary render settings.
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    bpy.context.scene.render.film_transparent = True

    bpy.context.scene.render.filepath = filePath
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.color_depth = '8'

    bpy.context.scene.render.resolution_x = IMAGE_SIZE
    bpy.context.scene.render.resolution_y = IMAGE_SIZE
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.pixel_aspect_x = 1.0
    bpy.context.scene.render.pixel_aspect_y = 1.0

    # Store the current world.
    cache.values["world"] = bpy.context.scene.world


def restoreRenderSettings():
    """Restore the previous render settings
    """
    bpy.context.scene.render.engine = cache.values["engine"]
    bpy.context.scene.render.film_transparent = cache.values["transparent"]

    bpy.context.scene.render.filepath = cache.values["filepath"]
    bpy.context.scene.render.image_settings.file_format = cache.values["format"]
    bpy.context.scene.render.image_settings.color_mode = cache.values["mode"]
    bpy.context.scene.render.image_settings.color_depth = cache.values["depth"]

    bpy.context.scene.render.resolution_x = cache.values["resolutionX"]
    bpy.context.scene.render.resolution_y = cache.values["resolutionY"]
    bpy.context.scene.render.resolution_percentage = cache.values["percentage"]
    bpy.context.scene.render.pixel_aspect_x = cache.values["aspectX"]
    bpy.context.scene.render.pixel_aspect_y = cache.values["aspectY"]

    if cache.values["world"]:
        bpy.context.scene.world = cache.values["world"]


# ----------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------

def get3dView():
    """Return the SpaceView3D to be able to access the current viewing
    camera.

    :return: The current view space.
    :rtype: bpy.types.SpaceView3D or None
    """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            return bpy.types.SpaceView3D(area.spaces[0])


def createCamera():
    """Create the camera for rendering the preview images.
    """
    prefs = getPreferences()

    # Remove any pre-existing preview camera.
    if CAM_NAME in bpy.data.cameras:
        bpy.data.cameras.remove(bpy.data.cameras[CAM_NAME], do_unlink=True)

    # Store the current scene camera.
    cache.values["sceneCamera"] = bpy.context.scene.camera

    # Create a new camera and name it accordingly.
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = CAM_NAME
    cam.data.name = CAM_NAME
    cache.values["camera"] = cam

    # Set the camera properties.
    cam.location = Vector((10, -10, 10))
    rot = prefs.camAngle_value
    cam.rotation_euler = Euler((math.radians(rot[0]),
                                math.radians(rot[1]),
                                math.radians(rot[2])))
    cam.data.clip_start = prefs.clipStart_value
    cam.data.clip_end = prefs.clipEnd_value
    cam.data.lens = prefs.focal_value

    view3d = get3dView()
    # Store the current view camera, if any.
    cache.values["viewCamera"] = view3d.camera if view3d.camera else None
    # Set the render camera for the view.
    view3d.camera = cam


def cleanupCamera():
    """Set the camera settings back to the previous state.
    """
    # Delete the preview camera.
    bpy.data.cameras.remove(cache.values["camera"].data, do_unlink=True)
    # Reset the scene camera.
    if cache.values["sceneCamera"]:
        bpy.context.scene.camera = cache.values["sceneCamera"]
    # Reset the view camera.
    view3d = get3dView()
    try:
        if cache.values["viewCamera"]:
            view3d.camera = cache.values["viewCamera"]
    except ReferenceError:
        pass


# ----------------------------------------------------------------------
# World node
# ----------------------------------------------------------------------

def createWorld(filePath):
    """Create a new world node.
    """
    prefs = getPreferences()

    # Remove any previously created data.
    cleanupWorld()

    # Create a new world and make it current.
    world = bpy.data.worlds.new(WORLD_NAME)
    bpy.context.scene.world = world
    world.use_nodes= True

    # Create the necessary shading nodes for the environment map.
    coord = world.node_tree.nodes.new(type="ShaderNodeTexCoord")
    mapping = world.node_tree.nodes.new(type="ShaderNodeMapping")
    texture = world.node_tree.nodes.new(type="ShaderNodeTexEnvironment")

    coord.location = (-740, 300)
    mapping.location = (-520, 300)
    texture.location = (-300, 300)

    world.node_tree.links.new(coord.outputs['Generated'], mapping.inputs[0])
    world.node_tree.links.new(mapping.outputs[0], texture.inputs[0])
    world.node_tree.links.new(texture.outputs[0], world.node_tree.nodes["Background"].inputs[0])

    # Create the image for the environment and link it to the texture
    # node.
    image = bpy.data.images.load(os.path.join(filePath, prefs.image_value), check_existing=True)
    cache.values["environmentImage"] = image
    texture.image = image

    # Adjust the horizontal rotation.
    mapping.inputs[2].default_value[2] = math.radians(prefs.worldRotation_value)


def cleanupWorld():
    """Delete all created data blocks for the world and reset to the
    previous world.
    """
    prefs = getPreferences()

    if WORLD_NAME in bpy.data.worlds:
        bpy.data.worlds.remove(bpy.data.worlds[WORLD_NAME], do_unlink=True)

    if prefs.image_value in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[prefs.image_value], do_unlink=True)


# ----------------------------------------------------------------------
# Thumbnail creation
# ----------------------------------------------------------------------

def renderPreviews(objects, imagePath):
    """Create the preview images for the given objects.

    :param objects: The list of objects to create previews for.
    :type objects: list(bpy.types.Object)
    :param imagePath: The render output path.
    :type imagePath: str

    :return: None or an error message
    :rtype: None or tuple(dict(), str)
    """
    prefs = getPreferences()

    paddingFactor = 1 - (prefs.padding_value * 0.01)

    if objects:
        # Set all objects to be invisible for rendering and store their
        # previous state.
        renderState = setRenderable(bpy.data.objects, hidden=True)

        for obj in objects:
            # Select the current object that the camera can focus on it.
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            # Set the object to be renderable.
            obj.hide_render = False

            # Frame the selection and adjust the focal length to allow
            # for a safe framing area.
            bpy.ops.view3d.camera_to_view_selected()
            cache.values["camera"].data.lens = prefs.focal_value * paddingFactor

            # Render the preview.
            bpy.ops.render.render(write_still=True)

            # Rename the output file to match the object's name.
            tempFile = ".".join((os.path.join(imagePath, IMAGE_NAME), "png"))
            thumbFile = ".".join((os.path.join(imagePath, obj.name), "png"))
            os.rename(tempFile, thumbFile)

            # Reset the focal length of the camera.
            cache.values["camera"].data.lens = prefs.focal_value

            # Deselect the object and hide it from rendering.
            obj.select_set(False)
            obj.hide_render = True

        # Reset the previous render state for all objects.
        resetRenderable(renderState)

        # Mark the selected objects as assets and assign their custom
        # preview image.
        # Usually copying the context shouldn't cause an error but just
        # for safety an error gets intercepted.
        try:
            override = bpy.context.copy()
        except TypeError:
            return ({'ERROR'}, "An error occurred while trying to access the context for loading the custom preview")

        for obj in objects:
            if not obj.asset_data:
                obj.asset_mark()

            override['id'] = obj
            thumbFile = ".".join((os.path.join(imagePath, obj.name), "png"))
            bpy.ops.ed.lib_id_load_custom_preview(override, filepath=thumbFile)


def setupRender():
    """Prepare the scene for rendering the preview images.

    Return the render output path if the setup was successful.
    Return None, if the build-in images could not be found.

    :return: The output path or a warning message.
    :rtype: str or tuple(dict(), str)
    """
    prefs = getPreferences()

    # Check of the built-in environment maps path can be located.
    # Discontinue if it cannot be found.
    envPath = prefs.path_value
    if not envPath:
        return ({'WARNING'}, "No environment images path defined")

    # Discontinue if there is no output path defined.
    renderPath = outputPath()
    if not renderPath:
        return ({'WARNING'}, "The scene needs to be saved before rendering")

    if prefs.image_value == 'NONE':
        return ({'WARNING'}, "No environment image defined")

    setRenderSettings(os.path.join(renderPath, IMAGE_NAME))
    createCamera()
    createWorld(envPath)
    return renderPath


def cleanup(filePath):
    """Restore all previous settings and delete all data blocks used for
    rendering the preview images.

    :param filePath: The path to render the images to.
    :type filePath: str
    """
    restoreRenderSettings()
    cleanupCamera()
    cleanupWorld()
    deleteOutputPath(filePath)


def createAssetPreview(objects):
    """Create asset preview images for the current selection or the
    currently active collection.

    :param objects: The object or list of objects to process.
    :type objects: list(bpy.types.Object)
    """
    if not type(objects) is list:
        objects = [objects]

    bpy.ops.object.select_all(action='DESELECT')
    if objects:
        # Return if there is no 3d view available.
        if not get3dView():
            return ({'WARNING'}, "No 3d view found")

        result = setupRender()
        # If the resulting path contains an error no rendering is
        # performed.
        # Cleanup is not necessary in this case.
        if type(result) is tuple:
            return result

        renderError = renderPreviews(objects, result)
        cleanup(result)

        if renderError:
            return renderError

        # Restore the selection.
        for obj in objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj


# ----------------------------------------------------------------------
# Operators
# ----------------------------------------------------------------------

class THUMBMATE_OT_renderPreview(bpy.types.Operator):
    """Operator class for rendering custom preview images for either
    the currently selected objects or all meshes of the active
    collection.
    """
    bl_idname = "thumbmate.render_preview"
    bl_label = "Render asset preview"
    bl_description = ANN_RENDER_OPERATOR
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Execute the operator.

        :param context: The current context.
        :type context: bpy.context
        """
        objects = currentSelection()
        result = createAssetPreview(objects)
        if result:
            self.report(result[0], result[1])
            return {'CANCELLED'}

        return {'FINISHED'}


class THUMBMATE_OT_updatePreview(AssetBrowserMetadataOperator, bpy.types.Operator):
    """Operator class for rendering a custom preview image for the
    currently selected asset.
    """
    bl_idname = "thumbmate.update_preview"
    bl_label = "Update asset preview"
    bl_description = ANN_UPDATE_OPERATOR
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_asset = SpaceAssetInfo.get_active_asset(context)
        # Only render the image if the asset is a mesh.
        if active_asset.id_data.type == 'MESH':
            result = createAssetPreview(active_asset.id_data)
            if result:
                self.report(result[0], result[1])
                return {'CANCELLED'}

        return {'FINISHED'}


# ----------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------

class THUMBMATE_MT_menu(bpy.types.Menu):
    bl_idname = "THUMBMATE_MT_menu"
    bl_label = "Render"

    def draw(self, context):
        self.layout.operator(THUMBMATE_OT_renderPreview.bl_idname,
                             text="Render Selected Objects",
                             icon="RENDER_RESULT")
        self.layout.operator(THUMBMATE_OT_updatePreview.bl_idname,
                             text="Update Selected Asset",
                             icon="RENDER_STILL")


def menu_item(self, context):
    """Draw the menu.

    :param context: The current context.
    :type context: bpy.context
    """
    self.layout.menu(THUMBMATE_MT_menu.bl_idname)


# ----------------------------------------------------------------------
# Customize the data panel
# ----------------------------------------------------------------------

def metadataPanelOverride(restore=False):
    """Create a new class as an override to
    ASSETBROWSER_PT_metadata_preview from space_filebrowser.py.
    The override is necessary in order to be able to add a new button
    below the existing since these are in a separate layout.
    Simply appending a new button would position it below the preview
    image, which is not intended.

    :return: The class instance for registering with the add-on.
    :rtype: class instance
    """
    # Get the content from the original class as a string.
    data = inspect.getsource(bl_ui.space_filebrowser.ASSETBROWSER_PT_metadata_preview)
    lines = data.split("\n")

    # Add new lines for the override.
    # Skip, if the original class should get restored.
    if not restore:
        # Add the new lines for adding the button.
        lines.append("        col.separator()")
        lines.append("        col.operator('{}',\n"
                     "                     text='',\n"
                     "                     icon='RENDER_STILL')".format(THUMBMATE_OT_updatePreview.bl_idname))

    # Get the class name from the first line which is needed for
    # registering the override.
    className = lines[0].split("(")[0].replace("class ", "")
    # Get the content for bl_label from the second line.
    label = lines[1].split(" = ")[1].replace("\"", "")
    # Remove the class line.
    lines.pop(0)
    # Remove the bl_label line.
    lines.pop(0)
    # Remove the empty line.
    lines.pop(0)
    # Overwrite the draw method because the original contains tabs at
    # the beginning.
    lines[0] = "def draw(self, context):"
    # print("\n".join(lines))

    # Register the method within the scope of the add-on.
    module = types.ModuleType("operatorDraw")
    exec("\n".join(lines), module.__dict__)

    # Create the class.
    panelClass = type(className,
                      (AssetMetaDataPanel, bpy.types.Panel, ),
                      {"bl_label": label,
                       "draw": module.draw})

    return panelClass


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


def imageItems(self, context):
    """Callback for populating the enum property with the HDRI names
    based on the current world images path.

    :param context: The current context.
    :type context: bpy.context
    """
    prefs = getPreferences()

    images = [('NONE', "––– Select –––", "")]
    if prefs.path_value:
        for img in environmentImages(prefs.path_value):
            images.append((img, img, ""))

    return images


class THUMBMATEPreferences(bpy.types.AddonPreferences):
    """Create the layout for the preferences.
    """
    bl_idname = NAME

    path_value: bpy.props.StringProperty(name="World Images",
                                         description=ANN_PATH,
                                         default=environmentImagesPath(),
                                         subtype='DIR_PATH',
                                         update=imageItems)
    image_value: bpy.props.EnumProperty(name="HDRI",
                                        description=ANN_IMAGE,
                                        items=imageItems,
                                        default=1)
    camAngle_value: bpy.props.FloatVectorProperty(name="Camera Rotation",
                                                  description=ANN_CAM_ANGLE,
                                                  default=CAM_ANGLE)
    focal_value: bpy.props.FloatProperty(name="Camera Focal Length",
                                         description=ANN_FOCAL,
                                         default=FOCAL_LENGTH)
    clipStart_value: bpy.props.FloatProperty(name="Clip Min",
                                             description=ANN_CLIP_START,
                                             default=CLIP_START,
                                             precision=3)
    clipEnd_value: bpy.props.FloatProperty(name="Clip Max",
                                           description=ANN_CLIP_END,
                                           default=CLIP_END)
    worldRotation_value: bpy.props.FloatProperty(name="World Rotation",
                                                 description=ANN_WORLD_ROTATION,
                                                 default=ROTATION)
    padding_value: bpy.props.IntProperty(name="Edge Padding %",
                                         description=ANN_PADDING,
                                         default=PADDING)

    def draw(self, context):
        """Draw the panel and it's properties.

        :param context: The current context.
        :type context: bpy.context
        """
        self.layout.use_property_split = True

        col = self.layout.column(align=True)
        col.prop(self, "path_value")
        col.prop(self, "image_value")

        col.separator()
        row = col.row(align=True)
        row.prop(self, "camAngle_value")

        col = self.layout.column(align=True)
        col.prop(self, "focal_value")
        col.prop(self, "clipStart_value")
        col.prop(self, "clipEnd_value")

        col.separator()
        col.prop(self, "worldRotation_value")

        col.separator()
        col.prop(self, "padding_value")


# ----------------------------------------------------------------------
# Registration
# ----------------------------------------------------------------------

# Collect all classes in a list for easier access.
classes = [THUMBMATE_OT_renderPreview,
           THUMBMATE_OT_updatePreview,
           THUMBMATE_MT_menu,
           metadataPanelOverride(),
           THUMBMATEPreferences]


def register():
    """Register the add-on.
    """
    for cls in classes:
        bpy.utils.register_class(cls)

    # Add the menu items.
    bpy.types.ASSETBROWSER_MT_editor_menus.append(menu_item)


def unregister():
    """Unregister the add-on.
    """
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Restore the original metadata class.
    bpy.utils.register_class(metadataPanelOverride(restore=True))

    # Remove the menu items.
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(menu_item)


if __name__ == "__main__":
    register()
