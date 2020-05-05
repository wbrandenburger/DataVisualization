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

import rsvis.tools.imgcanvas
import rsvis.tools.settingsbox
import rsvis.tools.topwindow
import rsvis.tools.widgets

from tkinter import *
import numpy as np
import pandas as pd
import pathlib 

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
        self._data = data
        self._img_out = img_out

        self._options = options
        self.set_options(self._options)

        self._index = rsvis.utils.index.Index(len(self._data))
        self._logger = logger

        self._popup_help = 0
        
        self._grid = grid if grid else [2, 2]

        self._classes = classes
        self._settings= dict()
        self._get_obj_path = glu.PathCreator(**objects)

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
        self._root.columnconfigure(0)
        self._root.columnconfigure(1)
        self._root.columnconfigure(2, weight=1)
        self._root.rowconfigure(0, pad=3, weight=1)
        self._root.rowconfigure(1, pad=3)
        self._root.rowconfigure(2, pad=3)
        self._root.rowconfigure(3, pad=3)

        self.scrollbar = Scrollbar(self._root, orient="vertical", width=16)
        self.listbox = Listbox(self._root, yscrollcommand=self.scrollbar.set, width=37)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=0, sticky=N+S)
        self.listbox.grid(row=0, column=1, sticky=N+S)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_event)
        for count, item in enumerate(self._data):
           self.listbox.insert(END, pathlib.Path(item[0].path).stem)

        self.cbox_area = rsvis.tools.settingsbox.ComboBox(self._root, "Histogram", ["Grid", "Objects"], self.set_area_event)
        self.cbox_area.grid(row=1, column=0, columnspan=2, sticky=N+S)

        self.cbox_class = rsvis.tools.settingsbox.ComboBox(self._root, "Class", [c["name"] for c in self._classes], self.set_class )
        self.cbox_class.grid(row=2, column=0, columnspan=2, sticky=N+S)

        self.grid_settingsbox = rsvis.tools.settingsbox.SettingsBox(self._root,  ["Dimension x (Grid)", "Dimension y (Grid)"],  self.set_grid, default=self._grid)
        self.grid_settingsbox.grid(row=3, column=0, columnspan=2, sticky=N+S)
        self.grid_settingsbox.button_set.grid(row=4, column=0, columnspan=2,)
    
        self.canvas = rsvis.tools.imgcanvas.ImageCanvas(self._root, bg="black", grid=self._grid, double_button=self.new_popup, classes=self._classes, logger=self._logger)
        self.set_img_container()
        self.canvas.grid(row=0, column=2, rowspan=5, sticky=N+S+E+W)
        
        self._menubar = Menu(self._root)
        filemenu = Menu(self._menubar, tearoff=0)
        filemenu.add_command(label="Open")
        # Save the currently displayed image to a given folder.
        filemenu.add_command(label="Save", command=lambda obj=self: obj._img_out(obj.get_img_path(), obj.get_img(), prefix=obj.get_img_spec()))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._root.quit)
        self._menubar.add_cascade(label="File", menu=filemenu)
        ##########
        rsvis.tools.widgets.add_option_menu(self._menubar, self._options, self,label="Options")
        #self.add_option_menu(self._options, self, label="Options")

        infomenu = Menu(self._menubar, tearoff=0)
        infomenu.add_command(label="Help", command=self.show_help)
        self._menubar.add_cascade(label="Information", menu=infomenu)

        self._root.config(menu=self._menubar)
        
        self._root.bind("<F1>", self.show_help)
        self.canvas.bind("<Key>", self.key_event)
        
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
        t = rsvis.tools.topwindow.TopWindow(self._root, title=title, dtype=dtype, value=value, command=self.quit_window, menubar=self._options, **kwargs)
        t.mainloop()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, event=None):
        self.canvas.set_class(self.cbox_class.get()["label"])
        self.cbox_area.set_choice("Objects")
        self.set_area_event()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self, entries):
        grid = [0, 0]
        for index, entry in enumerate(entries):
            grid[index]  = int(entry[1].get())
        self.canvas.set_grid(grid)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_grid(self):
        self.canvas.show_grid()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, event=None):
        self.canvas.set_area_event(**self.cbox_area.get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_objects(self):
        self.canvas.show_objects()
        if self.canvas.obj:
            self.cbox_area.set_choice("Objects")
            self.set_area_event()
            
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
    def listbox_event(self,event):
        self._index(index=self.listbox.curselection()[0])
        self.set_img_container()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, **kwargs):
        """Display the next image in given list."""
        index = self._index.next()
        self.listbox.activate(index)
        self.set_img_container()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, **kwargs):
        """Display the previous image in given list.""",
        index = self._index.last()
        self.listbox.activate(index)
        self.set_img_container()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, **kwargs):
        """Exit RSVis."""
        self._root.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, show=False):
        self.img = img
        self.canvas.set_img(self.img, objects=self.get_object())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_container(self, index=None):
        self.canvas.set_img_container(self._data[self._index()], objects=self.get_object())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img(self):
        return self.canvas.get_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_spec(self):
        try:
            return self.canvas.get_img_container().spec
        except AttributeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_path(self):
        try:
            return self.canvas.get_img_container().path
        except AttributeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_spec(self, spec):
        try:
            return self.canvas.get_img_from_spec(spec)
        except AttributeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object(self):
        if self.get_obj_path():
            return rsvis.utils.yaml.yaml_to_data(self.get_obj_path())
        return list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_path(self):
        try: 
            path = self._get_obj_path(self._data[self._index()][0].path)
            if pathlib.Path(path).is_file():
                return path
        except TypeError:
            return

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        self.canvas.remove_object()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def save_object(self):
        rsvis.utils.yaml.data_to_yaml(self.get_obj_path(), self.canvas.get_objects())  

