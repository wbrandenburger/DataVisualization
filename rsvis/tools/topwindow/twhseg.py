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

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

from skimage import segmentation

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
        self._csbox_difference.grid_forget()

        # set combobox and settingsbox for blurring parameters
        self._csbox_seg = csbox.CSBox(self, cbox=[["Model"], [["Felzenswalb", "SLIC"]], ["SLIC"], ["str"]], bbox=[["Image Segmentation"], [self.image_segmentation]])
        self._csbox_seg.grid(row=4, column=1, rowspan=1, sticky=N+W+E+S)

        # set combobox and settingsbox for blurring parameters
        self._csbox_felz = csbox.CSBox(self, sbox=[["scale", "sigma", "min_size"], [32, 0.5, 256], ["int", "float", "int"]], )
        self._csbox_felz.grid(row=5, column=1, rowspan=3, sticky=N+W+E+S)

        # set combobox and settingsbox for blurring parameters
        self._csbox_slic = csbox.CSBox(self, sbox=[["compactness", "n_segments", "max_iter", "convert2lab", "enforce_connectivity"], [20, 50, 100, 1, 0], ["float", "int", "int", "bool", "bool"]])
        self._csbox_slic.grid(row=8, column=1, rowspan=3, sticky=N+W+E+S)

        self._button_quit.grid(row=12, column=0, columnspan=3, sticky=W+E)

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
        
        if param["Model"]=="Felzenswalb":
            # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.felzenszwalb.
            seg_map = segmentation.felzenszwalb(img, **self._csbox_felz.get_dict())
        elif param["Model"]=="SLIC":
            # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
            seg_map = segmentation.slic(img, **self._csbox_slic.get_dict(), start_label=1)

        # set image in canvas and update histogram
        # self.get_obj().set_img(seg_map)
        self.get_obj().set_img(segmentation.mark_boundaries(img, seg_map), clear_mask=False)        