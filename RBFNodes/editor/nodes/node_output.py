# <pep8 compliant>

import bpy

from . import common, node
from ... import dev, language, preferences, var
from ... core import driver


# Get the current language.
strings = language.getLanguage()


class RBFNodeOutputNode(node.RBFNode):
    """Node tree output node.
    """
    bl_idname = "RBFNodeOutputNode"
    bl_label = strings.NODE_OUTPUT_LABEL
    bl_icon = 'NODETREE'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def updateCallback(self, context):
        """Callback for any value changes.

        :param context: The current context.
        :type context: bpy.context
        """
        pass

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    parentItems = [('MATERIAL', strings.MATERIAL_LABEL, ""),
                   ('NODE_GROUP', strings.NODE_GROUP_LABEL, "")]
    nodeParent : bpy.props.EnumProperty(name="", items=parentItems)
    parentName : bpy.props.StringProperty(name=strings.PARENT_LABEL)
    nodeName : bpy.props.StringProperty(name=strings.NODE_LABEL)
    plugName : bpy.props.StringProperty(name=strings.PLUG_LABEL)
    propertyEnum : bpy.props.EnumProperty(name="",
                                          items=common.nodeItemsCallback,
                                          update=common.setPropertyPlugName)

    output : bpy.props.FloatVectorProperty(size=var.ARRAY_SIZE, update=updateCallback)
    # The indices of the created drivers on the driven object.
    driverIndex : bpy.props.IntVectorProperty(size=var.ARRAY_SIZE, default=[-1]*var.ARRAY_SIZE)
    isDriver : bpy.props.BoolProperty(default=False)

    propertyPlugs = {}

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addInput("RBFNodeSocket", strings.NODE_LABEL)

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawNodeProperties(self, layout)

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

    def getProperties(self):
        """Return the name of the selected custom property.

        :return: A list with the selected custom property and the value
                 as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getNodeProperties(self)

    def getOutputProperties(self):
        """Return the output property.

        :return: A list with the node and the output property indices as
                 a tuple.
        :rtype: list(bpy.types.Node, int)
        """
        result = []

        for i in range(var.ARRAY_SIZE):
            if self.driverIndex[i] != -1:
                result.append((self, i))

        return result

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def _buildDriverItems(self, prop):
        """Extract and build the necessary elements for creating or
        removing a driver from the given property string.

        :param prop: The string containing the node and property.
        :type prop: str

        Examples:
        bpy.data.materials["eyes"].node_tree.nodes["Mix"]:inputs[2].default_value
        bpy.data.node_groups["Geometry Nodes"].nodes["Value"]:outputs[0].default_value
        """
        # Split the prop string into the node and property items.
        # Example:
        # bpy.data.materials["Material"].node_tree.nodes["Mix"]
        # and
        # inputs[0].default_value[0]
        items = prop.split(":")
        propItems = items[1].split(".")
        # The driven object needs to be the socket.
        # bpy.data.materials["Material"].node_tree.nodes["Mix"].inputs[0]
        driven = eval(".".join([items[0], propItems[0]]))
        # The object which receives the driver is the node tree.
        # bpy.data.materials['Material'].node_tree
        obj = eval(items[0]).id_data
        propString = propItems[1]
        if items[0].startswith("bpy.data.materials"):
            propStringLong = ".".join([items[0].split("node_tree.")[-1], items[1]])
        else:
            propStringLong = "nodes{}.{}".format(items[0].split(".nodes")[-1], items[1])

        return obj, driven, propString, propStringLong

    def createDriver(self, nodeGroup, driven, rbfNode):
        """Create a driver for the property of the driven object.

        :param nodeGroup: The node tree of the current RBF setup.
        :type nodeGroup: bpy.types.NodeGroup
        :param driven: The driven object. Not used in case of the node
                       ouput node.
        :type driven: bpy.types.Object
        :param rbfNode: The current RBF node.
        :type rbfNode: bpy.types.Node
        """
        # Clear the driver indices.
        self.driverIndex = [-1] * var.ARRAY_SIZE
        # Delete any existing driver.
        if rbfNode.active:
            self.deleteDriver()

        props = self.getProperties()
        if props:
            size = len(props)
            index = 0
            drivenIndex = -1
            if size > 1:
                drivenIndex = 0

            for prop, value, poseValue in props:
                obj, driven, propString, propStringLong = self._buildDriverItems(prop)
                dataPath = 'nodes["{}"].output[{}]'.format(self.name, str(index))
                driver.createNodeGroupDriver(nodeGroup, driven, dataPath, propString, drivenIndex)
                # Get the index of the created driver.
                self.driverIndex[index] = driver.getDriverIndex(obj,
                                                                dataPath,
                                                                propStringLong,
                                                                drivenIndex)
                self.isDriver = True

                if size > 1:
                    index += 1
                    drivenIndex += 1

    def deleteDriver(self, *args):
        """Delete the drivers for the current node.
        """
        props = self.getProperties()
        if props:
            size = len(props)
            drivenIndex = -1
            if size > 1:
                drivenIndex = 0

            for prop, value, poseValue in props:
                obj, driven, propString, propStringLong = self._buildDriverItems(prop)
                result = obj.driver_remove(propStringLong, drivenIndex)
                dev.log("Delete driver: {} {}[{}] : {}".format(obj, propStringLong, drivenIndex, result))

                if size > 1:
                    drivenIndex += 1

        # Clear the driver indices.
        self.driverIndex = [-1] * var.ARRAY_SIZE

    def enableDriver(self, obj, enable):
        """Enable or disable the driver FCurves for the given object.

        :param obj: The driven object. Not used in case of the node
                    ouput node.
        :type obj: bpy.types.Object
        :param enable: The enabled state of the driver FCurves.
        :type enable: bool
        """
        props = self.getProperties()
        if props:
            for prop, value, poseValue in props:
                obj, driven, propString, propStringLong = self._buildDriverItems(prop)
                driver.enableDriver(self, obj, enable)
