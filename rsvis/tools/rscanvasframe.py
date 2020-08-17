# ===========================================================================
#   rscanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.tools.canvas import rsviscv

import numpy as np
import pathlib
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Listbox, Scrollbar, END, N, W, E, S, UNDERLINE

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSVisCanvasFrame(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent,
        images, 
        data,
        **kwargs
    ):
        super(RSVisCanvasFrame, self).__init__(parent)

        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.scrollbar = Scrollbar(self, orient="vertical", width=16)
        self.listbox = Listbox(self, yscrollcommand=self.scrollbar.set, width=37, activestyle=UNDERLINE)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=0, sticky=N+S)
        self.listbox.grid(row=0, column=1, sticky=N+S)
        for count, item in enumerate(data.get_img_in()):
            self.listbox.insert(END, pathlib.Path(item[0].path).stem)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_event)

        self._canvas = rsviscv.RSVisCanvas(self, data, **kwargs)
        self._canvas.set_container()
        self._canvas.grid(row=0, column=2, sticky=N+S+E+W)

        # parent.bind("<a>", self.key_a)
        # parent.bind("<d>", self.key_d)  

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def listbox_event(self,event):
        try:
            self._canvas._idx_list(index=self.listbox.curselection()[0])
            self._canvas.set_container()
        except IndexError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_listbox(self, event):
        self.listbox.activate(self._canvas.get_idx_list())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, event, **kwargs):
        """Show the previous image in given image list (see listbox)."""
        self.update_listbox(event)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, event, **kwargs):
        """Show the next image in given image list (see listbox)."""
        self.update_listbox(event)