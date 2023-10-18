# <pep8 compliant>

import bpy

from . import node
from ... core import matrix, plugs, rbf, utils
from ... import dev, language, var

import json
import math


# Get the current language.
strings = language.getLanguage()


class RBFSolverNode(node.RBFNode):
    """RBF node.
    """
    bl_idname = "RBFSolverNode"
    bl_label = strings.RBF_LABEL
    bl_icon = 'POINTCLOUD_DATA'

    # ------------------------------------------------------------------
    # Property callbacks
    # ------------------------------------------------------------------

    def rbfMode(self, context):
        """Callback for the RBF mode.

        The pre-calculated weight matrix needs to be updated on a mode
        change because of the required interpolation function.

        :param context: The current context.
        :type context: bpy.context
        """
        if self.active_value:
            rbf.initialize(context, refresh=True)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    interpolation_items = [('LINEAR', strings.LINEAR_LABEL, ""),
                           ('GAUSSIAN_1', strings.GAUSS_1_LABEL, ""),
                           ('GAUSSIAN_2', strings.GAUSS_2_LABEL, ""),
                           ('THIN_PLATE', strings.THIN_PLATE_LABEL, ""),
                           ('MULTI_QUADRATIC', strings.MULTI_QUADRATIC_LABEL, ""),
                           ('INVERSE_MULTI_QUADRATIC', strings.MULTI_QUADRATIC_INVERSE_LABEL, "")]
    radius_items = [('MEAN', strings.MEAN_DISTANCE_LABEL, ""),
                    ('VARIANCE', strings.VARIANCE_LABEL, ""),
                    ('STANDARD_DEVIATION', strings.DEVIATION_LABEL, ""),
                    ('CUSTOM', strings.CUSTOM_LABEL, "")]
    mode : bpy.props.EnumProperty(name=strings.KERNEL_LABEL,
                                  items=interpolation_items,
                                  default='GAUSSIAN_1',
                                  update=rbfMode)
    radiusType : bpy.props.EnumProperty(name=strings.RADIUS_LABEL,
                                        items=radius_items,
                                        default='STANDARD_DEVIATION',
                                        update=rbfMode)
    radius : bpy.props.FloatProperty(name=strings.RADIUS_LABEL,
                                     default=1.0,
                                     min=0,
                                     update=rbfMode)
    negativeWeights : bpy.props.BoolProperty(name=strings.NEGATIVE_WEIGHTS_LABEL,
                                             default=True)
    active_value : bpy.props.BoolProperty(default=False)

    version : bpy.props.StringProperty()

    # Internal value for the RBF calculation.
    # Set during activation and used by the runtime calculation.
    meanDistance : bpy.props.FloatProperty(default=1.0)
    variance : bpy.props.FloatProperty(default=1.0)

    poseMatrix0 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix1 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix2 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix3 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix4 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix5 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix6 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix7 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix8 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix9 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix10 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix11 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix12 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix13 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix14 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix15 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix16 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix17 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix18 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix19 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix20 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix21 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix22 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix23 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix24 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix25 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix26 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix27 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix28 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix29 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix30 : bpy.props.FloatVectorProperty(size=32)
    poseMatrix31 : bpy.props.FloatVectorProperty(size=32)
    # Add additional floatVectorProperties here if the default capacity
    # is not efficient.
    # Important:
    # Also extend the number of weightMatrix properties below.
    # Update the NUM_ARRAYS constant in var.py accordingly.

    poseMatrixRows : bpy.props.IntProperty()
    poseMatrixColumns : bpy.props.IntProperty()

    weightMatrix0 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix1 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix2 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix3 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix4 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix5 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix6 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix7 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix8 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix9 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix10 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix11 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix12 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix13 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix14 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix15 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix16 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix17 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix18 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix19 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix20 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix21 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix22 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix23 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix24 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix25 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix26 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix27 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix28 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix29 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix30 : bpy.props.FloatVectorProperty(size=32)
    weightMatrix31 : bpy.props.FloatVectorProperty(size=32)
    # Add additional floatVectorProperties here if the default capacity
    # is not efficient.
    # Important:
    # Also extend the number of poseMatrix properties above.
    # Update the NUM_ARRAYS constant in var.py accordingly.

    weightMatrixRows : bpy.props.IntProperty()
    weightMatrixColumns : bpy.props.IntProperty()

    def init(self, context):
        """Initialize the node and add the sockets.

        :param context: The current context.
        :type context: bpy.context
        """
        self.addOutput("RBFObjectSocket", strings.OBJECTS_LABEL)
        self.addOutput("RBFNodeSocket", strings.NODES_LABEL)
        self.addInput("RBFObjectSocket", strings.OBJECTS_LABEL, link_limit=0)
        self.addInput("RBFNodeSocket", strings.NODES_LABEL, link_limit=0)
        self.addInput("RBFPoseSocket", strings.POSES_LABEL, link_limit=0)
        utils.setVersion(self)
        dev.log("Version: {}".format(utils.getVersion(self)))

    def draw(self, context, layout):
        """Draw the content of the node.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        layout.use_property_decorate = False

        layout.prop(self, "mode")
        layout.prop(self, "radiusType")
        if self.radiusType == 'CUSTOM':
            layout.prop(self, "radius")
        layout.prop(self, "negativeWeights")

    def draw_buttons_ext(self, context, layout):
        """Draw node buttons in the sidebar.

        :param context: The current context.
        :type context: bpy.context
        :param layout: The current layout.
        :type layout: bpy.types.UILayout
        """
        self.draw(context, layout)

    @property
    def active(self):
        """Return, if the node is active and used for processing.

        If active but no connections exist, set the node to inactive.

        :return: The active state of the node.
        :rtype: bool
        """
        if self.active_value:
            inConn = plugs.getInputNodes(self.inputs[0])
            outConn = plugs.getInputNodes(self.outputs[0])
            if not inConn and not outConn:
                self.active_value = False
                self.use_custom_color = False
                self.color = var.COLOR_DEFAULT[:-1]

        return self.active_value

    @active.setter
    def active(self, state):
        """Set the node to active or inactive which sets the property
        and a background color for the node.

        :param state: The value for the active state.
        :type state: bool
        """
        if state:
            color = [i*0.55 for i in var.COLOR_GREEN[:-1]]
            self.resetLabel()
        else:
            color = [i*0.55 for i in var.COLOR_RED[:-1]]
            self.suffixLabel("Error")

        self.use_custom_color = True
        self.color = color

        self.active_value = state

    def reset(self):
        """Clear all stored data.
        """
        dev.log("Resetting RBF node: {}".format(self.name))
        self.active_value = False
        self.meanDistance = 0.0
        self.variance = 0.0
        self.poseMatrixRows = 0
        self.poseMatrixColumns = 0
        self.weightMatrixRows = 0
        self.weightMatrixColumns = 0
        self.resetLabel()
        dev.log("Reset state")

        values = [0] * var.MAX_LEN
        for i in range(var.NUM_ARRAYS):
            self.setFloatVector(i, values, "poseMatrix")
            self.setFloatVector(i, values, "weightMatrix")
        dev.log("Reset matrices")

        self.use_custom_color = False
        self.color = var.COLOR_DEFAULT[:-1]

        utils.setVersion(self)
        dev.log("Version: {}".format(utils.getVersion(self)))
        dev.log("Reset finished")

    def getRadius(self):
        """Return the current radius value.

        :return: The radius value. Return -1 if the selection is set to
                 mean distance.
        :rtype: float
        """
        if self.radiusType == 'MEAN':
            return self.meanDistance
        elif self.radiusType == 'VARIANCE':
            return self.variance
        elif self.radiusType == 'STANDARD_DEVIATION':
            return math.sqrt(self.variance)
        else:
            return self.radius

    def suffixLabel(self, suffix):
        """Extend the current node label with the given suffix.

        :param suffix: The suffix string to add.
        :type suffix: str
        """
        current = self.label
        if not len(current):
            current = self.bl_label
        self.label = "{}: {}".format(current, suffix)

    def resetLabel(self):
        """Reset the label by removing the suffix.
        """
        current = self.label.split(":")[0]
        if current == self.bl_label:
            current = ""
        self.label = current

    # ------------------------------------------------------------------
    # Matrix storage
    # ------------------------------------------------------------------

    def setPoseMatrix(self, mat):
        """Store the given matrix in the pose vector arrays.

        :param mat: The matrix to store.
        :type mat: Matrix
        """
        self.poseMatrixRows = mat.rows
        self.poseMatrixColumns = mat.cols
        self.setMatrix(mat, "poseMatrix")

    def setWeightMatrix(self, mat):
        """Store the given matrix in the weight vector arrays.

        :param mat: The matrix to store.
        :type mat: Matrix
        """
        self.weightMatrixRows = mat.rows
        self.weightMatrixColumns = mat.cols
        self.setMatrix(mat, "weightMatrix")

    def setMatrix(self, mat, name):
        """Store the given matrix in the vector arrays.

        Create chunks of values if the number of given values doesn't
        fit into one array.

        :param mat: The matrix to store.
        :type mat: Matrix
        :param name: The vector array property string.
        :type name: str
        """
        # Flatten the matrix to get a single list of values.
        values = mat.flatten()
        # The complete number of values to store.
        size = len(values)
        # The number of vector arrays required.
        arrayCount = math.ceil(size / var.MAX_LEN)
        # The number of values required to fill all arrays.
        fullSize = arrayCount * var.MAX_LEN
        # Extend the value list to fill all arrays.
        values.extend([0] * (fullSize - size))

        arrayIndex = 0
        for i in range(0, size, var.MAX_LEN):
            # Store the partial matrix in one of the vector arrays.
            self.setFloatVector(arrayIndex, values[i:i + var.MAX_LEN], name)
            # Increment the vector property index.
            arrayIndex += 1

    def getPoseMatrix(self):
        """Return the stored values from the vector arrays as a Matrix.

        :return: The matrix of the stored pose values.
        :rtype: Matrix
        """
        rows = self.poseMatrixRows
        cols = self.poseMatrixColumns
        return self.getMatrix("poseMatrix", rows, cols)

    def getWeightMatrix(self):
        """Return the stored values from the vector arrays as a Matrix.

        :return: The matrix of the stored weight values.
        :rtype: Matrix
        """
        rows = self.weightMatrixRows
        cols = self.weightMatrixColumns
        return self.getMatrix("weightMatrix", rows, cols)

    def getMatrix(self, name, rows, cols):
        """Return the stored values from the vector arrays as a Matrix.

        :param name: The vector array property string.
        :type name: str
        :param rows: The number of matrix rows.
        :type rows: int
        :param cols: The number of matrix columns.
        :type cols: int

        :return: The matrix of the stored values.
        :rtype: Matrix
        """
        # The complete number of values to read.
        size = rows * cols
        if size == 0:
            return

        allValues = []
        # The number of vector arrays to read from.
        arrayCount = math.ceil(size / var.MAX_LEN)
        for a in range(arrayCount):
            allValues.extend(self.getFloatVector(a, name))

        mat = matrix.Matrix(rows, cols)
        mat.mat = [allValues[i:i + cols] for i in range(0, size, cols)]
        return mat

    def setFloatVector(self, index, values, name):
        """Set the indexed float vector property with the given values.

        :param index: The index of the float vector property.
        :type index: int
        :param values: The list of values to set.
        :type values: list(float)
        :param name: The vector array property string.
        :type name: str
        """
        setattr(self, "{}{}".format(name, index), values)

    def getFloatVector(self, index, name):
        """Get the values from the indexed float vector property.

        :param index: The index of the float vector property.
        :type index: int
        :param name: The vector array property string.
        :type name: str
        """
        return getattr(self, "{}{}".format(name, index))
