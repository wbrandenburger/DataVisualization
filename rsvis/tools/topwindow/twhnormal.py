# ===========================================================================
#   twhnormal.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox
from rsvis.tools.topwindow import twhist

import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHNormal(twhist.TWHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            param,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHNormal, self).__init__(parent, **kwargs)
        
        self._height = Height(param, logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWHNormal, self).set_canvas(img, **kwargs)
        self._csbox_normal = csbox.CSBox(self, cbox=[["model", "ntype"], [["LS", "TRI", "QUADRIC"], ["xy", "z"]], ["LS", "z"], ["str", "str"]], sbox=[["radius", "bins", "log", "alpha", "domain"], [6.0, 16, 1, 0.1, "height"], ["float", "int", "int", "float", "str"]])
        self._csbox_normal.grid(row=2, column=0, rowspan=7, sticky=N+W+E+S)

        self._button_normal = buttonbox.ButtonBox(self, bbox=[["Open PC", "Open PC Normal", "Normal Image", "Binned Image"], [self.open_normal_cloud, self.open_normal_cloud_rgb, self.set_normal_img, self.set_binned_normal_img]])
        self._button_normal.grid(row=2, column=1, rowspan=4, sticky=N+W+E+S)

        self._button_quit.grid(row=9, column=0, columnspan=3, sticky=W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_normal(self):
        param = self._csbox_normal.get_dict()

        self._height.set_level()
        self._height.set_param_normal(radius=param["radius"], model=param["model"])    

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_normal_img(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()
        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label(param["domain"]), log=param["log"], ntype=param["ntype"])

        self.get_obj().set_img(normalimg, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_binned_normal_img(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()
        normalimg = np.round(self._height.get_normal_img(self.get_obj().get_img_from_label(param["domain"]), log=param["log"], ntype=param["ntype"], bins=param["bins"])*param["bins"])

        self.get_obj().set_img(imgtools.get_color_map(normalimg, self.get_obj().get_img(), alpha=param["alpha"]) , clear_mask=False)
        self.set_img()
        

# def blubb(obj, param):
#     bins=12
#     normal_img = np.round(Height(param).get_normal_img(obj.get_img_from_label("{height}"),log=True, bins=bins)*bins)
#     return imgtools.get_color_map(normal_img, obj.get_img(), alpha=0.2)        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()    
        self._height.open("pointcloud", [self.get_obj().get_img_from_label(param["domain"]), self.get_obj().get_img(), []])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud_rgb(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()    
        self._height.get_normal(self.get_obj().get_img_from_label(param["domain"]))