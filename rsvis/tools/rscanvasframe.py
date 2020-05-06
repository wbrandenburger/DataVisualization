# ===========================================================================
#   rscanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.rscanvas

import numpy as np
import pathlib
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Listbox, Scrollbar, END, N, W, E, S

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSCanvasFrame(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        data,
        **kwargs
    ):
        super(RSCanvasFrame, self).__init__(parent)

        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.scrollbar = Scrollbar(self, orient="vertical", width=16)
        self.listbox = Listbox(self, yscrollcommand=self.scrollbar.set, width=37)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=0, sticky=N+S)
        self.listbox.grid(row=0, column=1, sticky=N+S)
        self.listbox.bind("<<ListboxSelect>>", self.listbox_event)
        for count, item in enumerate(data):
            self.listbox.insert(END, pathlib.Path(item[0].path).stem)

        self._canvas = rsvis.tools.rscanvas.RSCanvas(self, data, **kwargs)
        self._canvas.set_container()
        self._canvas.grid(row=0, column=2, sticky=N+S+E+W)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def listbox_event(self,event):
        try:
            self._canvas._index_list(index=self.listbox.curselection()[0])
            self._canvas.set_container()
        except IndexError:
            pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def update_listbox(self,event):
        self.listbox.activate(self._canvas.get_index_list())      