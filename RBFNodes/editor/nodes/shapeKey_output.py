# <pep8 compliant>

import bpy

from . import common, node
from ... import var
from ... core import driver
from ... ui import preferences


class RBFShapeKeyOutputNode(node.RBFNode):
    """Driver object source.
    """
    bl_idname = "RBFShapeKeyOutputNode"
    bl_label = "Shape Key"
    bl_icon = 'SHAPEKEY_DATA'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def updateCallback(self, context):
        """Callback for any value changes.

        :param context: The current context.
        :type context: bpy.context
        """
        pass

    def setLabelCallback(self, context):
        """Callback for updating the node label based on the shape key
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.shapeKeyLabelCallback(self)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all shape keys of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.shapeKeyItemsCallback(self, source=True)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    modeItems = [('LIST', "Auto", ""),
                 ('MANUAL', "Manual", "")]
    mode : bpy.props.EnumProperty(items=modeItems)
    shapeName : bpy.props.StringProperty(name="", update=setLabelCallback)
    shapeNameEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    output : bpy.props.FloatProperty(update=updateCallback)
    # The indices of the created drivers on the driven object.
    # There seems to be a bug with the IntVectorProperty, because even
    # though the documentation says that a size of 1 is possible the
    # property fails to register.
    # Therefore, the property is set to a size of two but with a
    # different name. The actual value access is performed through a
    # class property.
    driverIndices : bpy.props.IntVectorProperty(size=2, default=(-1, -1))
    isDriver : bpy.props.BoolProperty(default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addInput("RBFPropertySocket", "Shape Key")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawShapeKeyProperties(self, layout)

        if preferences.getPreferences().developerMode:
            layout.prop(self, "output")

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    @property
    def driverIndex(self):
        return [self.driverIndices[0]]

    @driverIndex.setter
    def driverIndex(self, values):
        self.driverIndices = values

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getProperties(self, obj):
        """Return the name of the selected shape key.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: The selected shape key name and the value as a tuple.
        :rtype: tuple(str, float)
        """
        return common.getShapeKeyProperties(self, obj)

    def getOutputProperties(self):
        """Return the output property.

        :return: A list with the output property and the index as a
                 tuple.
        :rtype: list(bpy.types.Node, int)
        """
        return [(self, -1)]

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def createDriver(self, nodeGroup, driven, rbfNode):
        """Create a driver for the shape key of the driven object.

        :param nodeGroup: The node's node tree of the current RBF setup.
        :type nodeGroup: bpy.types.NodeGroup
        :param driven: The driven object.
        :type driven: bpy.types.Object
        :param rbfNode: The current RBF node.
        :type rbfNode: bpy.types.Node
        """
        # Clear the driver index.
        self.driverIndices[0] = -1
        # Delete any existing driver.
        if rbfNode.active:
            self.deleteDriver(driven)

        props = self.getProperties(driven)
        if props:
            shapeKeyName = driven.data.shape_keys.name
            shapeKey = bpy.data.shape_keys[shapeKeyName]
            dataPath = 'nodes["{}"].output'.format(self.name)
            drivenProp = 'key_blocks["{}"].value'.format(props[0][0][9:])
            driver.createNodeGroupDriver(nodeGroup, shapeKey, dataPath, drivenProp, -1)
            self.driverIndices[0] = driver.getShapeKeyDriverIndex(dataPath)
            self.isDriver = True

    def deleteDriver(self, obj):
        """Delete the driver for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        """
        props = self.getProperties(obj)
        if props:
            shapeKeyName = obj.data.shape_keys.name
            shapeKey = bpy.data.shape_keys[shapeKeyName]
            drivenProp = 'key_blocks["{}"].value'.format(props[0][0])
            result = shapeKey.driver_remove(drivenProp, -1)
            if var.EXPOSE_DATA:
                print("Delete driver: {} {} : {}".format(shapeKey, drivenProp, result))

    def enableDriver(self, driven, enable):
        """Enable or disable the driver FCurves for the given object.

        :param driven: The driven object.
        :type driven: bpy.types.Object
        :param enable: The enabled state of the driver FCurves.
        :type enable: bool
        """
        obj = bpy.data.shape_keys[driven.data.shape_keys.name]
        driver.enableDriver(self, obj, enable)
