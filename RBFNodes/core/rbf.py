# <pep8 compliant>

import bpy

from . import driver, matrix, nodeTree, plugs, poses
from .. import var

import json
import math

MAX_SIZE = 1024


def initialize(context):
    """Pre-calculate the weight matrix based on the existing poses and
    activate the RBF node.
    This also creates the necessary drivers for the target object/s
    which are driven by the RBF outputs.

    :param context: The current context.
    :type context: bpy.context

    :return: None, or a tuple with the error type and message.
    :rtype: None or tuple(str, str)
    """
    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode is None:
        return {'WARNING'}, "No RBF node exists in the node tree"

    # Check, if all nodes are set up correctly. This can easily be done
    # by getting the pose data as when creating a pose.
    driverData = poses.getPoseInputData(rbfNode)
    drivenData = poses.getPoseOutputData(rbfNode)
    # If the second tuple item is a string an error has occurred.
    # In this case the driverData is the error type and the driven
    # data is the message.
    if len(driverData) > 1 and isinstance(driverData[1], str):
        return driverData
    if len(drivenData) > 1 and isinstance(drivenData[1], str):
        return drivenData

    result = solveWeightMatrix(rbfNode)

    if isinstance(result, tuple):
        rbfNode.active = False
        return result[0], result[1]

    # Create the drivers.
    nodeGroup = nodeTree.getNodeTree(context)
    result = driver.generateDrivers(nodeGroup, rbfNode)
    if result:
        return result[0], result[1]

    # Activate the RBF node.
    rbfNode.active = True

    if var.EXPOSE_DATA:
        print("RBF solver successfully initialized")


def solveWeightMatrix(rbfNode):
    """Solve the weight matrix based on the input and output values
    defined by the poses.

    :param rbfNode: The RBF node to solve.
    :type rbfNode: bpy.types.Node

    :return: True, if the solve was successful. A tuple if there was a
             decomposition error.
    :rtype: bool or tuple
    """
    # Get the pose nodes of the current solver.
    poseNodes = nodeTree.getPoseNodes(rbfNode)
    poseCount = len(poseNodes)
    if not poseCount:
        return {'WARNING'}, "No poses defined"

    # Create matrices for all driving and driven property values.
    inputMat = propertyDataToMatrix(poseNodes, isDriver=True)
    outputMat = propertyDataToMatrix(poseNodes, isDriver=False)

    # Normalize the input matrix.
    inputNorms = inputMat.normsColumn()
    inputMat.normalize(inputNorms, rows=False)

    # Important:
    # Append the input norm factors as a new row to the input matrix.
    # The norm factors are being used to normalize the driver vector and
    # need to be stored on the RBF node.
    # But since the size of the norm factors is arbitrary and there's a
    # limitation to the length of vector array properties it's easiest
    # to simply add the values to the input matrix as an additional row.
    # This needs to be considered when reading the input matrix at the
    # interpolation state.
    inputMat_ext = inputMat.copy()
    inputMat_ext.mat.append(inputNorms)
    inputMat_ext.rows += 1

    # Make sure that the maximum number of values which can be stored is
    # not exceeded.
    # The maximum size is defined by the 32 vector array properties of
    # the RBF node which only can store 32 float values per array.
    if inputMat_ext.rows * max(inputMat_ext.cols, outputMat.cols) > MAX_SIZE:
        return {'WARNING'}, "Maximum matrix size exceeded"

    if var.EXPOSE_DATA:
        print("Driver (with normalization row):")
        print(inputMat_ext)
        print("Driven:")
        print(outputMat)

    # Store the input matrix for the runtime calculation.
    rbfNode.setPoseMatrix(inputMat_ext)

    # ------------------------------------------------------------------
    # Distances
    # ------------------------------------------------------------------

    # Create a distance matrix from all poses and calculate the mean
    # distance for the rbf function.
    distMat, meanDist = getDistances(inputMat)
    rbfNode.meanDistance = meanDist
    if var.EXPOSE_DATA:
        print("Distance matrix:")
        print(distMat)

    # ------------------------------------------------------------------
    # Activations
    # ------------------------------------------------------------------

    # Transform the distance matrix to include the activation values.
    distMat = getActivations(distMat, rbfNode.getRadius(), rbfNode.mode)
    if var.EXPOSE_DATA:
        print("Activations:")
        print(distMat)

    # ------------------------------------------------------------------
    # Solve
    # ------------------------------------------------------------------

    outputSize = outputMat.cols
    weightMat = matrix.Matrix(poseCount, outputSize)

    for i in range(outputSize):
        y = outputMat.getColumnVector(i)

        solveMat = distMat.copy()
        w = []
        for j in range(poseCount):
            w.append(0)
        w = solveMat.solve(y, w)
        if not len(w):
            return {'WARNING'}, "Decomposition error"

        for j in range(poseCount):
            weightMat[j, i] = w[j]

    if var.EXPOSE_DATA:
        print("Weight matrix:")
        print(weightMat)

    # ------------------------------------------------------------------
    # Store
    # ------------------------------------------------------------------

    rbfNode.setWeightMatrix(weightMat)

    if var.EXPOSE_DATA:
        print("Weight matrix successfully created")

    return True


