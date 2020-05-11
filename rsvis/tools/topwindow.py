# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.imgcontainer

import rsvis.tools.extcanvas
import rsvis.tools.imgconcanvas
import rsvis.tools.keys
import rsvis.tools.rescanvas
import rsvis.tools.widgets

import rsvis.tools.rscanvasframe

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
            title="Box",  
            dtype="msg", 
            value="",
            command=None,
            options=list(),
            label=None,
            histogram=False
        ):

        #   settings --------------------------------------------------------
        Toplevel.__init__(self, parent)
        self.wm_title(title)

        self._label = label
        self._histogram_flag = histogram
        self._menubar_flag = False

        #   general window settings -----------------------------------------
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        #   key bindings ----------------------------------------------------
        self.bind("<q>", self.key_q)
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)      
        self.bind("<u>", self.key_u)

        self._keys = { 
            "q": "Exit RSVis.",
            "u": "Update the histogram due to changes in image canvas."
        }

        for o in options:
            if o["key"] is not None:
                self._keys.update({o["key"]: o["description"]}) 

        #   main image window -----------------------------------------------
        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":
            self.set_canvas(value)

        #   button (Quit) ---------------------------------------------------
        if command is not None:
            self._command = lambda toplevel=self, title=title: command(toplevel, title)
            button = ttk.Button(self, text="OK", 
                command=self._command
            )
            button.grid(row=1, column=0, columnspan=2)
        
        #   menubar (Options) -----------------------------------------------
        if self._menubar_flag and options:
            self._menubar = Menu(self)
            rsvis.tools.widgets.add_option_menu(self._menubar, options, self, self._canvas, label="Options")
            rsvis.tools.widgets.add_info_menu(self._menubar, self, self, lambda obj=self, parent=parent: self.show_help(parent))
            self.config(menu=self._menubar)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_help(self, parent):
        """Show help."""

        keys = ""
        for key, description in rsvis.tools.keys.update_key_list([self._keys, self._canvas.get_keys()]).items():
            keys = "{}\n{}: {}".format(keys, [key], description)

        rsvis.tools.widgets.set_popup(parent, title="Help", dtype="msg", value=keys)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)# anchor='w' ttk?

        frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, value):
        columnspan=1 if self._histogram_flag else 2
        img = value
        if isinstance(value,rsvis.utils.imgcontainer.ImgListContainer):
            self._canvas = rsvis.tools.imgconcanvas.ImgConCanvas(self)
            self._canvas.set_img_container(value)
            img = self._canvas.get_img()

            self._menubar_flag = True
        else:
            self._canvas = rsvis.tools.extcanvas.ExtendedCanvas(self)
            self._canvas.set_img(value)

        self._canvas.grid(row=0, column=0, columnspan=columnspan, sticky=N+S+W+E)

        if self._histogram_flag:
            self.set_canvas_histogram(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas_histogram(self, img):
        self._canvas_hist = rsvis.tools.rescanvas.ResizingCanvas(self)
        self._canvas_hist.set_img(imgtools.get_histogram(img))
        
        self._canvas_hist.grid(row=0, column=1, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_histogram(self, event=None, **kwargs):
        if self._histogram_flag:
            self._canvas_hist.set_img(
                imgtools.get_histogram(self._canvas.get_img())
            )

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
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self._command()

    