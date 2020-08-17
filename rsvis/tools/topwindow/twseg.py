# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
import rsvis.utils.general as gu
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox, imgiogui
from rsvis.tools.topwindow import tw

from scipy.cluster.vq import vq, kmeans, kmeans2, whiten

from skimage import segmentation, color
from skimage.future import graph

import rsvis.utils.imgseg

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWSeg(tw.TopWindow):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWSeg, self).__init__(parent, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWSeg, self).set_canvas(img, **kwargs)
        
        self._frame = Frame(self)
        self._frame.grid(row=2, column=0, sticky=N+W+S+E)

        self._imgio = imgiogui.ImgIOGUI(self)
        self._imgio.grid(row=1, column=0, sticky=N+W+S+E)

        self._button_attempt = ttk.Button(self, text="Attempt", 
                command=lambda x = self.attempt: x(self.image_segmentation)
            )
        self._button_attempt.grid(row=3, column=0, columnspan=1)
        self._button_quit.grid(row=4, column=0, sticky=N+W+S+E) 

        # set combobox and settingsbox for segmentation methods
        self._csbox_seg = csbox.CSBox(self._frame, cbox=[["Model"], [[ "SLIC",  "Normalized Cuts", "Felzenswalb"]], ["SLIC"], ["str"]], bbox=[["Image Segmentation"], [self.image_segmentation]]) 
        self._csbox_seg.grid(row=1, column=0, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for segmentation methods
        self._csbox_bound = csbox.CSBox(self._frame, cbox=[["boundaries"], [[ "mark",  "find"]], ["find"], ["str"]]) 
        self._csbox_bound.grid(row=3, column=0, rowspan=1, sticky=N+W+S+E)

       # set combobox and settingsbox for the segmentation method felzenswalb
        self._csbox_felz = csbox.CSBox(self._frame, sbox=[["scale", "sigma", "min_size"], [16, 0.5, 16], ["int", "float", "int"]])
        self._csbox_felz.grid(row=4, column=0, rowspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut k-means
        self._csbox_slic = csbox.CSBox(self._frame, sbox=[["compactness", "n_segments", "max_iter", "convert2lab"], [10, 5000, 15, 1], ["float", "int", "int", "bool"]])
        self._csbox_slic.grid(row=7, column=0, rowspan=4, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut
        self._csbox_grab = csbox.CSBox(self._frame, sbox=[["iterCount"], [5], ["int"]],  bbox=[["GrabCut Segmentation"], [self.image_segmentation_grabcut]])
        self._csbox_grab.grid(row=11, column=0, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut
        self._csbox_bp = csbox.CSBox(self._frame, sbox=[["dim1", "dim2", "min_label", "max_label", "iterCount", "factor", "net"], [32, 64 , 4, 256, 160, 1.0, 1], ["int", "int", "int", "int", "int", "float", "int"]],  bbox=[["Unsupervised Segmentation via BP"], [self.image_segmentation_backpropagation]])
        self._csbox_bp.grid(row=1, column=1, rowspan=7, sticky=N+W+S+E)

        self._button_quit.grid(row=2, column=0, sticky=N+W+S+E) 


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def attempt(self, func):
        for obj in self.get_obj():
            func()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        # get settings of combobox and fields 
        param = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img()

        # define image list for visualization
        img_list = [img]

        if param["Model"]=="SLIC":
            param_str = "slic-{}".format("-".join([str(e) for e in self._csbox_slic.get_list()]))
            _, seg_map_color, seg_map_bound = rsvis.utils.imgseg.segmentation_slic(img, **self._csbox_slic.get_dict(), **self._csbox_bound.get_dict())

        elif param["Model"]=="Felzenswalb":
            param_str = "felz-{}".format("-".join([str(e) for e in self._csbox_slic.get_list()]))
            _, seg_map_color, seg_map_bound = rsvis.utils.imgseg.segmentation_felzenswalb(img, **self._csbox_felz.get_dict(), **self._csbox_bound.get_dict())

        elif param["Model"]=="Normalized Cuts":
            param_str = "norm-{}".format("-".join([str(e) for e in self._csbox_slic.get_list()]))
            _, seg_map_color, seg_map_bound = rsvis.utils.imgseg.segmentation_norm(img, **self._csbox_slic.get_dict(), **self._csbox_bound.get_dict())

        # seg_map dtype: int64 
        self._imgio.write(self.get_obj().get_img_path(), seg_map_color, log_str=log_str, name="{}-{{}}".format(gu.get_valid_filename(param_str)))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation_backpropagation(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        pass
        # self.image_segmentation()
        # define image list for visualization
        # import rsvis.segmentation.unsegbp
        # rsvis.segmentation.unsegbp.unsegbp(self._img_seg, self._seg_map, lambda img: self._img_tw.update(img, index=2), self._logger, **self._csbox_bp.get_dict())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation_grabcut(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        # get settings of combobox and fields 
        param = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img()

        # define image list for visualization
        img_list = [img]

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