def propertyDataToMatrix(nodes, isDriver=True):
    """Build a matrix from all poses and their properties.

    :param nodes: The list of pose nodes.
    :type nodes: list(bpy.types.Nodes)
    :param isDriver: True, for building a matrix from the driver
                     properties.
    :type isDriver: bool

    :return: The pose matrix.
    :rtype: Matrix
    """
    if isDriver:
        propSize = poses.getPropertyCount(json.loads(nodes[0].driverData))
    else:
        propSize = poses.getPropertyCount(json.loads(nodes[0].drivenData))

    mat = matrix.Matrix(len(nodes), propSize)

    for i, node in enumerate(nodes):
        if isDriver:
            data = json.loads(node.driverData)
        else:
            data = json.loads(node.drivenData)

        allValues = []
        for obj, props in data:
            allValues.extend([p[1] for p in props])

        for j in range(len(allValues)):
            mat[i, j] = allValues[j]

    return mat


def getDistances(mat):
    """Build a matrix containing the distance values between all poses.
    Based on all distances also calculate the mean distance which is
    needed for the RBF calculation.

    :param mat: The matrix containing all poses.
    :type mat: Matrix

    :return: A tuple with the distance matrix and the mean distance.
    :rtype: tuple(Matrix, float)
    """
    size = mat.rows

    distMat = matrix.Matrix(size, size)
    value = 0.0

    for i in range(size):
        for j in range(size):
            dist = getRadius(mat.getRowVector(i), mat.getRowVector(j))
            distMat[i, j] = dist
            value += dist

    meanDist = value / (size*size)

    return distMat, meanDist


def getRadius(vec1, vec2):
    """Calculate the linear distance between two vectors.

    :param vec1: The first vector.
    :type vec1: list(float)
    :param vec2: The second vector.
    :type vec2: list(float)

    :return: The linear distance.
    :rtype: float
    """
    value = 0.0
    for i in range(len(vec1)):
        value += pow(vec1[i] - vec2[i], 2)
    return math.sqrt(value)


def getActivations(mat, width, kernel):
    """Calculate the RBF activation values.

    :param mat: The matrix with the activation values.
    :type mat: Matrix
    :param width: The activation width.
    :type width: float
    :param kernel: The interpolation function.
                   ('LINEAR', 'GAUSSIAN')
    :type kernel: str

    :return: The activation matrix.
    :rtype: Matrix
    """
    size = mat.rows

    for i in range(size):
        for j in range(size):
            mat[i, j] = interpolateRbf(mat[i, j], width, kernel)

    return mat


