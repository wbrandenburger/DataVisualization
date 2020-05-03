# ===========================================================================
#   topwindow.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.canvas_resizing

from PIL import Image, ImageTk
from tkinter import Toplevel, ttk, Button, Canvas, Label, TOP, X, NW, N, W, S, E, CENTER

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TopWindow(Toplevel):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, title="Box", command=None, dtype="msg", value=""):
        Toplevel.__init__(self, parent)
        self.wm_title(title)

        if dtype=="msg":
            self.set_msg(value)
        elif dtype=="img":
            if isinstance(value, list):
                self.set_canvas_grid(value)
            else: 
                self.set_canvas(value)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1)

        button = ttk.Button(self, text="OK", 
            command=lambda toplevel=self, title=title: command(toplevel, title)
        )
        button.grid(row=1, column=0, columnspan=2)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_msg(self, msg):
        frame = ttk.Label(self, text=msg)# anchor='w' ttk?

        frame.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img):
        canvas = rsvis.tools.canvas_resizing.ResizingCanvas(self, bg="black")
        canvas.set_img(img)

        canvas.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas_grid(self, img):

        for index, item in enumerate(img):
            canvas = rsvis.tools.canvas_resizing.ResizingCanvas(self, bg="black")
            canvas.set_img(item)
            
            canvas.grid(row=0, column=index, sticky=N+S+W+E)