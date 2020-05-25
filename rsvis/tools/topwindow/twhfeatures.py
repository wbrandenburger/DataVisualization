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
        self._slider_hist_column = 4
        super(TWHFeatures, self).set_canvas(img, **kwargs)
        self._canvas.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=N+S+W+E)
        self._canvas_hist.grid(row=0, column=2, rowspan=2, columnspan=2, sticky=N+S+W+E)

        self._sbox_harris = rsvis.tools.settingsbox.SettingsBox(self, sbox=[["blockSize", "ksize", "k"], [2, 3, 0.04], ["int", "int", "float"]], func=self.create_harris, button="Harris")
        self._sbox_harris.grid(row=2, column=0, rowspan=4, sticky=W+E)

        self._sbox_shi = rsvis.tools.settingsbox.SettingsBox(self, sbox=[["maxCorners", "qualityLevel", "minDistance", "blockSize", "k"], [50, 0.01, 3, 3, 0.04], ["int", "float", "float", "int", "float"]], func=self.create_shi, button="Shi")
        self._sbox_shi.grid(row=2, column=1, rowspan=6, sticky=W+E)
    
        self._sbox_star = rsvis.tools.settingsbox.SettingsBox(self, sbox=[["maxSize", "responseThreshold", "lineThresholdProjected", "lineThresholdBinarized", "suppressNonmaxSize"], [40, 30, 10, 8, 5], ["int", "int", "int", "int", "int"]], func=self.create_star, button="STAR")
        self._sbox_star.grid(row=2, column=2, rowspan=6, sticky=W+E)

        self._sbox_sift = rsvis.tools.settingsbox.SettingsBox(self, sbox=[["nfeatures", "nOctaveLayers", "contrastThreshold", "edgeThreshold", "sigma"], [0, 3, 0.04, 10, 1.6], ["int", "int", "float", "int", "float"]], func=self.create_sift, button="SIFT")
        self._sbox_sift.grid(row=2, column=3, rowspan=6, sticky=W+E)

        self._button_quit.grid(row=8, column=0, columnspan=5, sticky=W+E)

    # https://docs.opencv.org/3.4/d3/df6/namespacecv_1_1xfeatures2d.html

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_harris(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
        grayimg = imgbasictools.get_gray_image(self._img).astype(np.float32)
        dstimg = cv2.cornerHarris(grayimg, **self._sbox_harris.get_dict())
        dstimg = cv2.dilate(dstimg, None)
        img = self._img.copy()
        img[dstimg>0.01*dstimg.max()]=[0,0,255]

        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_shi(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html
        grayimg = imgbasictools.get_gray_image(self._img).astype(np.float32)
        corners = cv2.goodFeaturesToTrack(grayimg,**self._sbox_shi.get_dict())
        corners = np.int0(corners)

        img = self._img.copy()
        for i in corners:
            x,y = i.ravel()
            cv2.circle(img, (x,y), 1, 255, -1)

        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_sift(self, event=None, **kwargs):
        # https://docs.opencv.org/4.3.0/d5/d3c/classcv_1_1xfeatures2d_1_1SIFT.html
        gray = imgbasictools.get_gray_image(self._img)
        sift = cv2.xfeatures2d.SIFT_create(**self._sbox_sift.get_dict())
        kp = sift.detect(gray, None)
        img = cv2.drawKeypoints(self._img, kp, outImage=None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_star(self, event=None, **kwargs):
        # https://docs.opencv.org/3.4/dd/d39/classcv_1_1xfeatures2d_1_1StarDetector.html#a9f1ed97bd2b42e30fc0fb1355ad262d3
        gray = imgbasictools.get_gray_image(self._img)
        star = cv2.xfeatures2d.StarDetector_create(**self._sbox_star.get_dict())
        kp = star.detect(gray, None)
        img = cv2.drawKeypoints(self._img, kp, outImage=None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self._canvas.set_img(img)        