def interpolateRbf(value, width, kernel):
    """Interpolation function for processing the weight values.

    :param value: The value to interpolate.
    :type value: float
    :param width: The activation width.
    :type width: float
    :param kernel: The interpolation function.
                   ('LINEAR', 'GAUSSIAN')
    :type kernel: str

    :return: The new interpolated value.
    :rtype: float
    """
    if width == 0.0:
        width = 1.0

    # LINEAR
    result = value

    # GAUSSIAN_1
    if kernel == 'GAUSSIAN_1':
        width = 1.0 / width
        sigma = -(width * width)
        result = math.exp(sigma * value)
    # GAUSSIAN_2
    elif kernel == 'GAUSSIAN_2':
        width *= 0.707
        result = math.exp(-(value * value) / (2.0 * width * width))
    # THIN_PLATE
    elif kernel == 'THIN_PLATE':
        value /= width
        result = value * value * math.log(value) if value > 0 else value
    # MULTI_QUADRATIC
    elif kernel == 'MULTI_QUADRATIC':
        result = math.sqrt((value * value) + (width * width))
    # INVERSE_MULTI_QUADRATIC
    elif kernel == 'INVERSE_MULTI_QUADRATIC':
        result = 1.0 / math.sqrt((value * value) + (width * width))

    return result


def getPoseWeights(rbfNode):
    """Calculate the individual output weights based on the current
    driver values in relation to the stored poses.

    This is the main part of the RBF calculation but a rather simple
    process as it just gets the distances of the driver to the stored
    poses and calculates the weighted output values based on the weight
    matrix built during initialization.
    """
    # Get the stored pose matrix from the RBF node.
    poseMat = rbfNode.getPoseMatrix()
    if poseMat is None:
        return
    # The actual number of poses is the number of rows -1 because the
    # last row represents the norm factors for normalization.
    poseSize = poseMat.rows - 1

    weightMat = rbfNode.getWeightMatrix()
    if weightMat is None:
        return
    outSize = weightMat.cols

    # Get the current driver values and normalize them with the stored
    # norm factors.
    driverValues = poses.getDriverValues(rbfNode)
    norms = poseMat.getRowVector(poseSize)
    driverValues = matrix.normalizeVector(driverValues, factors=norms)

    outValues = [0.0] * outSize
    for i in range(poseSize):
        poseValues = poseMat.getRowVector(i)
        dist = getRadius(poseValues, driverValues)

        for j in range(outSize):
            outValues[j] += weightMat[i, j] * interpolateRbf(dist, rbfNode.getRadius(), rbfNode.mode)

    # Get the output properties for setting their values.
    outProps = poses.getOutputProperties(rbfNode)

    for i in range(outSize):
        node, index = outProps[i]
        value = outValues[i]
        if value < 0.0 and not rbfNode.negativeWeights:
            value = 0.0
        if isinstance(node.output, float):
            node.output = value
        else:
            node.output[index] = value


def update(context):
    """Update the solver after a pose edit.

    :param context: The current context.
    :type context: bpy.context

    :return: None, or a tuple with the error type and message.
    :rtype: None or tuple(str, str)
    """
    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode is None:
        return {'WARNING'}, "No RBF node exists in the node tree"

    # Update the pose values and re-enable all drivers.
    poses.updatePose()

    # Update the solver.
    if rbfNode.active:
        result = solveWeightMatrix(rbfNode)

        if isinstance(result, tuple):
            rbfNode.active = False
            return result[0], result[1]


def reset(context):
    """Reset the RBF node to its default values and clear all stored
    data.
    Delete all drivers from the output nodes.

    :param context: The current context.
    :type context: bpy.context

    :return: None, or a tuple with the error type and message.
    :rtype: None or tuple(str, str)
    """
    rbfNode = nodeTree.getRBFNode(context)
    if rbfNode is None:
        return {'WARNING'}, "No RBF node exists in the node tree"

    rbfNode.reset()

    nodeTypes = ["RBFObjectOutputNode", "RBFNodeOutputNode"]

    for i, nodeType in enumerate(nodeTypes):
        for node in plugs.getOutputNodes(rbfNode.outputs[i], nodeId=nodeType):
            if node.bl_idname == "RBFObjectOutputNode":
                obj = node.getObject()
                if obj:
                    for socket in node.outputs:
                        for outNode in plugs.getOutputNodes(socket):
                            outNode.deleteDriver(obj)
            elif node.bl_idname == "RBFNodeOutputNode":
                node.deleteDriver()