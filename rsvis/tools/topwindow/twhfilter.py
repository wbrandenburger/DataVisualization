# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox
from rsvis.tools.topwindow import twhist

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHFilter(twhist.TWHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHFilter, self).__init__(parent, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TWHFilter, self).set_canvas(img, **kwargs)

        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Gaussian", "Median"]], ["Median"], ["str"]], sbox=[["Kernel Size", "Kernel Std"], [5, 1.0, True, 1.0], ["int", "float"]])
        self._csbox_blur.grid(row=2, column=0, rowspan=3, sticky=N+W+E)

        self._button_normal = buttonbox.ButtonBox(self, bbox=[["Blur Image"], [self.set_image_blur]])
        self._button_normal.grid(row=2, column=1, rowspan=1, sticky=N+W+E)

        self._button_quit.grid(row=6, column=0, columnspan=3, sticky=W+E)
  
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_image_blur(self):
        param = self._csbox_blur.get_dict()
        param["BorderType"] = cv2.BORDER_REFLECT
        
        img = self.get_obj().get_img(show=True)
        kernel_size = (param["Kernel Size"], param["Kernel Size"])
        if param["Model"] == "Average":
            img = cv2.boxFilter(img, -1, kernel_size, normalize=True, borderType=param["BorderType"])
        elif param["Model"] == "Gaussian":
            img = cv2.GaussianBlur(img, kernel_size, param["Kernel Std"], borderType=param["BorderType"])
        elif param["Model"] == "Median":
            img = cv2.medianBlur(img, kernel_size[0])
        # elif self._param_image_blur == "Bilateral Filtering":
        #     imf = cv2.bilateralFilter(img, 9, 50, 50)
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()