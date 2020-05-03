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

import rsvis.tools.canvas_image
import rsvis.tools.settingsbox
import rsvis.tools.topwindow

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
        self._index_spec = rsvis.utils.index.Index(len(self._data[0]))
        self._index_channel = None

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
        self.window.mainloop()

    def initialize_window(self):
        self.window = Tk()
        self.window.title(
            "RSVis - Exploring and viewing RS data"
        )
        self.window.geometry("1000x700")
        # https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        self.menubar = Menu(self.window)
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open")
        # Save the currently displayed image to a given folder.
        filemenu.add_command(label="Save", command=lambda obj=self: obj._img_out(obj.get_img(path=True), obj.get_window_img(), prefix=obj.get_label()))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        
        self.add_option_menu(self._options, label="Options")
        self.window.config(menu=self.menubar)
        
        infomenu = Menu(self.menubar, tearoff=0)
        infomenu.add_command(label="Help", command=self.show_help)
        self.menubar.add_cascade(label="Information", menu=infomenu)

        self.window.columnconfigure(0)
        self.window.columnconfigure(1)
        self.window.columnconfigure(2, weight=1)
        self.window.rowconfigure(0, pad=3, weight=1)
        self.window.rowconfigure(1, pad=3)
        self.window.rowconfigure(2, pad=3)
        self.window.rowconfigure(3, pad=3)

        self.scrollbar = Scrollbar(self.window, orient="vertical", width=16)
        self.listbox = Listbox(self.window, yscrollcommand=self.scrollbar.set, width=37)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=0, sticky=N+S)
        self.listbox.grid(row=0, column=1, sticky=N+S)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_event)
        for count, item in enumerate(self._data):
           self.listbox.insert(END, pathlib.Path(item[0].path).stem)
        self.set_img_from_index()

        self.cbox_area = rsvis.tools.settingsbox.ComboBox(self.window, "Histogram", ["Grid", "Objects"], self.set_area_event)
        self.cbox_area.grid(row=1, column=0, columnspan=2, sticky=N+S)

        self.cbox_class = rsvis.tools.settingsbox.ComboBox(self.window, "Class", [c["name"] for c in self._classes], self.set_class )
        self.cbox_class.grid(row=2, column=0, columnspan=2, sticky=N+S)

        self.grid_settingsbox = rsvis.tools.settingsbox.SettingsBox(self.window,  ["Dimension x (Grid)", "Dimension y (Grid)"],  self.set_grid, default=self._grid)
        self.grid_settingsbox.grid(row=3, column=0, columnspan=2, sticky=N+S)
        self.grid_settingsbox.button_set.grid(row=4, column=0, columnspan=2,)
    
        self.canvas = rsvis.tools.canvas_image.ImageCanvas(self.window, bg="black", grid=self._grid, double_button=self.new_popup, classes=self._classes, logger=self._logger)
        self.set_img(self.img, show=True)
        self.canvas.grid(row=0, column=2, rowspan=5, sticky=N+S+E+W)
        
        self.window.bind("<F1>", self.show_help)
        self.canvas.bind("<Key>", self.key_event)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def invoke(self, command):
        return command(self)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_option_menu(self, options, label="Default"):
        optionmenu = Menu(self.menubar, tearoff=0)
        for option in options: 
            optionmenu.add_command(label=option["name"], command=lambda cmd=option["command"]: self.invoke(cmd))
        
        self.menubar.add_cascade(label=label, menu=optionmenu)

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
    def new_popup(self, title="Box", dtype="msg", value=""):
        t = rsvis.tools.topwindow.TopWindow(self.window, title=title, dtype=dtype, value=value, command=self.quit_window)
        t.wm_deiconify()
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
    def get_label(self):
        img_container = self._data[self._index()][self._index_spec()]
        return img_container.spec

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_path(self):
        img_container = self._data[self._index()][self._index_spec()]
        return img_container.path

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
                img = imgtools.project_and_stack(img[..., self._index_channel()], dtype=np.uint8, factor=255)
                return img
        return img

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_window_img(self):
        return self.img.copy()

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
    def get_obj_path(self):
        
        try: 
            import pathlib
            path = self._get_obj_path(self.get_path())
            if pathlib.Path(path).is_file():
                return path
        except TypeError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, show=False):
        self.img = img

        if show:
            objects = list()
            path = self.get_obj_path()
            if path:
                objects=rsvis.utils.yaml.yaml_to_data(path)

            self.canvas.set_img(self.img, objects=objects)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def listbox_event(self,event):
        self._index(index=self.listbox.curselection()[0])
        self.set_img_from_index(show=True)

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
    def key_q(self, **kwargs):
        """Exit RSVis."""
        self.window.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        self.canvas.remove_object()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def save_object(self):
        rsvis.utils.yaml.data_to_yaml(self.get_obj_path(), self.canvas.get_objects())        
        

