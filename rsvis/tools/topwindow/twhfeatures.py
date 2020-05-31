# ===========================================================================
#   twhfeatures.py ----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import settingsbox
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
        self._slider_hist_column = 3
        super(TWHFeatures, self).set_canvas(img, **kwargs)
        self._canvas.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=N+S+W+E)
        self._canvas_hist.grid(row=0, column=2, rowspan=2, columnspan=1, sticky=N+S+W+E)

        self._sbox_shi = settingsbox.SettingsBox(self, sbox=[["maxCorners", "qualityLevel", "minDistance", "blockSize", "k"], [50, 0.01, 3, 3, 0.04], ["int", "float", "float", "int", "float"]], func=self.create_shi, button="Shi")
        self._sbox_shi.grid(row=2, column=0, rowspan=6, sticky=W+E)
    
        self._sbox_star = settingsbox.SettingsBox(self, sbox=[["maxSize", "responseThreshold", "lineThresholdProjected", "lineThresholdBinarized", "suppressNonmaxSize"], [40, 30, 10, 8, 5], ["int", "int", "int", "int", "int"]], func=self.create_star, button="STAR")
        self._sbox_star.grid(row=2, column=1, rowspan=6, sticky=W+E)

        self._sbox_sift = settingsbox.SettingsBox(self, sbox=[["nfeatures", "nOctaveLayers", "contrastThreshold", "edgeThreshold", "sigma"], [0, 3, 0.04, 10, 1.6], ["int", "int", "float", "int", "float"]], func=self.create_sift, button="SIFT")
        self._sbox_sift.grid(row=2, column=2, rowspan=6, sticky=W+E)

        self._button_quit.grid(row=8, column=0, columnspan=4, sticky=W+E)

    # https://docs.opencv.org/3.4/d3/df6/namespacecv_1_1xfeatures2d.html

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_shi(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html
        grayimg = imgtools.get_gray_image(self._img).astype(np.float32)
        corners = np.int0(cv2.goodFeaturesToTrack(grayimg,**self._sbox_shi.get_dict()))
        img = imgtools.zeros_from_shape(self._img.shape[0:2], dtype=np.uint8)
        for c in corners:
            x, y = c.ravel()
            cv2.circle(img, (x,y), 3, 255, 2)
        self.get_obj().set_mask(imgtools.img_to_bool(img), color=[100,200,50])
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_sift(self, event=None, **kwargs):
        # https://docs.opencv.org/4.3.0/d5/d3c/classcv_1_1xfeatures2d_1_1SIFT.html
        self.create_keypoints( cv2.xfeatures2d.SIFT_create(**self._sbox_sift.get_dict()))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_star(self, event=None, **kwargs):
        # https://docs.opencv.org/3.4/dd/d39/classcv_1_1xfeatures2d_1_1StarDetector.html#a9f1ed97bd2b42e30fc0fb1355ad262d3
        self.create_keypoints(cv2.xfeatures2d.StarDetector_create(**self._sbox_star.get_dict()))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_keypoints(self, model, color=[100,200,50]):
        kp = model.detect(imgtools.get_gray_image(self._img), None)
        img = imgtools.zeros_from_shape(self._img.shape, dtype=np.uint8)
        img = imgtools.get_gray_image(cv2.drawKeypoints(img, kp, outImage=None))
        self.get_obj().set_mask(imgtools.img_to_bool(img), color=color)
        self.set_img()