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

import numpy as np
from PIL import Image, ImageTk
from tkinter import Toplevel, ttk, Button, Canvas, Label, Menu, TOP, X, NW, N, W, S, E, CENTER

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindow(Toplevel):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            title="Message Canvas",  
            dtype="msg", 
            value="",
            q_cmd=None,
            options=list(),
            logger=None,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        Toplevel.__init__(self, parent)
        self.wm_title(title)

        self._menubar_flag = False
        self._logger = logger
        
        #   general window settings -----------------------------------------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        #   key bindings ----------------------------------------------------
        self.bind("<q>", self.key_q)
        self.bind("<e>", self.key_e)

        self._keys = { 
            "q": "Exit RSVis.",
            "e": "Set current image for processing."
        }

        for o in options:
            if o["key"] is not None:
                self._keys.update({o["key"]: o["description"]}) 

        #   button (Quit) ---------------------------------------------------
        self._q_cmd = lambda toplevel=self, title=title: q_cmd(toplevel, title)
        self._button = ttk.Button(self, text="OK", 
            command=self._q_cmd
        )
        self._button.grid(row=1, column=0, columnspan=1)

        #   main image window -----------------------------------------------
        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":
            self.set_canvas(value)
        
        #   menubar (Options) -----------------------------------------------
        if self._menubar_flag and options:
            self._menubar = Menu(self)
            rsvis.tools.widgets.add_option_menu(self._menubar, options, self, self._canvas, label="Options")
            rsvis.tools.widgets.add_info_menu(self._menubar, self, self, lambda obj=self, parent=parent: self.show_help(parent))
            self.config(menu=self._menubar)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup(self, dtype="msg", histogram=False, **kwargs):
        kwargs.update(
            {"dtype": dtype, "q_cmd": self._q_cmd, "logger": self._logger}
        )
        t = TopWindow(self, **kwargs)
        t.mainloop()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_help(self, parent):
        """Show help."""
        keys = ""
        for key, description in rsvis.tools.keys.update_key_list([self._keys, self._canvas.get_keys()]).items():
            keys = "{}\n{}: {}".format(keys, [key], description)

        self.set_popup(parent, title="Help", dtype="msg", value=keys)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)

        frame.grid(row=0, column=0, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self):
        self._img = self._canvas.get_img()
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, value):
        self._img = value
        if isinstance(value, rsvis.utils.imgcontainer.ImgListContainer):
            self._canvas = rsvis.tools.imgconcanvas.ImgConCanvas(self, logger=self._logger)
            self._canvas.set_img_container(value)
            self._img = self._canvas.get_img()

            self._menubar_flag = True
        else:
            self._canvas = rsvis.tools.extcanvas.ExtendedCanvas(self)
            self._canvas.set_img(value)

        self._canvas.grid(row=0, column=0, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_e(self, event, **kwargs):
        """Exit RSVis."""
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self._q_cmd()

    