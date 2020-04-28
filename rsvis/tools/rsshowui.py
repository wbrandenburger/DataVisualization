# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.index
from rsvis.utils import imgtools
import rsvis.utils.imgio
import rsvis.utils.format

import rsvis.tools.canvas
import rsvis.tools.settingsbox
import rsvis.tools.topwindow

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import pathlib 

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_number_of_channel(img):
    if len(img.shape) == 3:
        return img.shape[2]
    return None

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def quit_window(window):
    """Exit Window."""   
    # window.quit()
    window.destroy()

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSShowUI():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, data, keys=dict(), description=dict(), grid=list(), logger=None, **kwargs):
        self._data = data
        self.set_keys(keys, description=description)

        self._index = rsvis.utils.index.Index(len(self._data))
        self._index_spec = rsvis.utils.index.Index(len(self._data[0]))
        self._index_channel = None

        self._logger = logger

        self._popup_help = 0
        
        self._grid = grid if grid else [2, 2]

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
    def set_keys(self, keys, description=dict()):
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
        self._keys_description.update(description)

        if isinstance(keys, dict):
            self._keys = keys
        else:
            self._keys = dict()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_key_description(self):
        return pd.DataFrame.from_dict(self._keys_description, orient="index", columns=["Description"]).to_string()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imshow(self, wait=False):
        self.window.mainloop()

    def initialize_window(self):
        self.window = Tk()
        self.window.title(
            "RSVis - Visualization for Aerial and Satellite Datasets"
        )
        self.window.geometry("1000x700")
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        self.menubar = Menu(self.window)
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Help", command=self.show_help)
        self.menubar.add_cascade(label="Information", menu=editmenu)

        self.window.config(menu=self.menubar)

        self.window.columnconfigure(0)
        self.window.columnconfigure(1)
        self.window.columnconfigure(2, weight=1)
        self.window.rowconfigure(0, pad=3, weight=1)
        self.window.rowconfigure(1, pad=3)

        self.scrollbar = Scrollbar(self.window, orient="vertical", width=16)
        self.listbox = Listbox(self.window, yscrollcommand=self.scrollbar.set, width=30)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=0, sticky=N+S)
        self.listbox.grid(row=0, column=1, sticky=N+S)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_event)
        for count, item in enumerate(self._data):
           self.listbox.insert(END, pathlib.Path(item[0].path).stem)
        self.set_img_from_index()
        
        self.settingsbox = rsvis.tools.settingsbox.SettingsBox(self.window,  ["Dimension x", "Dimension y"],  self.set_grid_settings, default=self._grid)
        self.settingsbox.grid(row=1, column=0, columnspan=2, sticky=N+S)
        self.settingsbox.button_set.grid(row=2, column=0, columnspan=2)

        self.canvas = rsvis.tools.canvas.ImageCanvas(self.window, bg="black", grid=self._grid, double_button=self.new_popup, logger=self._logger)
        self.canvas.set_img(self.img)
        self.canvas.grid(row=0, column=2, rowspan=3, sticky=N+S+E+W)
        
        self.window.bind("<F1>", self.show_help)
        self.window.bind("<Key>", self.key_event)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_menu(self, label, menu=dict()):
        labelmenu = Menu(self.menubar, tearoff=0)
        for key in menu.keys(): 
            print(key)
            labelmenu.add_command(label=key, command=(lambda obj=self: menu[key](obj)))

        self.menubar.add_cascade(label=label, menu=labelmenu)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def new_popup(self, title="Box", dtype="msg", value=""):
        t = rsvis.tools.topwindow.TopWindow(title=title, dtype=dtype, value=value, command=quit_window)
        t.wm_deiconify()
        t.mainloop()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid_settings(self, entries):
        grid = [0, 0]
        for index, entry in enumerate(entries):
            grid[index]  = int(entry[1].get())
        self.canvas.set_grid_settings(grid)
        self.canvas.show_img()

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
            self.new_popup(title="Help", dtype="msg", msg=self.get_key_description())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img(self, index=None, path=False, show=True):
        index = self._index_spec() if not index else index
        img_container = self._data[self._index()][index]

        if path:
            return img_container.path
        else:
            img = img_container.data
            self.get_log(img_container)
            if show:
                if get_number_of_channel(img) > 3:
                    img = self.get_img_channel(img=img)

        return img

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log(self, img_container):
        try: 
            import pathlib
            log = img_container.log
            if pathlib.Path(log).is_file():
                print(rsvis.utils.imgio.read_log(log))
        except TypeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_channel(self, index=None, img=np.ndarray(0)):
        index = self._index_spec() if not index else index
        img_container = self._data[self._index()][index]
        
        if not len(img):
            img = img_container.data

        if not isinstance(self._index_channel, rsvis.utils.index.Index):
            if get_number_of_channel(img):
                self._index_channel = rsvis.utils.index.Index(get_number_of_channel(img))
        
        if isinstance(self._index_channel, rsvis.utils.index.Index):
            number_channel = get_number_of_channel(img)
            if number_channel:
                img = imgtools.project_and_stack(img[..., self._index_channel()])
                return img

        return img

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_window_img(self):
        return self.img

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_spec(self, spec, path=False, show=True):
        if spec:
            try:
                index = self._data[self._index()].index(spec)
                return self.get_img(index=index, path=path, show=show)
            except ValueError:
                return None 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_from_index(self, index=None, show=False):
        self.set_img(self.get_img(index=index), show=show)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, show=False):
        self.img = img
        if show:
            self.canvas.set_img(self.img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def listbox_event(self,event):
        self._index(index=self.listbox.curselection()[0])
        self.set_img_from_index(show=True)

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
    def key_d(self, **kwargs):
        """Display the next image in given list."""
        index = self._index.next()
        self.listbox.activate(index)
        self.set_img_from_index(show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, **kwargs):
        """Display the previous image in given list.""",
        index = self._index.last()
        self.listbox.activate(index)
        self.set_img_from_index(show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, **kwargs):
        """Display the next image of the given image set.""",
        self._index_spec.next()
        self._index_channel = None
        self.set_img_from_index(show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, **kwargs):
        """Display the previous image of the given image set.""",
        self._index_spec.last()
        self._index_channel = None
        self.set_img_from_index(show=True)     

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_x(self, **kwargs):
        """Display the next single channel of cuurent image."""
        if isinstance(self._index_channel, rsvis.utils.index.Index):
            self._index_channel.next()
        self.set_img(self.get_img_channel(), show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_y(self, **kwargs):
        """Display the previous single channel of current image."""
        if isinstance(self._index_channel, rsvis.utils.index.Index):
            self._index_channel.last()
        self.set_img(self.get_img_channel(), show=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_g(self, **kwargs):
        """Show grid lines in current image."""
        self.canvas.set_grid()
        self.canvas.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, **kwargs):
        """Exit RSVis."""
        self.window.destroy()

        

