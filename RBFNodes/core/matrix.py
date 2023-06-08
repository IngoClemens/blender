# <pep8 compliant>

import math
import mathutils

from .. import dev


class Matrix(object):
    """Class for a two-dimensional matrix.
    """
    def __init__(self, rowSize=0, colSize=0):
        """Initialization.

        :param rowSize: The number of matrix rows.
        :type rowSize: int
        :param colSize: The number of matrix columns.
        :type colSize: int
        """
        self.mat = self.fill(rowSize, colSize)
        self.rows = rowSize
        self.cols = colSize

    def __getitem__(self, index):
        """Return a value from the matrix at the given position.

        :param index: A tuple with the row and column index.
        :type index: tuple(int, int)

        :return: The value at the given position.
        :rtype: float
        """
        if isinstance(index, tuple):
            x, y = index
            return self.mat[x][y]

    def __setitem__(self, index, value):
        """Set a matrix value at the given position.

        :param index: A tuple with the row and column index.
        :type index: tuple(int, int)
        :param value: The value to set.
        :type value: float
        """
        if isinstance(index, tuple):
            x, y = index
            self.mat[x][y] = value

    def __str__(self):
        """Return a string representation of the current matrix.

        :return: The matrix as a string.
        :rtype: str
        """
        numSize = _getMaxNumberLength(self)

        lines = []
        for i in range(self.rows):
            suffix = "]"
            if i == 0:
                prefix = "Matrix [["
            else:
                prefix = "        ["
            if i == self.rows - 1:
                suffix = "]]"
            values = ", ".join([_conformValue(f, numSize) for f in self.mat[i]])
            lines.append("".join([prefix, values, suffix]))
        return "\n".join(lines)

    def copy(self):
        """Copy the current matrix to a new matrix and return it.

        :return: The copied matrix.
        :rtype: Matrix
        """
        newMatrix = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                newMatrix[i, j] = self.mat[i][j]
        return newMatrix

    def flatten(self):
        """Return the matrix as a list of values.

        :return: The list representation of the matrix.
        :rtype: list(float)
        """
        return [self.mat[i][j] for i in range(self.rows) for j in range(self.cols)]

    def normsRow(self):
        """Return the normalization factor for each vector row.

        :return: A list with a normalization factor for each row.
        :rtype: list
        """
        norms = []
        for i in range(self.rows):
            norms.append(norm(self.mat[i]))
        return norms

    def normsColumn(self):
        """Return the normalization factor for each vector column.

        :return: A list with a normalization factor for each column.
        :rtype: list
        """
        norms = []
        for i in range(self.cols):
            norms.append(norm(self.getColumnVector(i)))
        return norms

    def normalize(self, factor, rows=True):
        """Normalize the matrix by the given normalization factor.

        :param factor: The list of factors for each row.
        :type factor: list(float)
        :param rows: True, if the matrix rows should get normalized.
                     False, for columns.
        :type rows: bool

        :return: True, if the process was successful. It fails when the
                 size of factors doesn't match the number of matrix
                 rows.
        :rtype: bool
        """
        if rows:
            if self.rows != len(factor):
                return False
            self._normalizeRows(factor)
        else:
            if self.cols != len(factor):
                return False
            self._normalizeCols(factor)

        return True

    def _normalizeRows(self, factor):
        """Normalize the matrix by the given normalization factor.

        :param factor: The list of factors for each row.
        :type factor: list(float)
        """
        for i in range(self.rows):
            for j in range(self.cols):
                if factor[i] > 0:
                    self.mat[i][j] /= factor[i]

    def _normalizeCols(self, factor):
        """Normalize the matrix by the given normalization factor.

        :param factor: The list of factors for each column.
        :type factor: list(float)
        """
        for j in range(self.cols):
            for i in range(self.rows):
                if factor[j] > 0:
                    self.mat[i][j] /= factor[j]

    # ------------------------------------------------------------------
    # Size
    # ------------------------------------------------------------------

    def fill(self, rowSize, colSize, fill=0):
        """Create a new matrix with the given size and fill it with the
        given value.

        :param rowSize: The number of matrix rows.
        :type rowSize: int
        :param colSize: The number of matrix columns.
        :type colSize: int
        :param fill: The value to use to fill the matrix.
        :type fill: int

        :return: The new matrix.
        :rtype: list(list)
        """
        mat = []
        for i in range(rowSize):
            col = []
            for j in range(colSize):
                col.append(fill)
            mat.append(col)
        return mat.copy()

    def setSize(self, rowSize, colSize, fill=0, clear=False):
        """Set the matrix to the given size.

        This also initializes the matrix with zeros.

        :param rowSize: The number of matrix rows.
        :type rowSize: int
        :param colSize: The number of matrix columns.
        :type colSize: int
        :param fill: The value to use to fill the addition matrix
                     positions.
        :type fill: int
        :param clear: Fill the matrix with zeros.
        :type clear: bool
        """
        if clear:
            mat = self.fill(rowSize, colSize, fill)
        else:
            mat = []
            for i in range(rowSize):
                col = []
                if i < self.rows:
                    for j in range(colSize):
                        if j < self.cols:
                            col.append(self.mat[i][j])
                        else:
                            col.append(fill)
                else:
                    for j in range(colSize):
                        col.append(fill)
                mat.append(col)

        self.mat = mat.copy()
        self.rows = rowSize
        self.cols = colSize

    # ------------------------------------------------------------------
    # Get vector
    # ------------------------------------------------------------------

    def getRowVector(self, index):
        """Return all values of the given row index as a list.

        :param index: The index of the row.
        :type index: int

        :return: The list of row values.
        :rtype: list
        """
        return self.mat[index].copy()

    def getColumnVector(self, index):
        """Return all values of the given column index as a list.

        :param index: The index of the column.
        :type index: int

        :return: The list of column values.
        :rtype: list
        """
        vec = []
        for i in range(self.rows):
            vec.append(self.mat[i][index])
        return vec

    # ------------------------------------------------------------------
    # Mean and standard deviation
    # ------------------------------------------------------------------

    def mean(self):
        """Return the mean from all values contained in the matrix.

        :return: The mean value.
        :rtype: float
        """
        value = 0.0
        for i in range(self.rows):
            for j in range(self.cols):
                value += self.mat[i][j]
        return value / (self.rows * self.cols)

    def variance(self):
        """Return the variance of all values.

        :return: The variance value.
        :rtype: float
        """
        mean = self.mean()
        value = 0.0
        for i in range(self.rows):
            for j in range(self.cols):
                value += pow(self.mat[i][j] - mean, 2)
        return value / (self.rows * self.cols)

    # ------------------------------------------------------------------
    # Gaussian elimination
    # ------------------------------------------------------------------

    def solve(self, y, w):
        """Solve the current matrix based on the given column vector.

        :param y: The column vector for the solve.
        :type y: list(float)
        :param w: The list of weights to be generated.
        :type w: list(float)

        :return: The list of weights and an error message, if any.
        :rtype: tuple(list(float), None or str)
        """
        # Make sure that the matrix is square.
        if self.rows != self.cols:
            dev.log("Matrix rows and columns do not match")
            return [], "The number of poses between input and output is different"

        size = self.rows

        for i in range(size):
            # Find the row with the largest absolute value in the first
            # column and store the pivot index.
            maxVal = self.mat[i][i]
            pivot = i
            swap = False
            for j in range(i + 1, size):
                if abs(maxVal) < abs(self.mat[j][i]):
                    maxVal = self.mat[j][i]
                    pivot = j
                    swap = True

            # Perform the row interchange if necessary.
            if swap:
                for j in range(size):
                    w[j] = self.mat[pivot][j]
                    self.mat[pivot][j] = self.mat[i][j]
                    self.mat[i][j] = w[j]

                # Swap the order of the values.
                value = y[pivot]
                y[pivot] = y[i]
                y[i] = value

            # Check if the matrix is singular.
            if abs(self.mat[i][i]) < 0.0001:
                dev.log("The matrix is singular")
                return [], ("The pose at index {} has no unique values and " +
                            "is similar to another pose").format(i)

            # Perform the forward elimination.
            for j in range(i + 1, size):
                mult = self.mat[j][i] / self.mat[i][i]
                for k in range(size):
                    self.mat[j][k] -= mult * self.mat[i][k]
                y[j] -= mult * y[i]

        # Perform the back substitution.
        for x in reversed(range(0, size)):
            value = 0.0
            for j in range(x + 1, size):
                value += self.mat[x][j] * w[j]
            w[x] = (y[x] - value) / self.mat[x][x]

        return w, None


