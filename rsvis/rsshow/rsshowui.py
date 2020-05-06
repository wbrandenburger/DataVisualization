# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as glu
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
    def __init__(self, data, img_out, options=list(), grid=list(), classes=dict, objects=dict(), logger=None, **kwargs):
        
        self._img_out = img_out
        self._data = data

        self._options = options
        self._get_obj_path = glu.PathCreator(**objects)
        self.set_options(self._options)

        self._logger = logger

        self._popup_help = 0
        
        self._grid = grid if grid else [2, 2]

        self._classes = classes
        self._settings= dict()

        self.initialize_window()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def logger(self, log_str, stream="info"):
        if self._logger is None:
            return

        if stream == "info":
            self._logger.info(log_str)
        elif stream == "debug":
            self._logger.debug(log_str)
   
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
            "y" : "Display the previous single channel of current image.",
            "g" : "Show grid lines in current image.",
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
        self._root.mainloop()

    def initialize_window(self):
        self._root = Tk()
        self._root.title(
            "RSVis - Exploring and Viewing RS-Data"
        )
        self._root.geometry("1000x700")
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1)
        self._root.rowconfigure(2)
        self._root.rowconfigure(3)

        self.cbox_area = rsvis.tools.settingsbox.ComboBox(self._root, "Histogram", ["Grid", "Objects"], self.set_area_event)
        self.cbox_area.grid(row=1, column=0, sticky=N+W+S)

        self.cbox_class = rsvis.tools.settingsbox.ComboBox(self._root, "Class", [c["name"] for c in self._classes], self.set_class )
        self.cbox_class.grid(row=2, column=0, sticky=N+W+S)

        self.grid_settingsbox = rsvis.tools.settingsbox.SettingsBox(self._root,  ["Dimension x (Grid)", "Dimension y (Grid)"],  self.set_grid, default=self._grid)
        self.grid_settingsbox.grid(row=3, column=0, sticky=N+W+S)
    
        self._frame = rsvis.tools.rscanvasframe.RSCanvasFrame(self._root, self._data, bg="black", grid=self._grid, obj_path=self._get_obj_path, popup=self.new_popup, classes=self._classes, logger=self._logger)
        self._frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
        
        self._menubar = Menu(self._root)
        filemenu = Menu(self._menubar, tearoff=0)
        filemenu.add_command(label="Open")
        # Save the currently displayed image to a given folder.
        filemenu.add_command(label="Save", command=lambda obj=self: obj._img_out(obj.get_img_path(), obj.get_img(), prefix=obj.get_img_from_spec()))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._root.quit)
        self._menubar.add_cascade(label="File", menu=filemenu)
        ##########
        rsvis.tools.widgets.add_option_menu(self._menubar, self._options, self._frame._canvas, label="Options")
        #self.add_option_menu(self._options, self, label="Options")

        infomenu = Menu(self._menubar, tearoff=0)
        infomenu.add_command(label="Help", command=self.show_help)
        self._menubar.add_cascade(label="Information", menu=infomenu)
        self._root.config(menu=self._menubar)
        
        # https://stackoverflow.com/questions/665566/redirect-command-line-results-to-a-tkinter-gui

        self._root.bind("<F1>", self.show_help)
        self._root.bind("<Key>", self.key_event)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_key_event_name(self, arg):
        return 'key_' + str(arg)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def has_key(self, arg):
        return hasattr(self, self.get_key_event_name(arg)) or arg in self._keys 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_event(self, event):
        # Get the method from 'self'. Default to a lambda.
        key_event_name = self.get_key_event_name(event.char)

        if hasattr(self, key_event_name):
            method = getattr(self, key_event_name, lambda: "Invalid key")
            # Call the method as we return it
            return method()
        elif key_event_name in self._keys:
            # param = [self.show(index=p) for p in self._keys[key_event_name]["param"]]
            return self._keys[key_event_name](self) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def new_popup(self, title="Box", dtype="msg", value="", **kwargs):
        t = rsvis.tools.topwindow.TopWindow(self._root, title=title, dtype=dtype, value=value, command=self.quit_window, menubar=[m for m in self._options if m["label"] in ["image", "label", "height"]], **kwargs)
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
    def quit_window(self, window, title=None, **kwargs):
        """Exit Window."""
        if title=="Help":
            self._popup_help = 0       
        window.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def quit(self, window, **kwargs):
        """Exit RSVis."""   
        window.quit()
        window.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_help(self, event=None):
        """Show help."""
        if not self._popup_help:
            self._popup_help = 1
            self.new_popup(title="Help", dtype="msg", value=self.get_key_description())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log(self, img_container):
        try: 
            log = img_container.log
            if pathlib.Path(log).is_file():
                print(rsvis.utils.imgio.read_log(log))
        except TypeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, **kwargs):
        """Exit RSVis."""
        self._root.destroy()