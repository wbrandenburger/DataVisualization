# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox
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

        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Gaussian", "Median", "Bilateral Filtering"]], ["Median"], ["str"]], sbox=[["Kernel Size", "Sigma", "Diameter", "Sigma Color", "Sigma Space"], [5, 2.3, 7, 100, 500], ["int", "float", "int", "int", "int"]], bbox=[["Blur Image"], [self.get_image_blur]])
        self._csbox_blur.grid(row=2, column=0, rowspan=7, sticky=N+W+E)

        self._csbox_edges = csbox.CSBox(self, bbox=[["Get Edges"], [self.get_edges]], sbox=[["Threshold I", "Threshold II", "Aperture Size"], [50, 150, 3], ["int", "int", "int"]])
        self._csbox_edges.grid(row=9, column=0, rowspan=4, sticky=N+W+E)

        self._scbox_threshold = scalebox.ScaleBox(self, scbox=[["Thresh"], [[0, 255, 2, 0]], ["int"]],  orient=HORIZONTAL, func=self.set_simple_threshold, button="Simple Thresholding") 
        self._scbox_threshold.grid(row=2, column=1, rowspan=2, sticky=N+W+S+E)

        self._csbox_threshold = csbox.CSBox(self, cbox=[["adaptiveMethod"], [["Mean", "Gaussian"]], ["Gaussian"], ["str"]], sbox=[["blockSize", "C"], [5, 2], ["int", "int"]], bbox=[["Adaptive Thresholding"], [self.set_adaptive_thresholding]])
        self._csbox_threshold.grid(row=4, column=1, rowspan=3, sticky=N+W+S+E)

        self._button_quit.grid(row=13, column=0, columnspan=3, sticky=W+E)
  
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_image_blur(self):
        param = self._csbox_blur.get_dict()
        param["BorderType"] = cv2.BORDER_REFLECT
        
        img = self.get_obj().get_img(show=True)
        kernel_size = (param["Kernel Size"], param["Kernel Size"])
        if param["Model"] == "Average":
            img = cv2.boxFilter(img, -1, kernel_size, normalize=True, borderType=param["BorderType"])
        elif param["Model"] == "Gaussian":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
            img = cv2.GaussianBlur(img, kernel_size, param["Kernel Size"], borderType=param["BorderType"])
        elif param["Model"] == "Median":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9
            img = cv2.medianBlur(img, kernel_size[0])
        elif param["Model"] == "Bilateral Filtering":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga9d7064d478c95d60003cf839430737ed
            img = cv2.bilateralFilter(img, param["Diameter"], param["Sigma Color"], param["Sigma Space"])
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_simple_threshold(self, event=None, otsu=False):
        param = self._scbox_threshold.get_dict()
        thresh = cv2.THRESH_BINARY if param["Thresh"] else cv2.THRESH_BINARY + cv2.THRESH_OTSU
        
        ret, dst = cv2.threshold(imgtools.get_gray_image(self._img), param["Thresh"], 255, thresh)

        self._logger("Simple Thresholding with thresh: {}".format(ret))
        
        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_adaptive_thresholding(self, event=None):
        param = self._csbox_threshold.get_dict()
        if  param["adaptiveMethod"] == "Mean":
            param_method = cv2.ADAPTIVE_THRESH_MEAN_C
        elif param["adaptiveMethod"] == "Gaussian":
            param_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        dst	= cv2.adaptiveThreshold(imgtools.get_gray_image(self._img), 255,  param_method, cv2.THRESH_BINARY, param["blockSize"], param["C"])

        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_threshold_mask(self, dst):      
        dst = imgtools.img_to_bool(dst)
        dst_inv = imgtools.invert_bool_img(dst)

        mask = self.get_obj().get_mask(index=0)

        if not isinstance(mask, np.ndarray):
            mask = imgtools.zeros_from_shape(dst.shape, value=1, dtype=np.uint8)

        mask_list = [mask] if isinstance(mask, np.ndarray) else list()
        mask_list.extend([np.where(np.logical_and(dst_inv==1, mask!=0), 1, 0).astype(np.uint8)]) 

        mask_color = [[0, 0, 0]] if isinstance(mask, np.ndarray) else list()
        mask_color.extend([[255, 255, 0]])
        
        mask_alpha = [150] if isinstance(mask, np.ndarray) else list()
        mask_alpha.extend([75])

        mask_invert = [True] if isinstance(mask, np.ndarray) else list()
        mask_invert.extend([False])
        
        self.get_obj().set_mask(mask=mask_list, color=mask_color
        , invert=mask_invert, alpha=mask_alpha, show=True)
        self.update_hist()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_edges(self):
        param = self._csbox_edges.get_dict()

        img = self.get_obj().get_img()
        grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(grayimg, param["Threshold I"], param["Threshold II"], apertureSize=param["Aperture Size"])

        self.get_obj().set_img(edges, clear_mask=True)   