# ===========================================================================
#   imgiogui.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.tools.widgets import csbox

import rsvis.utils.general as gu
from rsvis.utils import imgio 

import os
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgIOGUI(csbox.CSBox):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            bbox=list(),
            **kwargs
        ):
        super(ImgIOGUI, self).__init__(
            parent, 
            sbox=[["path_dir", "path_name", "ext"], [os.environ.get("TEMP"), "{}", ".tif"], ["str", "str", "str"]], 
            **kwargs
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write(self, path, img, log_str=None, logger=None, log=".log", **kwargs):
        io = gu.PathCreator(**self.get_dict())

        imgio.write_image(io(path, **kwargs), img, logger=logger)

        if log_str is not None:
            imgio.write_log(io(path, ext=log, **kwargs), log_str, logger=logger)

