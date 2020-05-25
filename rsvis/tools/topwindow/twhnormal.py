# ===========================================================================
#   twhnormal.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.combobox
import rsvis.tools.settingsbox
from rsvis.tools.csbox import CSBox
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
        # self._slider_hist_column = 4
        super(TWHNormal, self).set_canvas(img, **kwargs)
    

        # self._param_normal_model = "LS"
        # self._cbox_normal_model = rsvis.tools.combobox.ComboBox(self, "Local Model",  ["LS", "TRI", "QUADRIC"], self.update_cbox_normal_model, default=0)
        # self._cbox_normal_model.grid(row=2, column=1, columnspan=4, sticky=W+E)



        # self._param_normal_radius = 6.0
        # self._sbox_normal_radius = rsvis.tools.settingsbox.SettingsBox(self, ["Radius"], self.update_sbox_normal_radius, default=[self._param_normal_radius])
        # self._sbox_normal_radius.grid(row=2, column=0, sticky=W+E)

        # self._param_normal_bins = 16
        # self._sbox_normal_bins = rsvis.tools.settingsbox.SettingsBox(self, ["Normal bins"], self.update_sbox_normal_bins, default=[self._param_normal_bins])
        # self._sbox_normal_bins.grid(row=3, column=0, sticky=W+E)

        # self._param_height_factor = 1.0
        # self._sbox_height_factor = rsvis.tools.settingsbox.SettingsBox(self, ["Height factor"], self.update_sbox_height_factor, default=[self._param_height_factor])
        # self._sbox_height_factor.grid(row=4, column=0, sticky=W+E)

        # self._param_normal_log = IntVar()
        # self._param_normal_log.set(1)
        # self._cbutton_normal_log = Checkbutton(self, text="Log", variable=self._param_normal_log)
        # self._cbutton_normal_log.grid(row=2, column=4, sticky=W+E)

        self._csbox_normal = CSBox(self, cbox=[["Local Model"], ["LS", "TRI", "QUADRIC"], ["LS"], ["str"]], sbox=[["Radius", "Normal bins", "Log", "Height factor"], [6.0, 16, True, 1.0], ["float", "int", "bool", "float"]])

        self._csbox_normal.grid(row=2, column=0, rowspan=5, sticky=W+E)

        self._button_open = ttk.Button(self, text="Open PC", 
            command=self.open_normal_cloud)
        self._button_open.grid(row=2, column=1, sticky=W+E)

        self._button_open = ttk.Button(self, text="Open PC Normal", 
            command=self.open_normal_cloud_rgb)
        self._button_open.grid(row=3, column=1, sticky=W+E)

        self._button_hist_proj = ttk.Button(self, text="Mask Image", 
            command=self.update_proj_hist)
        self._button_hist_proj.grid(row=4, column=1, sticky=E+W)

        self._button_normal = ttk.Button(self, text="Normal Image", 
            command=self.set_normal_img)
        self._button_normal.grid(row=5, column=1, sticky=W+E)

        self._button_binned_normal = ttk.Button(self, text="Binned Image", 
            command=self.set_binned_normal_img)
        self._button_binned_normal.grid(row=6, column=1, sticky=W+E)

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

        self.get_obj().set_img(normalimg)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_binned_normal_img(self):
        self.update_normal()

        param = self._csbox_normal.get_dict()
        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label("height"), log=param["Log"], factor=param["Height factor"], bins=param["Normal bins"])

        self.get_obj().set_img(normalimg)
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