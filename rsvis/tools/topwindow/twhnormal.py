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

        self._csbox_normal = csbox.CSBox(self, cbox=[["Local Model"], [["LS", "TRI", "QUADRIC"]], ["LS"], ["str"]], sbox=[["Radius", "Normal bins", "Log", "Height factor"], [6.0, 16, 1, 1.0], ["float", "int", "int", "float"]])
        self._csbox_normal.grid(row=2, column=0, rowspan=5, sticky=N+W+E+S)

        self._button_normal = buttonbox.ButtonBox(self, bbox=[["Open PC", "Open PC Normal", "Normal Image", "Binned Image"], [self.open_normal_cloud, self.open_normal_cloud_rgb, self.set_normal_img, self.set_binned_normal_img]])
        self._button_normal.grid(row=2, column=1, rowspan=4, sticky=N+W+E+S)

        self._button_quit.grid(row=7, column=0, columnspan=3, sticky=W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_normal(self):
        param = self._csbox_normal.get_dict()

        self._height.set_level()
        self._height.set_param_normal(radius=param["Radius"], model=param["Local Model"])    

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_normal_img(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()
        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label("height"), log=param["Log"], factor=param["Height factor"])

        self.get_obj().set_img(normalimg, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_binned_normal_img(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()
        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label("height"), log=param["Log"], factor=param["Height factor"], bins=param["Normal bins"])

        self.get_obj().set_img(normalimg, clear_mask=False)
        self.set_img()
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()    
        self._height.open("pointcloud", [self.get_obj().get_img_from_label("height"), self.get_obj().get_img(), []], factor=param["Height factor"])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud_rgb(self):
        self.update_normal()    
        
        self._height.get_normal(self.get_obj().get_img_from_label("height"))