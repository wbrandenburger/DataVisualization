# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.config.settings
import rsvis.utils.general as gu

import rsvis.tasks.rsshow
import rsvis.tasks.rsexp_aux
import rsvis.tasks.rsexp_gaofen_to_agan
import rsvis.tasks.rsexp_agan_valid
import rsvis.tasks.rsexp_uncty


import rsvis.tasks.rsexpseg
import rsvis.tasks.rsexpsegthresh

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    """Default task of set 'test'"""
    _logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow(setting="training"):
    param_obj=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_obj", dict())
    if param_obj:
        param_obj = param_obj[setting] 
        
    rsvis.tasks.rsshow.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_vis=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_vis", dict()),
        param_obj=param_obj,            
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())     
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_auxiliary_data(setting="training"):
    rsvis.tasks.rsexp_aux.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_gaofen_data(setting="training"):
    rsvis.tasks.rsexp_gaofen_to_agan.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_gaofen_valid(setting="training"):
    rsvis.tasks.rsexp_agan_valid.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
    )


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_uncty(setting="training"):
    rsvis.tasks.rsexp_uncty.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_cloud=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_cloud", dict()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_segmentation(setting="training"):
    rsvis.tasks.rsexpseg.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_segmentation_threshold(setting="training"):
    rsvis.tasks.rsexpsegthresh.run(
        rsvis.config.settings.get_data(setting),
        rsvis.config.settings._SETTINGS["param_specs"],
        rsvis.config.settings._SETTINGS["param_in"], 
        param_out=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_out", dict()), 
        param_classes=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_classes", list()),
        param_exp=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_exp", list()),
        param_show=gu.get_value(
            rsvis.config.settings._SETTINGS,"param_show", dict())   
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