"""Helper functions to save and load json files."""

import json
import os

import maya.cmds as cmds


def saveJson(filepath, data):
    """Save given data to a json file at the given filepath.

    :param filepath: Full file path to be saved.
    :type filepath: str 
    
    :param data: Saves this data to the json file.
    :type data: object

    :return: The saved file path.
    :rtype: str
    """
    # Write the json file with the list of dictionaries
    try:
        with open(filepath, 'w+') as outfile:
            json.dump(data, outfile)
        print ('File Saved:', filepath)
    except Exception:
        raise
    return filepath


def loadJson(filepath):
    """Load the json file.

    :param filepath: The name of the json file being saved.
    :type filepath: str 

    :return: The data within the json file.
    :rtype: object
    """
    # Load the selected file
    if os.path.exists(filepath):
        with open(filepath) as outfile:
            data = json.load(open(filepath))
    else:
        data = None
    return data


def saveAsJson(data):
    """Save the data to a prompted location.
    
    :param data: The data to be saved.
    :type data: object

    :return: The saved file path.
    :rtype: str
    """
    # saves a new file by iteration
    filepath = cmds.fileDialog2(fileFilter="JSON (*.json)")
    if filepath:
        return saveJson(filepath[0], data)


def loadAsJson():
    """Load the json file at a prompted location.

    :return: The data within the json file.
    :rtype: object
    """
    # Load the selected file
    filepath = cmds.fileDialog2(fileFilter="JSON (*.json)", fm=1)
    if filepath:
        return loadJson(filepath[0])
