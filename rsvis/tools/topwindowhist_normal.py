# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.settingsbox
import rsvis.tools.topwindowhist

import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindowHistNormal(rsvis.tools.topwindowhist.TopWindowHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            param,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TopWindowHistNormal, self).__init__(parent, **kwargs)
        
        self._height = Height(param, logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TopWindowHistNormal, self).set_canvas(img, **kwargs)

        self.columnconfigure(1, weight=1)

        self._canvas_hist.grid(row=0, column=1, columnspan=3, sticky=N+S+W+E)
        self._button.grid(row=3, column=0, columnspan=2)

        self._slider_mean.grid(row=1, column=1, columnspan=2, sticky=W+E)
        self._slider_std.grid(row=1, column=3, sticky=W+E)

        self._factor = 1.0
        self._sbox_factor = rsvis.tools.settingsbox.SettingsBox(self, ["Height factor"], self.update_sbox_factor, default=[self._factor])
        self._sbox_factor.grid(row=2, column=1, sticky=W+E)

        self._button_normal = ttk.Button(self, text="Open", 
            command=self.open_normal_cloud)
        self._button_normal.grid(row=2, column=2)

        self._button_normal = ttk.Button(self, text="Normal", 
            command=self.set_normal_img)
        self._button_normal.grid(row=2, column=3)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_factor(self, event):
        self._factor = self._sbox_factor.get_entry()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_normal_img(self):
        self._height.set_level()
        self.get_obj().set_img(self._height.get_normal_img(self.get_obj().get_img_from_spec("height"), factor=self._sbox_factor.get_entry()))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud(self):
        self._height.set_level()
        self._height.open("pointcloud", [self.get_obj().get_img_from_spec("height"), self.get_obj().get_img(), []], factor=self._sbox_factor.get_entry())