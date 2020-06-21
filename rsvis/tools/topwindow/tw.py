# ===========================================================================
#   tw.py -------------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.canvas import imgcv, extimgcv, extimgconcv
from rsvis.tools.widgets import widgets

import math
import numpy as np
from tkinter import ttk
from tkinter import *

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
            canvas=dict(),
            logger=None,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        Toplevel.__init__(self, parent)
        self.wm_title(title)
        
        self._logger = logger
 
        #   general window settings -----------------------------------------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        #   key bindings ----------------------------------------------------
        self.bind("<q>", self.key_q)
        self.bind("<r>", self.key_r)

        self._keys = { 
            "q": "Exit RSVis.",
            "r": "Set currently displayed image for further analysis."
        }

        for o in options:
            if o["key"] is not None:
                self._keys.update({o["key"]: o["description"]}) 

        #   button (Quit) ---------------------------------------------------
        if q_cmd is not None:
            self._q_cmd = lambda toplevel=self, title=title: q_cmd(toplevel, title)
            self._button_quit = ttk.Button(self, text="OK", 
                command=self._q_cmd
            )
            self._button_quit.grid(row=1, column=0, columnspan=1)

        #   main image window -----------------------------------------------
        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":          
            self.set_canvas(value, **canvas)
        
        #   menubar (Options) -----------------------------------------------
        if options:
            self._menubar = Menu(self)
            widgets.add_option_menu(self._menubar, options, self, self._canvas)
            widgets.add_info_menu(self._menubar, self, self, lambda obj=self, parent=parent: self.show_help(parent))
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
    def get_obj(self):
        return self._canvas

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)

        frame.grid(row=0, column=0, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, **kwargs):
        self._img = self._canvas.get_img(show=True)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update(self, img, index=None, **kwargs):
        if index is None:
            self._canvas.set_img(img)
        else:
            self._canvas[index].set_img(img)
            
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, value, **kwargs):
        """Set the main image canvas with the image to be displayed
        """
        if isinstance(value, rsvis.utils.imgcontainer.ImgListContainer):
            self._canvas = extimgconcv.ExtendedImgConCv(self, logger=self._logger, **kwargs)
            self._canvas.set_img_container(value)
            self._img = self._canvas.get_img()
            self._canvas.grid(row=0, column=0, sticky=N+S+W+E)
        elif isinstance(value, np.ndarray):
            self._canvas = extimgcv.ExtendedImgCv(self)
            self._canvas.set_img(value)
            self._img = self._canvas.get_img()
            self._canvas.grid(row=0, column=0, sticky=N+S+W+E)
        elif isinstance(value, list):
            dim = math.ceil(math.sqrt(len(value))) if len(value) > 4 else len(value)
            grid = np.indices((dim, dim))
            grid_y = grid[0].reshape(dim**2)
            grid_x = grid[1].reshape(dim**2)
            
            self._canvas = list()
            for idx, img in enumerate(value):
                self._canvas.append(imgcv.ImgCanvas(self, logger=self._logger, **kwargs))

                self._canvas[-1].set_img(img)
                self._canvas[-1].grid(row=grid_y[idx], column=grid_x[idx], sticky=N+S+W+E)
                
                self.rowconfigure(grid_y[idx], weight=1)
                self.columnconfigure(grid_x[idx], weight=1)
                
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_r(self, event, **kwargs):
        """Set currently displayed image for further analysis."""
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self._q_cmd()
