# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.combobox
import rsvis.tools.settingsbox
import rsvis.tools.topwindowhist

import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindowHistFilter(rsvis.tools.topwindowhist.TopWindowHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TopWindowHistFilter, self).__init__(parent, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        self._slider_hist_column = 3
        super(TopWindowHistFilter, self).set_canvas(img, **kwargs)
        
        self._canvas_hist.grid(row=0, column=1, rowspan=2, columnspan=2, sticky=N+S+W+E)

        self._param_image_blur = "Average"
        self._cbox_image_blur = rsvis.tools.combobox.ComboBox(self, "Blurring",  ["Average", "Gaussian", "Median", "Bilateral Filtering"], self.update_cbox_image_blur, default=0)
        self._cbox_image_blur.grid(row=2, column=0, columnspan=1, sticky=W+E)

        self._button_image_blur = ttk.Button(self, text="Blur Image", 
            command=self.set_image_blur)
        self._button_image_blur.grid(row=2, column=1, columnspan=1)

        self._button_quit.grid(row=2, column=2, columnspan=1)


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_cbox_image_blur(self, event=None):
        self._param_image_blur = self._cbox_image_blur.get()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_image_blur(self):
        self.update_cbox_image_blur()

        self._logger("[CMP] Model: {}".format(self._param_image_blur))
  
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_image_blur(self):
        self.update_image_blur()
        self.get_obj().set_img(self.get_obj().get_img(show=True))
        self.set_img()