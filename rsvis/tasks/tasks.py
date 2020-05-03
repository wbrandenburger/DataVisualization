# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.config.settings
import rsvis.utils.format
import rsvis.utils.general as glu

import rsvis.tools.rsshow

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    """Default task of set 'test'"""
    _logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow(setting="training"):
    rsvis.tools.rsshow.rsshow(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_io"],
        param_log=glu.get_value(
            rsvis.config.settings._SETTINGS,"param_log", dict()),
        param_show=glu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict()),
        param_classes=glu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_cloud=glu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict( )),
        param_obj=glu.get_value(
            rsvis.config.settings._SETTINGS,"param_obj", dict())             
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_settings():
    """Print the user settings"""
    
    # print user's defined settings
    _logger.info("Print user's defined settings")
    rsvis.utils.format.print_data(rsvis.config.settings._SETTINGS)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_data():
    """Print the user data"""
    
    # print user's defined data
    _logger.info("Print user's defined data")
    rsvis.utils.format.print_data(rsvis.config.settings.get_data_dict())