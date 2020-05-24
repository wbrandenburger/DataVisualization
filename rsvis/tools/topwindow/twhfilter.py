# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
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
        self._slider_hist_column = 4
        super(TWHFilter, self).set_canvas(img, **kwargs)

        self._canvas.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=N+S+W+E)        
        self._canvas_hist.grid(row=0, column=2, rowspan=2, columnspan=2, sticky=N+S+W+E)

        self._param_image_blur = "Average"
        self._cbox_image_blur = rsvis.tools.combobox.ComboBox(self, "Blurring",  ["Average", "Gaussian", "Median"], self.update_cbox_image_blur, default=0) # , "Bilateral Filtering"
        self._cbox_image_blur.grid(row=2, column=0, columnspan=2, sticky=W+E)

        self._param_kernel_size = 5
        self._sbox_kernel_size = rsvis.tools.settingsbox.SettingsBox(self, ["Kernel Size"], self.update_sbox_kernel_size, default=[self._param_kernel_size])
        self._sbox_kernel_size.grid(row=3, column=0, sticky=W+E)

        self._param_kernel_std = 1.0
        self._sbox_kernel_std = rsvis.tools.settingsbox.SettingsBox(self, ["Kernel Std"], self.update_sbox_kernel_std, default=[self._param_kernel_std])
        self._sbox_kernel_std.grid(row=3, column=1, sticky=W+E)

        self._button_image_blur = ttk.Button(self, text="Blur Image", 
            command=self.set_image_blur)
        self._button_image_blur.grid(row=2, column=3, columnspan=1, sticky=W)

        self._button_quit.grid(row=3, column=3, columnspan=1, sticky=W)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_cbox_image_blur(self, event=None):
        self._param_image_blur = self._cbox_image_blur.get()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_kernel_size(self, event=None):
        self._param_kernel_size = int(self._sbox_kernel_size.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_kernel_std(self, event=None):
        self._param_kernel_std = float(self._sbox_kernel_std.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_image_blur(self):
        self.update_cbox_image_blur()
        self.update_sbox_kernel_size()
        self.update_sbox_kernel_std()
        self._logger("[CMP] Model: {}".format(self._param_image_blur))
  
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_image_blur(self):
        self.update_image_blur()
        
        self._param_border_type = cv2.BORDER_REFLECT
        
        img = self.get_obj().get_img(show=True)
        if self._param_image_blur == "Average":
            img = cv2.boxFilter(img, -1, (self._param_kernel_size, self._param_kernel_size), normalize=True, borderType=self._param_border_type)
        elif self._param_image_blur == "Gaussian":
            img = cv2.GaussianBlur(img, (self._param_kernel_size, self._param_kernel_size), self._param_kernel_std, borderType=self._param_border_type)
        elif self._param_image_blur == "Median":
            img = cv2.medianBlur(img, self._param_kernel_size)
        # elif self._param_image_blur == "Bilateral Filtering":
        #     imf = cv2.bilateralFilter(img, 9, 50, 50)
        self.get_obj().set_img(img)
        self.set_img()