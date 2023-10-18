# <pep8 compliant>

import bpy

import importlib
import os

from . import preferences


def reload(name=""):
    """Reload all modules.

    :param name: The name of the submodule to reload only or empty to
                 reload the entire package.
    :type name: str
    """
    path = os.path.dirname(__file__)
    base = os.path.dirname(path)
    if len(name):
        path = os.path.join(path, name)

    for dirPath, dirs, fileList in os.walk(path):
        # Get the folder name from the current path.
        dirName = os.path.basename(dirPath)
        if dirName not in ["__pycache__"]:
            # Build the module name from the current path and strip away
            # the base path.
            # Replace the path separators with periods.
            modName = dirPath.replace(base, "").lstrip(os.sep).replace(os.sep, ".")
            for fileItem in fileList:
                if fileItem.endswith(".py"):
                    # Reload the package.
                    if fileItem == "__init__.py":
                        moduleName = modName
                    # Reload the module.
                    else:
                        moduleName = ".".join([modName, fileItem[:-3]])
                    try:
                        module = __import__(moduleName, fromlist=[""])
                        importlib.reload(module)
                        print("Reloading module: {}".format(moduleName))
                    except Exception as exception:
                        print(str(exception))


# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------

def logEnabled():
    """Return if logging is enabled when developer mode is active.

    :return: True, if logging is enabled.
    :rtype: bool
    """
    return preferences.getPreferences().developerMode and preferences.getPreferences().logData


def log(message):
    """Write to the given message to the logger.

    :param message: The message to log.
    :type message: str
    """
    if logEnabled():
        print(message)


# ----------------------------------------------------------------------
# Stats
# ----------------------------------------------------------------------

def countLines():
    """Print statistics about all files contained in the package
    regarding lines and code lines.
    """
    print("{:>10} |{:>10} |{:>10} |{:>10} |{:>10} | {:<20}".format("Lines", "Code", "%", "Total Code", "All", "File"))
    print("{:->11}|{:->11}|{:->11}|{:->11}|{:->11}|{:->20}".format("", "", "", "", "", ""))

    numLines = 0
    allLines = 0
    for root, dirs, fileList in os.walk(os.path.dirname(__file__)):
        for fileItem in fileList:
            if fileItem.endswith(".py"):
                filePath = "{}/{}".format(root, fileItem)
                with open(filePath, "r") as fileObj:
                    data = fileObj.readlines()
                    if len(data):
                        codeLines = _numCodeLines(data)
                        numLines += codeLines
                        allLines += len(data)
                        print("{:>10} |{:>10} |{:>10} |{:>10} |{:>10} | {:<20}".format(len(data),
                                                                                       codeLines,
                                                                                       int((float(codeLines)/len(data))*100.0),
                                                                                       numLines,
                                                                                       allLines,
                                                                                       "{}/{}".format(os.path.basename(root), fileItem)))


def _numCodeLines(data):
    """Return the number of code lines contained in the given file
    data.

    :param data: The content of the file to inspect.
    :type data: list(str)

    :return: The number of code lines without comments.
    :rtype: int
    """
    startDoc = False
    add = True
    numLines = 0
    for i in range(len(data)):
        if not startDoc:
            add = True
        line = data[i].lstrip(" ").lstrip("\n")
        if line.startswith("#") or not len(line):
            add = False
        elif '"""' in line or "'''" in line:
            add = False
            if startDoc or line.count('"""') == 2 or line.count("'''") == 2:
                startDoc = False
            else:
                startDoc = True
        if add:
            numLines += 1
    return numLines
