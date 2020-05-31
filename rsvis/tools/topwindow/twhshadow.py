# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.shadow.shdwDetection as sd

from rsvis.tools.widgets import csbox, buttonbox, scalebox
from rsvis.tools.topwindow import twhfilter

from scipy.cluster.vq import vq, kmeans, kmeans2, whiten

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHShadow(twhfilter.TWHFilter):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHShadow, self).__init__(parent, **kwargs)

        self._centroids = list()
        

        #self._img_whiten = whiten(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TWHShadow, self).set_canvas(img, **kwargs)

        self._csbox_threshold.grid_forget()

        self._csbox_centroids = csbox.CSBox(self, bbox=[["Reset Centroids", "Set Centroids", "Compute Centroids"], [self.reset_centroids, self.set_centroids, self.get_centroids]], sbox=[["Centroids"], [3], ["int"]])
        self._csbox_centroids.grid(row=4, column=1, rowspan=4, sticky=W+E)

        self._csbox_shadow = csbox.CSBox(self, bbox=[["Detect Shadow"], [self.get_shadow]], cbox=[["Image"], [[0,1,2]], [0], ["int"]])
        self._csbox_shadow.grid(row=8, column=1, rowspan=2, sticky=N+W+E)

        self._button_quit.grid(row=10, column=0, columnspan=3, sticky=W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_shadow(self, event=None):
        pass


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_cmap(self, n, name='hsv'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
        cmap = plt.cm.get_cmap(name, n)
        cmap = [list(cmap(c)[0:3]) for c in range(0, n)]

        return cmap

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_centroids(self, event=None):
        self._centroids_img = self.get_obj().get_img()
        self._centroids_img_shape = (self._centroids_img.shape[0], self._centroids_img.shape[1]) 

        if not self._centroids:
            number = self._csbox_centroids.get_dict()["Centroids"]
            codes = number
            minit = "++"
        else:
            number = len(self._centroids)
            codes = np.stack(self._centroids, axis=0).astype(np.float)
            minit = "matrix"
        
        centroids, label = kmeans2(self._centroids_img.reshape((-1,3)).astype(np.float), codes, minit=minit)
        label = label.reshape(self._centroids_img_shape)

        mask_list = [np.where(label==idx, 1, 0).astype(np.uint8) for idx in range(len(centroids))]
        mask_color = np.random.randint(0, 255, number*3, dtype=np.uint8).reshape((number,3)).tolist()
        mask_alpha = [100]*number
        mask_invert = [False]*number

        self.get_obj().set_mask(mask=mask_list, color=mask_color
        , invert=mask_invert, alpha=mask_alpha, show=True)
        # self._centroids.append(self.get_obj()._mouse_img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def reset_centroids(self, event=None): 
        self._centroids = list()   

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_centroids(self, event=None):
        self._centroids.append(self.get_obj()._data_img[self.get_obj()._mouse_img[0], self.get_obj()._mouse_img[1], :])
        print(self._centroids)
        # param_shdw = self._csbox_shadow.get_dict()
        # param_blur = self._csbox_blur.get_dict()

        # img = self.get_obj().get_img_from_label("image")
        
        
        # shdwimg_list = sd.shadowDetection(img, d=param_blur["Diameter"], sigmaColor= param_blur["Sigma Color"], sigmaSpace=param_blur["Sigma Space"], logger=self._logger)

        # self.get_obj().set_img(shdwimg_list[param_shdw["Image"]])
        # self.set_img()
