# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox
from rsvis.tools.topwindow import tw, twhist, twhfilter

from scipy.cluster.vq import vq, kmeans, kmeans2, whiten

from skimage import segmentation, color
from skimage.future import graph

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHSeg(twhfilter.TWHFilter):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHSeg, self).__init__(parent, **kwargs)
        
        self.reset_dimage()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWHSeg, self).set_canvas(img, **kwargs)

        self._csbox_threshold.grid_forget()
        self._csbox_edges.grid_forget()
        self._csbox_hough.grid_forget()
        self._csbox_difference.grid_forget()

        # set combobox and settingsbox for segmentation methods
        self._csbox_seg = csbox.CSBox(self, cbox=[["Model"], [[ "SLIC",  "Normalized Cuts", "GrabCut", "Felzenswalb"]], ["SLIC"], ["str"]], bbox=[["Image Segmentation"], [self.image_segmentation]]) 
        self._csbox_seg.grid(row=4, column=1, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut k-means
        self._csbox_slic = csbox.CSBox(self, sbox=[["compactness", "n_segments", "max_iter", "convert2lab"], [20, 50, 100, 1], ["float", "int", "int", "bool"]])
        self._csbox_slic.grid(row=6, column=1, rowspan=4, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut
        self._csbox_grab = csbox.CSBox(self, sbox=[["iterCount"], [5], ["int"]])
        self._csbox_grab.grid(row=10, column=1, rowspan=1, sticky=N+W+S+E)

       # set combobox and settingsbox for the segmentation method felzenswalb
        self._csbox_felz = csbox.CSBox(self, sbox=[["scale", "sigma", "min_size"], [32, 0.5, 256], ["int", "float", "int"]], )
        self._csbox_felz.grid(row=11, column=1, rowspan=3, sticky=N+W+S+E)

        self._button_quit.grid(row=14, column=0, columnspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for adding images boxes
        self._csbox_boxes = csbox.CSBox(self, bbox=[["Show Box"], [self.show_box]])
        self._csbox_boxes.grid(row=10, column=0, rowspan=1, sticky=N+W+S+E)  

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb'efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        # get settings of combobox and fields 
        param = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img()

        # define image list for visualization
        img_list = [img]
        if param["Model"]=="SLIC" or param["Model"]=="Normalized Cuts":
            # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
            # n_segments = the (approximate) number of labels in the segmented output image.
            # compactness: balances color proximity and space proximity.
            # max_iter: maximum number of iterations of k-means.
            seg_map = segmentation.slic(img, **self._csbox_slic.get_dict(), start_label=1)
            seg_map_bound = segmentation.mark_boundaries(img, seg_map)
            seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=0)

            # define image list for visualization
            img_list.extend([seg_map_bound, seg_map_color])

        if param["Model"]=="Felzenswalb":
            # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.felzenszwalb.
            seg_map = segmentation.felzenszwalb(img, **self._csbox_felz.get_dict())
            seg_map_bound = segmentation.mark_boundaries(img, seg_map)
            seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=0)

            # define image list for visualization
            img_list.extend([seg_map_bound, seg_map_color])
    
        elif param["Model"]=="Normalized Cuts":
            # https://scikit-image.org/docs/stable/api/skimage.future.graph.html#skimage.future.graph.cut_normalized
            # https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_ncut.html
            g = graph.rag_mean_color(img, seg_map, mode='similarity')
            seg_map = graph.cut_normalized(seg_map, g)
            seg_map_bound = segmentation.mark_boundaries(img, seg_map)
            seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=0) 
            
            # define image list for visualization
            img_list.extend([seg_map_bound, seg_map_color])

        elif param["Model"]=="GrabCut":
            # https://docs.opencv.org/master/dd/dfc/tutorial_js_grabcut.html
            
            # get the region of interest
            roi = self.get_obj().get_roi()

            # raise error if the width and height of the roi is not defined
            if not sum(roi[2:4]):
                raise IndexError("There are no images available.")
            
            # allocate mask, background and foreground model
            mask = np.zeros(img.shape[:2],np.uint8)
            bgdModel = np.zeros((1,65),np.float64)
            fgdModel = np.zeros((1,65),np.float64)

            # this modifies mask 
            cv2.grabCut(img, mask, roi, bgdModel, fgdModel, **self._csbox_grab.get_dict(), mode=cv2.GC_INIT_WITH_RECT)

            # If mask==2 or mask== 1, mask2 get 0, other wise it gets 1 as 'uint8' type.
            seg_map = np.where((mask==2)|(mask==0), 0, 1).astype('bool')
            img_cut = img*seg_map[:,:,np.newaxis]
            
            # define image list for visualization
            img_list = [img, img_cut, img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2], :]]  

        # open a topwindow with the segmentation results of the currently displayed image      
        tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)      

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_box(self, event=None):        
        """Show list of boxes 
        """

        # get the region of interest
        roi = self.get_obj().get_roi()

        # raise error if the width and height of the roi is not defined
        if not sum(roi[2:4]):
            raise IndexError("There are no images available.")
        
        # get the currently displayed image
        img = self.get_obj().get_img(show=True)

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Boxes", dtype="img", value=[img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2], :]])

    # #   CENTROIDS -----------------------------------------------------------
    # # -----------------------------------------------------------------------

        # # set combobox and settingsbox for kmeans
        # self._csbox_centroids = csbox.CSBox(self, bbox=[["Reset Centroids", "Set Centroids", "Compute Centroids (Color)", "Compute Centroids (Color+Space)"], [self.reset_centroids, self.set_centroids, self.get_centroids_color, self.get_centroids_color_space]], sbox=[["Centroids"], [3], ["int"]])
        # self._csbox_centroids.grid(row=4, column=1, rowspan=5, sticky=W+E)


    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_cmap(self, n, name='hsv'):
    #     '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    #     RGB color; the keyword argument name must be a standard mpl colormap name.'''
    #     cmap = plt.cm.get_cmap(name, n)
    #     cmap = [list(cmap(c)[0:3]) for c in range(0, n)]

    #     return cmap

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids_color(self, event=None):
    #     img = self.get_obj().get_img(show=True).astype(np.float)
    #     self._centroids_img_shape = (img.shape[0], img.shape[1]) 

    #     data = whiten(img.reshape((-1,3)))
    #     self.get_centroids(data)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids_color_space(self, event=None):
    #     img = self.get_obj().get_img(show=True).astype(np.float)
    #     self._centroids_img_shape = (img.shape[0], img.shape[1]) 

    #     grid = np.indices((self._centroids_img_shape), dtype=np.float)
    #     data = whiten(np.stack([img[...,0], img[...,1], img[...,2], grid[0], grid[1]], axis=2).reshape((-1,5)))
    #     self.get_centroids(data)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids(self, data, event=None):     
    #     if not self._centroids:
    #         number = self._csbox_centroids.get_dict()["Centroids"]
    #         codes = number
    #         minit = "++"
    #     else:
    #         number = len(self._centroids)
    #         codes = np.stack(self._centroids, axis=0).astype(np.float)
    #         minit = "matrix"

    #     centroids, label = kmeans2(data, codes, minit=minit)
    #     label = label.reshape(self._centroids_img_shape)

    #     mask_list = [np.where(label==idx, 1, 0).astype(np.uint8) for idx in range(len(centroids))]
    #     mask_color = np.random.randint(0, 255, number*3, dtype=np.uint8).reshape((number,3)).tolist()
    #     mask_alpha = [150]*number
    #     mask_invert = [False]*number

    #     self.get_obj().set_mask(mask=mask_list, color=mask_color
    #     , invert=mask_invert, alpha=mask_alpha, show=True)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def reset_centroids(self, event=None): 
    #     self._centroids = list()   

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def set_centroids(self, event=None):
    #     self._centroids.append(self.get_obj()._data_img[self.get_obj()._mouse_img[0], self.get_obj()._mouse_img[1], :])