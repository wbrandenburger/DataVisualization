# ===========================================================================
#   json.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import logging
import os
import json
import numpy as np
json.encoder.FLOAT_REPR = lambda o: format(o, '.4f' )

#   settings ----------------------------------------------------------------
# ---------------------------------------------------------------------------
logger = logging.getLogger("json")

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class PrettyFloat(float):
    def __call__(self, obj):
        return '{:.4f}'.format(obj)

prettyfloat = PrettyFloat()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def pretty_floats(obj):
    if isinstance(obj, float):
        return prettyfloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))
    return obj

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def data_to_json(path, data):
    """
    Save data to json at path outpath

    :param json_path: Path to a json file
    :type  json_path: str

    :param data: Data in a dictionary
    :type  data: dict
    """
    with open(path, 'w+') as f:
        json.dump(
            pretty_floats(data),
            f,
            #allow_unicode=True/False),
            sort_keys=False
        )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def json_to_data(path, raise_exception=False):
    """
    Convert a json file into a dictionary using the json module.

    :param path: Path to a json file
    :type  path: str

    :return:: Dictionary containing the info of the json file
    :rtype:  dict

    :raises ValueError: If a json parsing error happens
    """
    if os.path.exists(path):
        return file_to_data(path, raise_exception=raise_exception)
    else:
        return string_to_data(path, raise_exception=raise_exception)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def file_to_data(path, raise_exception=False):
    """
    Convert a json file into a dictionary using the json module.

    :param path: Path to a json file
    :type  path: str

    :return:: Dictionary containing the info of the json file
    :rtype:  dict

    :raises ValueError: If a json parsing error happens
    """
    with open(path) as f:
        try:
            data = json.load(f)
        except Exception as e:
            if raise_exception:
                raise ValueError(e)
            logger.error("json syntax error: \n\n{0}".format(e))
            return dict()
        else:
            return data

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def string_to_data(string, raise_exception=False):
    """
    Convert a json string into a dictionary using the json module.

    :param string: string representation of dictionary
    :type string: str

    :return:: Dictionary containing the info of the string
    :rtype:  dict

    :raises ValueError: If a json parsing error happens
    """
    try:
        data = json.loads(string)
    except Exception as e:
        if raise_exception:
            raise ValueError(e)
        logger.error("json syntax error: \n\n{0}".format(e))
        return dict()
    else:
        return data