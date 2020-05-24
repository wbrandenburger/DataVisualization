# ===========================================================================
#   twhfeatures.py ----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.combobox
import rsvis.tools.settingsbox
from rsvis.tools.topwindow import twhist

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHFeatures(twhist.TWHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHFeatures, self).__init__(parent, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TWHFeatures, self).set_canvas(img, **kwargs)

        # self._button_hist_proj = ttk.Button(self, text="Histogram Mask Image", 
        #     command=self.update_proj_hist)
        # self._button_hist_proj.grid(row=2, column=0, columnspan=1, sticky=E+W)

        # self._button_quit.grid(row=2, column=1, columnspan=1, sticky=E+W)