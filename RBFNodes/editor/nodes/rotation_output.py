# <pep8 compliant>

import bpy

from . import common, node
from ... import dev, language, preferences, var
from ... core import driver


# Get the current language.
strings = language.getLanguage()


class RBFRotationOutputNode(node.RBFNode):
    """Object rotation output node.
    """
    bl_idname = "RBFRotationOutputNode"
    bl_label = strings.ROTATION_OUTPUT_LABEL
    bl_icon = 'ORIENTATION_GIMBAL'

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    def updateCallback(self, context):
        """Callback for any value changes.

        :param context: The current context.
        :type context: bpy.context
        """
        pass

    w_axis : bpy.props.BoolProperty(name=strings.W_LABEL, default=False)
    x_axis : bpy.props.BoolProperty(name=strings.X_LABEL, default=False)
    y_axis : bpy.props.BoolProperty(name=strings.Y_LABEL, default=False)
    z_axis : bpy.props.BoolProperty(name=strings.Z_LABEL, default=False)

    rotationMode : bpy.props.EnumProperty(name="", items=common.ROTATION_MODE, default='EULER')

    output : bpy.props.FloatVectorProperty(size=4, update=updateCallback)
    # The indices of the created drivers on the driven object.
    driverIndex : bpy.props.IntVectorProperty(size=4, default=(-1, -1, -1, -1))
    isDriver : bpy.props.BoolProperty(default=False)

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addInput("RBFPropertySocket", strings.ROTATION_LABEL)
        
    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        common.drawRotationProperties(self, layout)

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
        """Return the selected rotation properties for the given object.

        :param obj: The object to query.
        :type obj: bpy.types.Object

        :return: A list with the selected rotation properties and their
                 values as a tuple.
        :rtype: list(tuple(str, float))
        """
        return common.getRotationProperties(self, obj)

    def getOutputProperties(self):
        """Return the selected output properties.

        :return: A list with the node and the selected output property
                 indices as a tuple.
        :rtype: list(bpy.types.Node, int)
        """
        result = []

        if self.rotationMode == 'EULER':
            if self.x_axis:
                result.append((self, 0))
            if self.y_axis:
                result.append((self, 1))
            if self.z_axis:
                result.append((self, 2))
        else:
            for i in range(4):
                result.append((self, i))

        return result

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def createDriver(self, nodeGroup, driven, rbfNode):
        """Create a driver for each selected axis of the driven object.

        :param nodeGroup: The node tree of the current RBF setup.
        :type nodeGroup: bpy.types.NodeGroup
        :param driven: The driven object.
        :type driven: bpy.types.Object
        :param rbfNode: The current RBF node.
        :type rbfNode: bpy.types.Node
        """
        # Clear the driver indices.
        self.driverIndex = [-1, -1, -1, -1]
        # Delete any existing driver.
        if rbfNode.active:
            self.deleteDriver(driven)

        rotMode = var.ROTATIONS[self.rotationMode]

        if self.rotationMode == 'EULER':
            axes = [(self.w_axis, 0), (self.x_axis, 1), (self.y_axis, 2), (self.z_axis, 3)]
            shiftIndex = 1
        else:
            axes = [(True, 0), (True, 1), (True, 2), (True, 3)]
            shiftIndex = 0

        for axis, index in axes:
            if (self.rotationMode != 'EULER' and index == 0) or index > 0:
                if axis:
                    dataPath = 'nodes["{}"].output[{}]'.format(self.name, str(index-shiftIndex))
                    driver.createNodeGroupDriver(nodeGroup, driven, dataPath, rotMode, index-shiftIndex)
                    # Get the index of the created driver.
                    self.driverIndex[index] = driver.getDriverIndex(driven, dataPath, rotMode, index-shiftIndex)
                    self.isDriver = True

    def deleteDriver(self, obj):
        """Delete the driver for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        """
        rotMode = var.ROTATIONS[self.rotationMode]

        if self.rotationMode == 'EULER':
            axes = [(self.w_axis, 0), (self.x_axis, 1), (self.y_axis, 2), (self.z_axis, 3)]
            shiftIndex = 1
        else:
            axes = [(True, 0), (True, 1), (True, 2), (True, 3)]
            shiftIndex = 0

        for axis, index in axes:
            if (self.rotationMode != 'EULER' and index == 0) or index > 0:
                if axis:
                    result = obj.driver_remove(rotMode, index-shiftIndex)
                    dev.log("Delete driver: {} {}[{}] : {}".format(obj, rotMode, index, result))

        # Clear the driver indices.
        self.driverIndex = [-1, -1, -1, -1]

    def enableDriver(self, obj, enable):
        """Enable or disable the driver FCurves for the given object.

        :param obj: The driven object.
        :type obj: bpy.types.Object
        :param enable: The enabled state of the driver FCurves.
        :type enable: bool
        """
        driver.enableDriver(self, obj, enable)
