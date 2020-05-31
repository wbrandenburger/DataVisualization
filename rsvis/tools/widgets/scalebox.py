# ===========================================================================
#   scalebox.py -----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ScaleBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            scbox=list(),
            func=lambda x: None,
            button="",
            orient=HORIZONTAL,
            **kwargs
        ):
        super(ScaleBox, self).__init__(parent, **kwargs)

        self._func = func

        self._orient = orient

        if button:
            self._button = Button(self, text=button, command=lambda: self._func())
            self._button.pack(side=TOP, fill=X)

        self._type = scbox[2] if scbox else list()
        self._entries = self.makeform(scbox[0], scbox[1]) if scbox else list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, labels, params):
        entries = []
        for label, param in zip(labels, params):
            row = Frame(self)
            lab = Label(row, width=16, text=label, anchor='w')

            sli = Scale(row, from_=param[0], to=param[1], orient=self._orient, command=lambda event: self._func(), resolution=param[2], showvalue=0)
            sli.set(param[3]) 
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)
            sli.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((label, sli))

        return entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self, index=0):
        return eval(self._type[index])(self._entries[index][1].get())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_list(self):
        entries = list()
        for entry, dtype in zip(self._entries, self._type):
            entries.append(eval(dtype)(entry[1].get()))
        return entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_dict(self):
        entries = dict()
        for entry, dtype in zip(self._entries, self._type):
            entries[entry[0]] = eval(dtype)(entry[1].get())
        return entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def fetch(self):
        entry_str = ""
        for entry, dtype in zip(self._entries, self._type):
            field = entry[0]
            text  = eval(dtype)(entry[1].get())
            entry_str = "{} {}: {}".format(entry_str, field, text)
            
        return entry_str