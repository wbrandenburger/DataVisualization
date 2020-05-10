# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
import rsvis.utils.index
from rsvis.utils import imgtools
import rsvis.utils.imgio
import rsvis.utils.format
import rsvis.utils.yaml

import rsvis.tools.rscanvasframe
import rsvis.tools.settingsbox
import rsvis.tools.topwindow
import rsvis.tools.widgets

from tkinter import *
import numpy as np
import pandas as pd
import pathlib 

import subprocess as sub

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_number_of_channel(img):
    if len(img.shape) == 3:
        return img.shape[2]
    return None

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSShowUI():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, data, options=list(), grid=list(), classes=dict, logger=None, **kwargs):
        
        self._data = data
    
        self._options = options
        self.set_options(self._options)

        self._popup_help = 0

        self.initialize_window(grid=grid, classes=classes, logger=logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_options(self, options):
        self._keys_description = {
            "F1" : "Show help.",
            "q" : "Exit RSVis.",
            "d" : "Display the next image in given list.",
            "a" : "Display the previous image in given list.",
            "w" : "Display the next image of the given image set.",
            "s" : "Display the previous image of the given image set.",
            "x" : "Display the next single channel of cuurent image.",
            "y" : "Display the previous single channel of current image."
        }

        self._keys = dict()
        for option in options:
            if option["key"] is not None:
                self._keys_description[option["key"]] = option["description"]
                self._keys["key_{}".format(option["key"])] = option["command"]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_key_description(self):
        return pd.DataFrame.from_dict(self._keys_description, orient="index", columns=["Description"]).to_string()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imshow(self, wait=False):
        """Start the mainloop for displaying the graphical user interface"""
        self._root.mainloop()

    def initialize_window(self, grid=list(), classes=dict(), logger=None):
        """Set the geometry of the main window"""

        #   settings --------------------------------------------------------
        self._root = Tk()
        grid = grid if grid else [2,2]

        #   general window settings -----------------------------------------
        self._root.title(
            "RSVis - Exploring and Viewing RS-Data"
        )
        self._root.geometry("1000x700")
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        #   comboboxes (mouse behavior/ classes) ----------------------------
        self.cbox_area = rsvis.tools.settingsbox.ComboBox(self._root, "Histogram", ["Grid", "Objects"], self.set_area_event)
        self.cbox_area.grid(row=1, column=0, sticky=N+W+S)
        self.cbox_class = rsvis.tools.settingsbox.ComboBox(self._root, "Class", [c["name"] for c in classes], self.set_class )
        self.cbox_class.grid(row=2, column=0, sticky=N+W+S)

        #   settingsboxes (grid) --------------------------------------------
        self.grid_settingsbox = rsvis.tools.settingsbox.SettingsBox(self._root,  ["Dimension x (Grid)", "Dimension y (Grid)"],  self.set_grid, default=grid)
        self.grid_settingsbox.grid(row=3, column=0, sticky=N+W+S)
    
        #   main image window -----------------------------------------------
        self._frame = rsvis.tools.rscanvasframe.RSCanvasFrame(self._root, self._data.get_img_in(), self._data, bg="black", grid=grid, popup=self.set_popup, classes=classes, logger=logger)
        self._frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)

        #   menubar (File / Options / Information) --------------------------
        self._menubar = Menu(self._root)

        #   menubar "File"
        filemenu = Menu(self._menubar, tearoff=0)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save", command=lambda obj=self._frame._canvas, img_out=self._data.get_img_out(): img_out(obj.get_img_path(), obj.get_img(), prefix=obj.get_img_spec()))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._root.quit)
        self._menubar.add_cascade(label="File", menu=filemenu)

        #   menubar "Information"
        infomenu = Menu(self._menubar, tearoff=0)
        infomenu.add_command(label="Help", command=self.show_help)
        self._menubar.add_cascade(label="Information", menu=infomenu)

        #   menubar "Options"
        rsvis.tools.widgets.add_option_menu(self._menubar, self._options, self._frame._canvas, label="Options")
        
        self._root.config(menu=self._menubar)
        #   key bindings ----------------------------------------------------
        self._root.bind("<F1>", self.show_help)
        self._root.bind("q", self.key_q)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup(self, title="Box", dtype="msg", value="", **kwargs):
        t = rsvis.tools.topwindow.TopWindow(self._root, title=title, dtype=dtype, value=value, command=self.quit, menubar=[m for m in self._options if m["label"] in ["image", "label", "height"]], **kwargs)
        t.mainloop()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, event=None):
        self._frame._canvas.set_class(self.cbox_class.get()["label"])
        self.cbox_area.set_choice("Objects")
        self.set_area_event()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self, entries):
        grid = [0, 0]
        for index, entry in enumerate(entries):
            grid[index]  = int(entry[1].get())
        self._frame._canvas.set_grid(grid)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_grid(self):
        self._frame._canvas.show_grid()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, event=None):
        self._frame._canvas.set_area_event(**self.cbox_area.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def quit(self, window, title=None, **kwargs):
        """Exit RSVis."""   
        if title=="Help":
            self._popup_help = 0
        window.quit()
        window.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_help(self, event=None):
        """Show help."""
        if not self._popup_help:
            self._popup_help = 1
            self.set_popup(title="Help", dtype="msg", value=self.get_key_description())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self.quit(self._root)