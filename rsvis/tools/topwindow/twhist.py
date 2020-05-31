# ===========================================================================
#   twhist.py ------------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools

from rsvis.tools.canvas import imgcv
from rsvis.tools.topwindow import tw

import numpy as np
from tkinter import *

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHist(tw.TopWindow):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            **kwargs
        ):

        #   general window settings -----------------------------------------
        self._slider_hist_row = 0
        self._slider_hist_column = 2
        self._slider_hist_rowspan = 1

        #   settings --------------------------------------------------------
        super(TWHist, self).__init__(parent, **kwargs)
        self.rowconfigure(1, weight=1)

        #   key bindings ----------------------------------------------------
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)

        self._keys.update(dict())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self):
        super(TWHist, self).set_img()
        self.set_slider_hist()
        self.update_hist()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TWHist, self).set_canvas(img, **kwargs)

        self.columnconfigure(1, weight=1)

        self._button_quit.grid(row=2, column=0, columnspan=3)

        self._canvas.grid(row=0, column=0, rowspan=2, sticky=N+S+W+E)
        self._canvas_hist = imgcv.ImgCanvas(self)
        self._canvas_hist.grid(row=0, column=1, rowspan=2, sticky=N+S+W+E)

        self.update_hist()
        self.set_slider_hist()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_slider_hist(self, mean=0., std=0.):
        img_mean = np.mean(self._canvas.get_img(show=True))
        img_std = np.std(self._canvas.get_img(show=True))

        self._param_hist_mean = 0.
        self._slider_hist_mean = Scale(self, from_=-img_mean, to=255.-img_mean, orient=VERTICAL, command=self.update_slider_hist_mean, resolution=5.) 
        self._slider_hist_mean.set(self._param_hist_mean) #label="Mean"
        self._slider_hist_mean.grid(row=self._slider_hist_row, column=self._slider_hist_column, rowspan=self._slider_hist_rowspan, sticky=N+S)

        self._param_hist_std = 0.
        self._slider_hist_std = Scale(self, from_=-img_std+3, to=img_std-3, orient=VERTICAL, command=self.update_slider_hist_std, resolution=3.) 
        self._slider_hist_std.set(self._param_hist_std) #label="Std"
        self._slider_hist_std.grid(row=self._slider_hist_row+1, column=self._slider_hist_column, rowspan=self._slider_hist_rowspan, sticky=N+S)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_hist(self, event=None, **kwargs):
        self._canvas_hist.set_img(
            imgtools.get_histogram(self._canvas.get_img(show=True), mask=self.get_obj().get_mask(), logger=self._logger)
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_slider_hist_mean(self, event):
        self._param_hist_mean = self._slider_hist_mean.get()
        self.update_img_linear_transformation(event)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_slider_hist_std(self, event):
        self._param_hist_std = self._slider_hist_std.get()
        self.update_img_linear_transformation(event)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_img_linear_transformation(self, event):
        self._canvas.set_img(
            imgtools.get_linear_transformation(self._img, self._param_hist_mean, self._param_hist_std, logger=self._logger
            ),
            clear_mask=False
        )
        self.update_hist()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_r(self, event, **kwargs):
        """Exit RSVis."""
        super(TWHist, self).key_r(event, **kwargs)
        self.set_slider_hist()
    