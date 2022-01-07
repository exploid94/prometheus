"""Helper functions to deal with file paths."""

import os
import getpass
import platform


def getBaseCodeLibrary():
    """Return the base code library folder.
    
    :return: The path that the library is at. If it doesnt exist, returns NameError.
    :rtype: str
    """
    # get the operating system type to handle the initial library path
    # TODO check if this works across all platforms
    # TODO just set this path to be a defualt path
    system = platform.system()
    if system == "Windows":
        path = "C:/prometheus/rigging/code_library"
    elif system == "Linux":
        path = "/c/prometheus/rigging/code_library"
    elif system == "Darwin":
        path = "/Volumes/c/prometheus/rigging/code_library"

    if os.path.exists(path):
        return path
    else:
        raise NameError("Directory does NOT exist: {}".format(path))


def getUserCodeLibrary(user="default_user"):
    """Return the user folder under the code library.

    :param user: The name of the user to look for the folder of.
    :type user: str

    :return: The path that the user library is at.
    :rtype: str
    """
    path = os.path.join(getBaseCodeLibrary(), user).replace("\\", "/")
    if os.path.exists(path):
        return path
    else:
        return _createCodeLibrary(user)


def getUserScriptsLibrary(user="default_user"):
    """Return the user scripts folder under the code library.

    :param user: The name of the user to look for the folder of.
    :type user: str

    :return: The path that the user scripts folder is at.
    :rtype: str
    """
    path = os.path.join(getUserCodeLibrary(user), "scripts").replace("\\", "/")
    if os.path.exists(path):
        return path
    else:
        return _createDirectory(path)


def _createDirectory(path):
    """Create and return a new directory at a specific path.

    :param path: The folder path.
    :type path: str

    :return: The folder path.
    :rtype: str
    """
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def _createCodeLibrary(user):
    """Create a code library for a specific user.

    :param user: The username to create a folder for.
    :type user: str

    :return: The folder path created.
    :rtype: str
    """
    # create new user
    path = os.path.join(getBaseCodeLibrary(), user).replace("\\", "/")
    user_path = _createDirectory(path)
    
    # create new user/scripts
    path = os.path.join(user_path, "scripts").replace("\\", "/")
    scripts_path = _createDirectory(path)

    # create new user/shelves
    path = os.path.join(user_path, "shelves").replace("\\", "/")
    shelves_path = _createDirectory(path)

    return user_path
