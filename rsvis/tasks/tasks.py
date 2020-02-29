# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.utils.format
import rsvis.tools.rsshow

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    task_print_user_settings()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
get_value = lambda obj, key, default: obj[key] if key in obj.keys() else default

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow(setting):
    try:
        rsvis.tools.rsshow.rsshow(
            rsvis.config.settings.get_data(setting),
            rsvis.config.settings._SETTINGS["data-tensor-types"],
            **rsvis.config.settings._SETTINGS["output"],
            param_label=get_value(rsvis.config.settings._SETTINGS,"param_label", dict()),
            param_msi=get_value(rsvis.config.settings._SETTINGS,"param_msi", list()),
            scale=get_value(rsvis.config.settings._SETTINGS,"scale", 100),
            param_dist=get_value(rsvis.config.settings._SETTINGS,"param_dist", dict())
        )
    except KeyError:
        pass    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow_training():
    task_rsshow("training")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow_test():
    task_rsshow("test")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_settings():
    """Print the user settings"""
    
    # print user's defined settings
    rsvis.__init__._logger.info("Print user's defined settings")
    rsvis.utils.format.print_data(rsvis.config.settings._SETTINGS)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_data():
    """Print the user data"""
    
    # print user's defined data
    rsvis.__init__._logger.info("Print user's defined data")
    rsvis.utils.format.print_data(rsvis.config.settings.get_data_dict())