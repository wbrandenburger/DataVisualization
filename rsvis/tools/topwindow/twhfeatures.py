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

        self._button_fast = ttk.Button(self, text="FAST Algorithm for Corner Detection", 
            command=self.create_fast)
        self._button_fast.grid(row=2, column=0, columnspan=1, sticky=E+W)

        self._button_harris_corner = ttk.Button(self, text="Harris Corner Detection", 
            command=self.create_harris_corner)
        self._button_harris_corner.grid(row=3, column=0, columnspan=1, sticky=E+W)

        self._button_shi_tomasi_corner = ttk.Button(self, text="Shi-Tomasi Corner Detection", 
            command=self.create_shi_tomasi_corner)
        self._button_shi_tomasi_corner.grid(row=4, column=0, columnspan=1, sticky=E+W)

        self._button_sift = ttk.Button(self, text="Scale-Invariant Feature Transform", 
            command=self.create_sift)
        self._button_sift.grid(row=5, column=0, columnspan=1, sticky=E+W)

        self._button_quit.grid(row=2, column=1, columnspan=1, sticky=E+W)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_harris_corner(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_features_harris/py_features_harris.html
        grayimg = imgbasictools.get_gray_image(self._img).astype(np.float32)

        # find Harris corners
        dstimg = cv2.cornerHarris(grayimg, 2, 3, 0.04)
        dstimg = cv2.dilate(dstimg, None)

        # Threshold for an optimal value, it may vary depending on the image.
        img = self._img.copy()
        img[dstimg>0.01*dstimg.max()]=[0,0,255]

        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_shi_tomasi_corner(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html
        grayimg = imgbasictools.get_gray_image(self._img).astype(np.float32)

        # find Harris corners
        corners = cv2.goodFeaturesToTrack(grayimg,50,0.01,3)
        corners = np.int0(corners)

        img = self._img.copy()
        for i in corners:
            x,y = i.ravel()
            cv2.circle(img, (x,y), 3, 255, -1)

        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_sift(self, event=None, **kwargs):
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_brief/py_brief.html
        gray= cv2.cvtColor(self._img,cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create(contrastThreshold = 0.1,edgeThreshold=20, sigma=2.0)
        kp = sift.detect(gray,None)
        #kp = sift.detect(gray,None)
        img = cv2.drawKeypoints(self._img, kp, outImage=None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        self._canvas.set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_fast(self, event=None, **kwargs):
        gray = imgbasictools.get_gray_image(self._img)

        # Initiate FAST object with default values
        fast = cv2.FastFeatureDetector_create()

        # find and draw the keypoints
        kp = fast.detect(gray, None)
        img = cv2.drawKeypoints(self._img, kp, outImage=None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        self._canvas.set_img(img)        