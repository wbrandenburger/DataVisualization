# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.utils.format
import rsvis.tools.rsshow
import rsvis.tools.lecture
import rsvis.utils.regex

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def main():
    
    test_user_data()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_rsshow():
    rsvis.tools.rsshow.rsshow(
        rsvis.config.settings._DATA, 
        rsvis.config.settings._SETTINGS["data-tensor-types"],
        rsvis.config.settings._SETTINGS["io"]["dest-dir"],
        rsvis.config.settings._SETTINGS["io"]["dest-basename"],
        rsvis.config.settings._SETTINGS["io"]["regex"],
        labels=rsvis.config.settings._SETTINGS["label"],
        resize=rsvis.config.settings._SETTINGS["resize"]
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_code():
    rsvis.tools.rsshow.test_code( rsvis.config.settings._DATA, 
        rsvis.config.settings._SETTINGS["data-tensor-types"])

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_lecture():
    rsvis.tools.lecture.test(
        rsvis.config.settings._DATA, 
        rsvis.config.settings._SETTINGS["data-tensor-types"], 
        cat=rsvis.config.settings._SETTINGS["label"],
        resize=rsvis.config.settings._SETTINGS["resize"]
    )
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_user_settings():
    """Print the user settings"""
    
    # print user's defined settings
    rsvis.__init__._logger.info("Print user's defined settings")
    rsvis.utils.format.print_data(rsvis.config.settings._SETTINGS)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test_user_data():
    """Print the user data"""
    
    # print user's defined data
    rsvis.__init__._logger.info("Print user's defined data")
    rsvis.utils.format.print_data(rsvis.config.settings._DATA)