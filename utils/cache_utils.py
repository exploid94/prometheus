"""Functions to help deal with file paths and caching for this toolset."""

import os 
import shutil
import tempfile
import time
from datetime import date


def initRootCacheFolder():
    """Create the root folder to store cache files related to the Prometheus Tools.
    
    :return: The root prometheus temp folder. Should be at C:/Users/user/AppData/Local/Temp/PrometheusCache
    :rtype: str
    """
    # create the prometheus root folder if it doesn't already exist
    temp_root = tempfile.gettempdir()
    temp_folder = os.path.join(temp_root, "PrometheusCache")
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    
    # assign this location to an environment variable for the session
    os.environ["PROMETHEUS_ROOT_CACHE"] = temp_folder
    return temp_folder


def initScriptsCacheFolder():
    """Create the scripts folder to store cache files of the scripts in the Prometheus TreeItem.
    
    :return: The prometheus scripts temp folder. C:/Users/user/AppData/Local/Temp/PrometheusCache/PrometheusScriptsCache
    :rtype: str
    """
    root_folder = initRootCacheFolder()
    temp_folder = os.path.join(root_folder, "PrometheusScriptsCache")
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    
    # assign this location to an environment variable for the session
    os.environ["PROMETHEUS_SCRIPTS_CACHE"] = temp_folder
    return temp_folder


def initDateFolder(directory, env_var):
    """Create a temporary date folder at the given directory.

    :param directory: The directory to create a new folder at.
    :type directory: str 

    :param env_var: The name of the environment variable to use to store this path.
    :type env_var: str 
    
    :return: The date folder created.
    :rtype: str
    """
    # if the env var is there but the folder is not, recreate the folder
    if env_var in os.environ:
        if not os.path.exists(os.environ[env_var]):
            os.mkdir(os.environ[env_var])

    elif os.path.exists(directory):
        # create the temp date folder
        today = date.today()
        time_stamp = today.strftime("%b-%d-%Y")
        date_folder = tempfile.mkdtemp(prefix="{}_".format(time_stamp), dir=directory)

        # assign the date folder to the env var 
        os.environ[env_var] = date_folder

        return date_folder


def deleteDirectory(directory):
    """Delete the folder at the given directory.
    
    :param directory: The directory to delete.
    :type directory: str
    """
    try:
        shutil.rmtree(directory)
    except OSError as err:
        raise err


def flushRootCache(delete_env=True):
    """Delete the root cache folder and it's children.
    
    :param delete_env: Delete the environment variable if set to True. (True)
    :type delete_env: bool
    """
    temp_folder = initRootCacheFolder()
    deleteDirectory(temp_folder)
    if delete_env:
        del os.environ["PROMETHEUS_ROOT_CACHE"]


def flushScriptsCache(delete_env=True):
    """Delete the scripts cache folder and it's children.
    
    :param delete_env: Delete the environment variable if set to True. (True)
    :type delete_env: bool
    """
    temp_folder = initScriptsCacheFolder()
    deleteDirectory(temp_folder)
    if delete_env:
        del os.environ["PROMETHEUS_SCRIPTS_CACHE"]


def flushOutdatedCache(directory):
    """Delete any folder that was created longer than 5 days ago at the given directory.

    :param directory: The directory to delete.
    :type directory: str 
    """
    for root, dirs, files in os.walk(directory):
        folder_path = os.path.join(directory, root)
        if os.stat(folder_path).st_mtime < time.time() - 5 * 86400:
            deleteDirectory(folder_path)


def flushCachedChildren(directory):
    """Delete all folder children of the given directory but no the directory itself.

    :param directory: The directory to remove the children of.
    :type directory: str 
    """
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            folder_path = os.path.join(directory, root, dir)
            deleteDirectory(folder_path)


def writeTempFile(directory, prefix, extension, data):
    """Write a temp file with the given data at the directory.

    :param directory: Folder path to save the file at.
    :type directory: str 
    
    :param prefix: The prefix to use for naming the file. 
    :type prefix: str

    :param extension: The extension (file type) to save the file as. 
    :type extension: str

    :param data: The data to be saved.
    :type data: object

    :return: The saved file path.
    :rtype: str
    """
    new_file, file_name = tempfile.mkstemp(suffix=".py", prefix="{}_".format(prefix), dir=directory)
    os.write(new_file, data)
    os.close(new_file)
    return file_name.replace("\\", "/")


def updateTempFile(filepath, data):
    """Update the temp file with the given data.

    :param filepath: File path of the temp file.
    :type filepath: str 
    
    :param data: The data to update the file with. 
    :type data: object

    :return: The updated file path.
    :rtype: str
    """
    with open(filepath, "w+") as outfile:
        outfile.truncate(0)
        outfile.write(data)
    return filepath


def renameCacheFile(filepath, new_name):
    """Rename the cache file to the new name.

    :param filepath: File path of the temp file.
    :type filepath: str 
    
    :param new_name: The new name of the file, excluding random characters. 
    :type new_name: str

    :return: The new renamed file path.
    :rtype: str
    """
    directory = os.path.dirname(filepath)
    old_name = os.path.basename(filepath)
    old_chars = old_name.split("__")[-1]
    new_name_with_chars = "{}__{}".format(new_name, old_chars)
    new_filepath = os.path.join(directory, new_name_with_chars)
    os.rename(filepath, new_filepath)
    return new_filepath
