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
    def __init__(self, parent, fields, func, default, dtype=list(), button="", **kwargs):
        Frame.__init__(self, parent, **kwargs)
        
        if button:
            self._button = Button(self, text=button, command=lambda: self.func())
            self._button.pack(side=TOP, fill=X)

        self._entries = dict()     
        self._dtype = dtype
        self._sbox_entries = self.makeform(fields, default)

        self.func = func

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, fields, default=list()):
        entries = []
        for index, field in enumerate(fields):
            row = Frame(self)
            lab = Label(row, width=16, text=field, anchor='w')
            ent = Entry(row)
            ent.bind("<Return>", (lambda event: self.func())) 
            ent.insert(END, str(default[index]))
            row.pack(side=TOP, fill=X, padx=2, pady=2)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((field, ent))

        return entries
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self, index=0):
        return self._sbox_entries[index][1].get() 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_dict(self):
        for entry, dtype in zip(self._sbox_entries, self._dtype):
            self._entries[entry[0]] = eval(dtype)(entry[1].get())
        return self._entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def fetch(self):
        entry_str = ""
        for entry in self._sbox_entries:
            field = entry[0]
            text  = entry[1].get()
            entry_str = "{} {}: {}".format(entry_str, field, text)
            
        return entry_str