# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgbasictools, imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.combobox
import rsvis.tools.settingsbox
import rsvis.tools.topwindowhist

import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindowHistNormal(rsvis.tools.topwindowhist.TopWindowHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            param,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TopWindowHistNormal, self).__init__(parent, **kwargs)
        
        self._height = Height(param, logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        self._slider_hist_column = 4
        super(TopWindowHistNormal, self).set_canvas(img, **kwargs)
        
        self._canvas_hist.grid(row=0, column=1, rowspan=3, columnspan=3, sticky=N+S+W+E)

        self._param_normal_radius = 6.0
        self._sbox_normal_radius = rsvis.tools.settingsbox.SettingsBox(self, ["Radius"], self.update_sbox_normal_radius, default=[self._param_normal_radius])
        self._sbox_normal_radius.grid(row=2, column=0, sticky=W+E)

        self._param_normal_bins = 16
        self._sbox_normal_bins = rsvis.tools.settingsbox.SettingsBox(self, ["Normal bins"], self.update_sbox_normal_bins, default=[self._param_normal_bins])
        self._sbox_normal_bins.grid(row=3, column=0, sticky=W+E)

        self._param_height_factor = 1.0
        self._sbox_height_factor = rsvis.tools.settingsbox.SettingsBox(self, ["Height factor"], self.update_sbox_height_factor, default=[self._param_height_factor])
        self._sbox_height_factor.grid(row=4, column=0, sticky=W+E)

        self._param_normal_model = "LS"
        self._cbox_normal_model = rsvis.tools.combobox.ComboBox(self, "Local Model",  ["LS", "TRI", "QUADRIC"], self.update_cbox_normal_model, default=0)
        self._cbox_normal_model.grid(row=2, column=1, columnspan=4, sticky=W+E)

        self._param_normal_log = IntVar()
        self._param_normal_log.set(1)
        self._cbutton_normal_log = Checkbutton(self, text="Log", variable=self._param_normal_log)
        self._cbutton_normal_log.grid(row=2, column=4, sticky=W+E)

        self._button_open = ttk.Button(self, text="Open PC", 
            command=self.open_normal_cloud)
        self._button_open.grid(row=3, column=1, columnspan=1, sticky=W+E)

        self._button_open = ttk.Button(self, text="Open PC Normal", 
            command=self.open_normal_cloud_rgb)
        self._button_open.grid(row=3, column=2, columnspan=1, sticky=W+E)

        self._button_normal = ttk.Button(self, text="Normal Image", 
            command=self.set_normal_img)
        self._button_normal.grid(row=4, column=1, columnspan=1, sticky=W+E)

        self._button_binned_normal = ttk.Button(self, text="Binned Image", 
            command=self.set_binned_normal_img)
        self._button_binned_normal.grid(row=4, column=2, columnspan=1, sticky=W+E)

        self._button_quit.grid(row=4, column=3, columnspan=1, sticky=W+E)


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_cbox_normal_model(self, event=None):
        self._param_normal_model = self._cbox_normal_model.get()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_normal_radius(self, event=None):
        self._param_normal_radius = float(self._sbox_normal_radius.get())
        if self._param_normal_radius == 0.0:
            self._param_normal_radius = "AUTO"

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_height_factor(self, event=None):
        self._param_height_factor = float(self._sbox_height_factor.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_sbox_normal_bins(self, event=None):
        self._param_normal_bins = int(self._sbox_normal_bins.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_normal(self):
        self.update_sbox_normal_radius()
        self.update_sbox_height_factor()
        self.update_sbox_normal_bins()

        self._logger("[CMP] Radius: {}, Model: {}, Bins: {}, Log: {}, Factor: {:.2f}".format(self._param_normal_radius, self._param_normal_model, self._param_normal_bins, self._param_normal_log.get(), self._param_height_factor))

        self._height.set_level()
        self._height.set_param_normal(radius=self._param_normal_radius, model=self._param_normal_model)    

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_normal_img(self):
        self.update_normal()

        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label("height"), log=int(self._param_normal_log.get()), factor=self._param_height_factor)

        self.get_obj().set_img(normalimg)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_binned_normal_img(self):
        self.update_normal()

        normalimg = self._height.get_normal_img(self.get_obj().get_img_from_label("height"), log=int(self._param_normal_log.get()), factor=self._param_height_factor, bins=self._param_normal_bins)

        self.get_obj().set_img(normalimg)
        self.set_img()
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud(self):
        self.update_normal()    
        self._height.open("pointcloud", [self.get_obj().get_img_from_label("height"), self.get_obj().get_img(), []], factor=self._param_height_factor)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open_normal_cloud_rgb(self):
        self.update_normal()    
        self._height.get_normal(self.get_obj().get_img_from_label("height"))        