# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.config.settings
import rsvis.utils.format
import rsvis.utils.general as gu

import rsvis.rsshow.rsshow
import rsvis.lecture.rsshow

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    """Default task of set 'test'"""
    _logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow(setting="training"):
    rsvis.rsshow.rsshow.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict()),        
      
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_lecture(setting="training"):
    rsvis.lecture.rsshow.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_in=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_in", dict()),   
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),          
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict()),
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