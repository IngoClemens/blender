# <pep8 compliant>

import importlib
import os


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
