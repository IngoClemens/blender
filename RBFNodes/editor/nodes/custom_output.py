# <pep8 compliant>

import bpy

from . import common, node
from ... import dev
from ... core import driver
from ... ui import preferences


class RBFCustomOutputNode(node.RBFNode):
    """Custom property output node.
    """
    bl_idname = "RBFCustomOutputNode"
    bl_label = "Custom Output"
    bl_icon = 'EMPTY_SINGLE_ARROW'

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
        """Callback for updating the node label based on the property
        selection.

        :param context: The current context.
        :type context: bpy.context
        """
        common.customLabelCallback(self)

    def propItems(self, context):
        """Callback for the property drop down menu to collect the names
        of all custom properties of the connected object.

        :param context: The current context.
        :type context: bpy.context

        :return: A list with tuple items for the enum property.
        :rtype: list(tuple(str))
        """
        return common.customItemsCallback(self, source=True)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    modeItems = [('LIST', "Auto", ""),
                 ('MANUAL', "Manual", "")]
    mode : bpy.props.EnumProperty(items=modeItems)
    propertyName : bpy.props.StringProperty(name="", update=setLabelCallback)
    propertyEnum : bpy.props.EnumProperty(name="", items=propItems, update=setLabelCallback)

    output : bpy.props.FloatVectorProperty(update=updateCallback)
    # The indices of the created drivers on the driven object.
    driverIndex : bpy.props.IntVectorProperty(default=(-1, -1, -1))
    isDriver : bpy.props.BoolProperty(default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addInput("RBFPropertySocket", "Custom")

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawCustomProperties(self, layout)

        if preferences.getPreferences().developerMode:
            col = layout.column(align=True)
            col.prop(self, "output")

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    # ------------------------------------------------------------------
    # Getter
    # ------------------------------------------------------------------

    def getProperties(self, obj):
        """Return the name of the selected custom property.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected custom property and the value
                 as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getCustomProperties(self, obj)

    def getPropertyName(self):
        """Return the name of the selected custom property.

        :return: The name of the selected custom property.
        :rtype: str
        """
        if self.mode == 'LIST':
            if self.propertyEnum != 'NONE':
                return self.propertyEnum
        else:
            if len(self.propertyName):
                return self.propertyName

        return ""

    def getOutputProperties(self):
        """Return the output property.

        :return: A list with the node and the output property indices as
                 a tuple.
        :rtype: list(bpy.types.Node, int)
        """
        result = []

        for i in range(3):
            if self.driverIndex[i] != -1:
                result.append((self, i))

        return result

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def createDriver(self, nodeGroup, driven, rbfNode):
        """Create a driver for the property of the driven object.

        :param nodeGroup: The node tree of the current RBF setup.
        :type nodeGroup: bpy.types.NodeGroup
        :param driven: The driven object.
        :type driven: bpy.types.Object
        :param rbfNode: The current RBF node.
        :type rbfNode: bpy.types.Node
        """
        # Clear the driver indices.
        self.driverIndex = [-1, -1, -1]
        # Delete any existing driver.
        if rbfNode.active:
            self.deleteDriver(driven)

        props = self.getProperties(driven)
        if props:
            size = len(props)
            index = 0
            drivenIndex = -1
            if size > 1:
                drivenIndex = 0
            propString = '["{}"]'.format(self.getPropertyName())

            for i in range(size):
                dataPath = 'nodes["{}"].output[{}]'.format(self.name, str(index))
                driver.createNodeGroupDriver(nodeGroup, driven, dataPath, propString, drivenIndex)
                # Get the index of the created driver.
                self.driverIndex[index] = driver.getDriverIndex(driven, dataPath, propString, drivenIndex)
                self.isDriver = True

                if size > 1:
                    index += 1
                    drivenIndex += 1

    def deleteDriver(self, obj):
        """Delete the driver for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        """
        props = self.getProperties(obj)
        if props:
            size = len(props)
            drivenIndex = -1
            if size > 1:
                drivenIndex = 0
            propString = '["{}"]'.format(self.getPropertyName())

            for i in range(size):
                result = obj.driver_remove(propString, drivenIndex)
                dev.log("Delete driver: {} {}[{}] : {}".format(obj, propString, drivenIndex, result))

                if size > 1:
                    drivenIndex += 1

        # Clear the driver indices.
        self.driverIndex = [-1, -1, -1]

    def enableDriver(self, obj, enable):
        """Enable or disable the driver FCurves for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        :param enable: The enabled state of the driver FCurves.
        :type enable: bool
        """
        driver.enableDriver(self, obj, enable)
