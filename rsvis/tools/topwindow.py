# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools

import rsvis.tools.extcanvas
import rsvis.tools.rescanvas
import rsvis.tools.widgets


from PIL import Image, ImageTk
from tkinter import Toplevel, ttk, Button, Canvas, Label, Menu, TOP, X, NW, N, W, S, E, CENTER

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindow(Toplevel):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, title="Box", command=None, dtype="msg", value="", histogram=False, container=False, menubar=None):
        Toplevel.__init__(self, parent)
        self.wm_title(title)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1)

        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":
            if container:
                self.set_canvas_container(value)
            else:
                if histogram:
                    self.set_canvas_histogram(value)
                else: 
                    self.set_canvas(value)

        self._command = lambda toplevel=self, title=title: command(toplevel, title)
        button = ttk.Button(self, text="OK", 
            command=self._command
        )
        button.grid(row=1, column=0, columnspan=2)
        
        if container and menubar:
            self._menubar = Menu(self)
            rsvis.tools.widgets.add_option_menu(self._menubar, menubar, self._canvas, label="Options")
            self.config(menu=self._menubar)

        self.bind("<q>", self.key_q)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)# anchor='w' ttk?

        frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas_container(self, container, columnspan=2):
        self._canvas = rsvis.tools.imgconcanvas.ImageContainerCanvas(self, bg="black")
        self._canvas.set_img_container(container)

        self._canvas.grid(row=0, column=0, columnspan=columnspan, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, columnspan=2):
        canvas = rsvis.tools.extcanvas.ExtendedCanvas(self, bg="black")
        canvas.set_img(img)

        canvas.grid(row=0, column=0, columnspan=columnspan, sticky=N+S+W+E)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas_histogram(self, img):
        self.set_canvas(img, columnspan=1)

        canvas = rsvis.tools.rescanvas.ResizingCanvas(self, bg="black")
        canvas.set_img(imgtools.get_histogram(img))
        
        canvas.grid(row=0, column=1, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, event, **kwargs):
        """Exit RSVis."""
        self._command()