def norm(vec):
    """Return the normalization factor for the given vector.

    :param vec: The vector.
    :type vec: list(float)

    :return: The normalization factor.
    :rtype: float
    """
    value = 0.0
    for i in range(len(vec)):
        value += pow(vec[i], 2)
    return math.sqrt(value)


def normalizeVector(vec, factors=None):
    """Normalize the given vector.

    :param vec: The vector to normalize.
    :type vec: list(float)
    :param factors: The list of normalization factors for each vector
                    value.
    :type factors: list(float)

    :return: The normalized vector.
    :rtype: list
    """
    if len(vec) != len(factors):
        return vec

    for i in range(len(vec)):
        if factors[i] > 0:
            vec[i] /= factors[i]

    return vec


def _getNumberLength(value):
    """Return the length of the whole part of the given value.

    :param value: The float value to get the length from.
    :type value: float

    :return: The character size of the whole number.
    :rtype: int
    """
    items = str(value).split(".")
    return len(items[0])


def _getMaxNumberLength(mat):
    """Return the size of the largest whole number of the given matrix.

    :param mat: The Matrix.
    :type mat: Matrix

    :return: The character size of the largest whole number.
    :rtype: int
    """
    numSize = 0
    for i in range(mat.rows):
        for j in range(mat.cols):
            x = _getNumberLength(mat[i, j])
            numSize = x if x > numSize else numSize

    return numSize


