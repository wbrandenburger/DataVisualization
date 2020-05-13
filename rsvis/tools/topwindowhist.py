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

import rsvis.tools.rscanvasframe

import numpy as np
from PIL import Image, ImageTk
from tkinter import Toplevel, ttk, Scale, Button, Canvas, Label, Menu, TOP, X, NW, N, W, S, E, CENTER, VERTICAL

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindowHist(Toplevel):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            command=None,
            options=list(),
            label=None,
            logger=None,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TopWindowHist, self).__init__(parent, title="Historam Canvas", dtype="img", **kwargs)
        
        #   general window settings -----------------------------------------
        self._b_col = 2 

        #   key bindings ----------------------------------------------------
        self.bind("<q>", self.key_q)
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)      
        self.bind("<u>", self.key_u)
        self.bind("<e>", self.key_e)

        self._keys = { 
            "q": "Exit RSVis.",
            "u": "Update the histogram due to changes in image canvas.",
            "e": "Set current image for processing."
        }

        for o in options:
            if o["key"] is not None:
                self._keys.update({o["key"]: o["description"]}) 
        
        #   menubar (Options) -----------------------------------------------
        if self._menubar_flag and options:
            self._menubar = Menu(self)
            rsvis.tools.widgets.add_option_menu(self._menubar, options, self, self._canvas, label="Options")
            rsvis.tools.widgets.add_info_menu(self._menubar, self, self, lambda obj=self, parent=parent: self.show_help(parent))
            self.config(menu=self._menubar)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, *args):
        super(TopWindowHist, self).set_canvas(self, *args)

        self.columnconfigure(1, weight=1)

        self._canvas.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
        self._button.grid(row=1, column=0, columnspan=2)

        self._canvas_hist = rsvis.tools.rescanvas.ResizingCanvas(self)
        self.update_histogram()
        self._canvas_hist(row=0, column=1, columnspan=2, sticky=N+S+W+E)

        self._slider_mean.set(0.0)
        self._slider_std.set(0.0)
        self._slider_std.grid(row=0, column=2, sticky=N+S)

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
        self.set_img()
        self.update_histogram()
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self._command()

    