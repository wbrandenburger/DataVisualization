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

        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Gaussian", "Median"]], ["Median"], ["str"]], sbox=[["Kernel Size", "Kernel Std"], [5, 1.0, True, 1.0], ["int", "float"]], bbox=[["Blur Image"], [self.set_image_blur]])
        self._csbox_blur.grid(row=2, column=0, rowspan=4, sticky=N+W+E)

        self._csbox_threshold = csbox.CSBox(self, cbox=[["adaptiveMethod"], [["Mean", "Gaussian"]], ["Gaussian"], ["str"]], sbox=[["blockSize", "C"], [5, 2], ["int", "int"]], bbox=[["Adaptive Thresholding"], [self.set_adaptive_thresholding]])
        self._csbox_threshold.grid(row=2, column=1, rowspan=3, sticky=N+W+E)

        self._slider_threshold = Scale(self, label="Threshold", from_=0, to=255, orient=HORIZONTAL, command=self.set_threshold, resolution=2) 
        self._slider_threshold.set(0)
        self._slider_threshold.grid(row=6, column=0, columnspan=3, sticky=W+E)

        self._button_quit.grid(row=7, column=0, columnspan=3, sticky=W+E)
  
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

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_threshold(self, event=None):
        param = self._slider_threshold.get()
        _, dst = cv2.threshold(imgbasictools.get_gray_image(self._img), param, 255, cv2.THRESH_BINARY)

        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_adaptive_thresholding(self, event=None):
        param = self._csbox_threshold.get_dict()
        if  param["adaptiveMethod"] == "Mean":
            param_method = cv2.ADAPTIVE_THRESH_MEAN_C
        elif param["adaptiveMethod"] == "Gaussian":
            param_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        dst	= cv2.adaptiveThreshold(imgbasictools.get_gray_image(self._img), 255,  param_method, cv2.THRESH_BINARY, param["blockSize"], param["C"])

        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_threshold_mask(self, dst):      
        dst = imgtools.img_to_bool(dst)
        dst_inv = imgtools.invert_bool_img(dst)

        mask = self.get_obj().get_mask(index=0)
        mask_list = [mask] if isinstance(mask, np.ndarray) else list()
        if isinstance(mask, np.ndarray):
            mask_list.extend([np.where(np.logical_and(dst_inv==1, mask!=0), 1, 0)]) #, np.where(np.logical_and(dst==1, mask!=0), 1, 0)]) 
        # else: 
        #     mask_list.extend([dst_inv])

            mask_color = [[0, 0, 0]] if isinstance(mask, np.ndarray) else list()
            mask_color.extend([[0, 0, 255]])#, [0,255,0]])
            
            mask_alpha = [200] if isinstance(mask, np.ndarray) else list()
            mask_alpha.extend([75])#, 75])

            mask_invert = [True] if isinstance(mask, np.ndarray) else list()
            mask_invert.extend([False])#, False])
            
            self.get_obj().set_mask(mask=mask_list, color=mask_color, invert=mask_invert, alpha=mask_alpha, show=True)