def _conformValue(value, numSize):
    """Return a formatted string which has been leading and trailing
    added to fit the given character length.

    :param value: The value to convert.
    :type value: float
    :param numSize: The number of characters to fit.
    :type numSize: int

    :return: The formatted string.
    :rtype: str
    """
    items = "{:.4f}".format(value).split(".")
    if len(items) == 1:
        items.append("0")

    if len(items[0]) < numSize:
        items[0] = "{}{}".format(" "*(numSize-len(items[0])), items[0])
    if len(items[1]) < 4:
        items[1] = "{}{}".format(items[1], " "*(4-len(items[1])))

    return ".".join(items)


# ----------------------------------------------------------------------
# Custom functions for converting a quaternion to an exponential map and
# back.
# The functions are not used because Blender provides these by default.
# But they are included for reference.
# ----------------------------------------------------------------------


def quaternionToExponentialMap(quat):
    """Calculate the exponential map representation of the given
    quaternion.

    :param quat: The rotation quaternion.
    :type quat: list(float) or Quaternion

    :return: The exponential map of the quaternion with the rotation
             axis values already multiplied by the rotation angle.
    :rtype: list(float)
    """
    w, x, y, z = q

    vec = [x, y, z]

    # Calculate the normalisation factor.
    normFactor = math.sqrt(sum([pow(i, 2) for i in vec]))

    # Check, if the quaternion is close to zero to avoid division by
    # zero.
    if normFactor < 1e-8:
        return [0, 0, 0]

    # Calculate the rotation angle.
    phi = 2 * math.atan2(normFactor, w)

    # Calculate the rotation axis.
    axis = [i / normFactor for i in vec]

    return [i * phi for i in axis]


def exponentialMapToQuaternion(expMap):
    """Convert the given exponential map back to a quaternion.

    The exponential map has the rotation axis values already multiplied
    by the rotation angle.

    :param expMap: The exponential map.
    :type expMap: list(float)

    :return: The converted quaternion.
    :rtype: Quaternion
    """
    angle = math.sqrt(expMap[0]**2 + expMap[1]**2 + expMap[2]**2)
    factor = 1.0 / angle
    normVec = [i * factor for i in expMap]

    if angle != 0:
        phi = 0.5 * angle
        factor = math.sin(phi)
        vec = [i * factor for i in normVec]

        return mathutils.Quaternion([math.cos(phi), vec[0], vec[1], vec[2]])
    else:
        return mathutils.Quaternion()
