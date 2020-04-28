# ===========================================================================
#   settingsbox.py ----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class SettingsBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, fields, func, default=list(), **kwargs):
        Frame.__init__(self, parent, **kwargs)

        entries = self.makeform(fields, default)

        self.func = func

        self.bind("<Return>", (lambda event, e=entries: self.func(e))) 

        self.button_set = Button(parent, text="Set", command=lambda e=entries: self.func(e))
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, fields, default=list()):
        entries = []
        for index, field in enumerate(fields):
            row = Frame(self)
            lab = Label(row, width=12, text=field, anchor='w')
            ent = Entry(row)
            ent.insert(END, str(default[index]))
            row.pack(side=TOP, fill=X, padx=2, pady=2)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))

        return entries
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def fetch(self, entries):
        entry_str = ""
        for entry in entries:
            field = entry[0]
            text  = entry[1].get()
            entry_str = "{} {}: {}".format(entry_str, field, text)
            
        return entry_str
