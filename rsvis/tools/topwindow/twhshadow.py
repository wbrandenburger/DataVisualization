# ===========================================================================
#   twhshadow.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox
from rsvis.tools.topwindow import tw,twhfilter

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

        self.reset_centroids()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWHShadow, self).set_canvas(img, **kwargs)

        self._csbox_threshold.grid_forget()
        self._csbox_difference.grid(row=14, column=0, rowspan=4, sticky=N+W+S+E)

        self._csbox_centroids = csbox.CSBox(self, bbox=[["Reset Centroids", "Set Centroids", "Compute Centroids (Color)", "Compute Centroids (Color+Space)"], [self.reset_centroids, self.set_centroids, self.get_centroids_color, self.get_centroids_color_space]], sbox=[["Centroids"], [3], ["int"]])
        self._csbox_centroids.grid(row=4, column=1, rowspan=5, sticky=W+E)

        self._csbox_hough = csbox.CSBox(self, bbox=[["Hough Transform"], [self.get_hough_transform]], sbox=[["Threshold", "Minimum Line Length","Maximum Line Gap"], [40, 40, 40], ["int", "int", "int"]])
        self._csbox_hough.grid(row=10, column=1, rowspan=1, sticky=N+W+E)

        self._button_quit.grid(row=18, column=0, columnspan=3, sticky=W+E)

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
    def get_centroids_color(self, event=None):
        img = self.get_obj().get_img(show=True).astype(np.float)
        self._centroids_img_shape = (img.shape[0], img.shape[1]) 

        data = whiten(img.reshape((-1,3)))
        self.get_centroids(data)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_centroids_color_space(self, event=None):
        img = self.get_obj().get_img(show=True).astype(np.float)
        self._centroids_img_shape = (img.shape[0], img.shape[1]) 

        grid = np.indices((self._centroids_img_shape), dtype=np.float)
        data = whiten(np.stack([img[...,0], img[...,1], img[...,2], grid[0], grid[1]], axis=2).reshape((-1,5)))
        self.get_centroids(data)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_centroids(self, data, event=None):     
        if not self._centroids:
            number = self._csbox_centroids.get_dict()["Centroids"]
            codes = number
            minit = "++"
        else:
            number = len(self._centroids)
            codes = np.stack(self._centroids, axis=0).astype(np.float)
            minit = "matrix"

        centroids, label = kmeans2(data, codes, minit=minit)
        label = label.reshape(self._centroids_img_shape)

        mask_list = [np.where(label==idx, 1, 0).astype(np.uint8) for idx in range(len(centroids))]
        mask_color = np.random.randint(0, 255, number*3, dtype=np.uint8).reshape((number,3)).tolist()
        mask_alpha = [150]*number
        mask_invert = [False]*number

        self.get_obj().set_mask(mask=mask_list, color=mask_color
        , invert=mask_invert, alpha=mask_alpha, show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def reset_centroids(self, event=None): 
        self._centroids = list()   

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_centroids(self, event=None):
        self._centroids.append(self.get_obj()._data_img[self.get_obj()._mouse_img[0], self.get_obj()._mouse_img[1], :])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_hough_transform(self, event=None):
        param_edges = self._csbox_edges.get_dict()
        param_hough = self._csbox_hough.get_dict()

        img = self.get_obj().get_img(show=True)
        grayimg= cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        images = list()

        aperture_size = param_edges["Aperture Size"]
        if (aperture_size%2)==0 or aperture_size<3 or aperture_size>7:
            raise ValueError("Aperture size should be odd between 3 and 7.")

        edges = cv2.Canny(grayimg, param_edges["Threshold I"], param_edges["Threshold II"], apertureSize=param_edges["Aperture Size"])
    
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, param_hough["Threshold"],minLineLength=param_hough["Minimum Line Length"], maxLineGap=param_hough["Maximum Line Gap"])

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 128), 1)

            images = [edges, img]
        else:
            images = edges

        tw.TopWindow(self, title="Hough Transform", dtype="img", value=images, q_cmd=self._q_cmd)