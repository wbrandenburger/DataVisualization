# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
import rsvis.utils.index
from rsvis.utils import opener, imgtools
import rsvis.utils.logger
import rsvis.utils.yaml

import rsvis.tools.rscanvasframe
import rsvis.tools.keys
from rsvis.tools.widgets import settingsbox, combobox, widgets
from rsvis.tools.topwindow import tw, twhist, twhnormal, twhfilter, twhfeatures, twhlecture, twhseg

from tkinter import *
import numpy as np
import pandas as pd
import pathlib 

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSShowUI():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, data, options=list(), show=dict(), classes=dict, param=dict(), **kwargs):
        
        self._data = data
        self._options = options

        self._param = param

        self.initialize_window(show=show, classes=classes)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_key_description(self):
        return pd.DataFrame.from_dict(self._keys_description, orient="index", columns=["Description"]).to_string()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imshow(self, wait=False):
        """Start the mainloop for displaying the graphical user interface"""
        self._root.mainloop()

    def initialize_window(self, show=list(), classes=dict()):
        """Set the geometry of the main window"""

        #   settings --------------------------------------------------------
        self._root = Tk()
        show["grid"] = gu.get_value(show, "grid", [2,2])
        classes = classes if classes else [{"name": "Default", "color": [255, 255, 0]}]

        #   general window settings -----------------------------------------
        self._root.title(
            "RSVis - Exploring and Viewing RS-Data"
        )
        self._root.geometry("1100x900")
        self._root.columnconfigure(1, weight=1)
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=0)

        self._row_settings = 6

        #   key bindings ----------------------------------------------------
        self._root.bind("q", self.key_q)
        self._keys = {
                "q":  "Exit RSVis."
        }

        for o in self._options:
            if o["key"] is not None:
                self._keys.update({o["key"]: o["description"]}) 

        #   textfield (grid) ------------------------------------------------
        self._textbox_scrollbar = Scrollbar(self._root)
        self._textbox = Text(self._root, height=3, font=("Courier", 8))
        self._textbox_scrollbar.grid(row=1, column=2, rowspan=self._row_settings, sticky=N+S)
        self._textbox.grid(row=1, column=1, rowspan=self._row_settings, sticky=N+S+W+E)
        self._textbox_scrollbar.config(command=self._textbox.yview)
        self._textbox.config(yscrollcommand=self._textbox_scrollbar.set)
        
        #   set the input / output logger
        self._logger =  rsvis.utils.logger.Logger(logger=lambda log: self._textbox.insert("1.0", "{}\n".format(log)))
        self._data.logger = self._logger
        self._opener = opener.GeneralOpener(logger=self._logger)

        #   comboboxes (mouse behavior/ classes) ----------------------------
        self._cbox_area = combobox.ComboBox(self._root, [["Histogram"], [["Grid", "Objects"]], ["Grid"], ["str"]], func=self.set_area_event)
        self._cbox_area.grid(row=1, column=0, sticky=N+W+S+E)
        self._cbox_class = combobox.ComboBox(self._root, [["Class"], [[c["name"] for c in classes]], [classes[0]["name"]], ["str"]], func=self.set_class)
        self._cbox_class.grid(row=2, column=0, sticky=N+W+S+E)
        self._cbox_test =combobox.ComboBox(self._root, [["Testing"],  [self._param["vis"]["test_menu"]], [self._param["vis"]["test"]], ["str"]])
        self._cbox_test.grid(row=3, column=0, sticky=N+W+S+E)

        #   settingsboxes (label image) -------------------------------------
        self._sbox_label_img = settingsbox.SettingsBox(self._root, sbox=[["Label Image"], ["label"], ["str"]])
        self._sbox_label_img.grid(row=4, column=0, sticky=N+W+S+E)

        #   settingsboxes (label image) -------------------------------------
        self._sbox_height_img = settingsbox.SettingsBox(self._root, sbox=[["Height Image"], ["height"], ["str"]])
        self._sbox_height_img.grid(row=5, column=0, sticky=N+W+S+E)

        #   settingsboxes (grid) --------------------------------------------
        self._sbox_grid = settingsbox.SettingsBox(self._root, sbox=[["Dimension x (Grid)", "Dimension y (Grid)"], show["grid"], ["int", "int"]], func=self.set_grid)
        self._sbox_grid.grid(row=6, column=0, sticky=N+W+S+E)

        #   canvas variables ------------------------------------------------
        self._variables = {
            "class": lambda value=False: self._cbox_class.get(value=value),
            "labelimg": lambda: self._sbox_label_img.get(),
            "heightimg": lambda: self._sbox_height_img.get()
        }

        #   main image window -----------------------------------------------
        self._frame = rsvis.tools.rscanvasframe.RSVisCanvasFrame(self._root, self._data.get_img_in(), self._data, popup=self.set_popup, classes=classes, variables=self._variables, logger=self._logger, **show)
        self._frame.grid(row=0, column=0, columnspan=3, sticky=N+S+W+E)
        
        #   menubar (File / Options / Information) --------------------------
        self._menubar = Menu(self._root)

        #   menubar "File"
        filemenu = Menu(self._menubar, tearoff=0)
        filemenu.add_command(label="Open", command=lambda: self.open(self.get_img_path()))
        filemenu.add_command(label="Save", command=lambda obj=self.get_obj(), img_out=self._data.get_img_out(): img_out(obj.get_img_path(), obj.get_img(), prefix=obj.get_img_spec()))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=widgets.quit)
        self._menubar.add_cascade(label="File", menu=filemenu)

        #   menubar "Options"
        widgets.add_option_menu(self._menubar, self._options, self._root, self.get_obj())

        #   menubar "Information"
        widgets.add_info_menu(self._menubar, self._root, self._root, lambda obj=self: self.show_help())

        self._root.config(menu=self._menubar)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj(self):
        return self._frame._canvas
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_path(self):
        return self.get_obj().get_img_path()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_image(self):
        return self.get_obj().create_image()        

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open(self, path):
        self._opener("files", str(pathlib.Path(path).parent))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup(self, dtype="msg", histogram=False, **kwargs):
        kwargs.update(
            {"dtype": dtype, "q_cmd": self.quit, "logger": self._logger}
        )

        if dtype=="img":
            kwargs.update( 
                {
                    "options": [o for o in self._options],# if o["require"] in ["image", "basic", "label", "height"]],
                    "canvas":{
                        "variables": self._variables
                    }
                }
            )

            if histogram:
                if self._cbox_test.get() == "Histogram":
                    t = twhist.TWHist(self._root, **kwargs)
                elif self._cbox_test.get() == "Normal":
                    t = twhnormal.TWHNormal(self._root, self._param["cloud"], **kwargs)
                elif self._cbox_test.get() == "Filter":
                    t = twhfilter.TWHFilter(self._root, **kwargs)
                elif self._cbox_test.get() == "Features":
                    t = twhfeatures.TWHFeatures(self._root, **kwargs)
                elif self._cbox_test.get() == "Lecture":
                    t = twhlecture.TWHLecture(self._root,**kwargs)
                elif self._cbox_test.get() == "Segmentation":
                    t = twhseg.TWHSeg(self._root, **kwargs)
            else:
                t = tw.TopWindow(self._root, **kwargs)
        else:
            t = tw.TopWindow(self._root, **kwargs)
        t.mainloop()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, event=None):
        self._cbox_area.set_label("Objects")
        self.get_obj().set_label(self._cbox_class.get())
        self.set_area_event()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self):
        self.get_obj().set_grid(self._sbox_grid.get_list())
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, event=None):
        self.get_obj().set_area_event(index=["Grid", "Objects"].index(self._cbox_area.get()))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def quit(self, window, title=None, **kwargs):
        """Exit Window."""   
        # if title=="Help":
        #     self._popup_help = 0
        window.quit()
        window.destroy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_help(self):
        """Show help."""
        keys = ""
        for key, description in rsvis.tools.keys.update_key_list([self._keys, self.get_obj().get_keys()]).items():
            keys = "{}\n{}: {}".format(keys, [key], description)

        self.set_popup(title="Help", dtype="msg", value=keys)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self.quit(self._root)