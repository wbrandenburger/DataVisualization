# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
from rsvis.utils import imgbasictools
import rsvis.utils.imgcontainer

import rsvis.tools.extcanvas
import rsvis.tools.imgconcanvas
import rsvis.tools.keys
import rsvis.tools.rescanvas
import rsvis.tools.widgets

import numpy as np
from PIL import Image, ImageTk
from tkinter import ttk, Scale, Button, Canvas, Label, Menu, TOP, X, NW, N, W, S, E, CENTER, VERTICAL, HORIZONTAL

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindowHist(rsvis.tools.topwindow.TopWindow):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TopWindowHist, self).__init__(parent, **kwargs)
        
        #   key bindings ----------------------------------------------------
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)
        self.bind("<u>", self.key_u)

        self._keys.update({ 
                "u": "Update the histogram due to changes in image canvas.",
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        super(TopWindowHist, self).set_canvas(img, **kwargs)

        self.columnconfigure(1, weight=1)

        self._canvas.grid(row=0, column=0, rowspan=3, sticky=N+S+W+E)
        self._button.grid(row=3, column=0, columnspan=2)

        self._canvas_hist = rsvis.tools.rescanvas.ResizingCanvas(self)
        self.update_histogram()
        self._canvas_hist.grid(row=0, column=1, columnspan=1, sticky=N+S+W+E)

        img_mean = np.mean(self._canvas.get_img())
        img_std = np.std(self._canvas.get_img())
        
        self._slider_mean = Scale(self, from_=255., to=-255, orient=HORIZONTAL, command=self.update_slider)
        self._slider_std = Scale(self, from_=img_std-1, to=-img_std+1, orient=HORIZONTAL, command=self.update_slider)
        self._slider_mean.set(0.0)
        self._slider_std.set(0.0)

        self._slider_mean.grid(row=1, column=1, sticky=W+E)
        self._slider_std.grid(row=2, column=1, sticky=W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_histogram(self, event=None, **kwargs):
        self._canvas_hist.set_img(
            imgtools.get_histogram(self._canvas.get_img(), logger=self._logger)
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_slider(self, event):
        self._canvas.set_img(
            imgbasictools.get_linear_transformation(self._img, self._slider_mean.get(), self._slider_std.get(), logger=self._logger
            )
        )
        self.update_histogram()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        self.update_histogram()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        self.update_histogram()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_u(self, event, **kwargs):
        """Update the histogram due to changes in image canvas."""
        self.update_histogram()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_e(self, event, **kwargs):
        """Exit RSVis."""
        super(TopWindowHist, self).key_e(event, **kwargs)
        self.update_histogram()
    