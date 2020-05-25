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
    def __init__(
            self, 
            parent, 
            sbox=list(), 
            func=lambda x: None, 
            button="", 
            **kwargs
        ):
        Frame.__init__(self, parent, **kwargs)
        
        if button:
            self._button = Button(self, text=button, command=lambda: self.func())
            self._button.pack(side=TOP, fill=X)

        self._sbox_type = sbox[2] if sbox else list()
        self._sbox_entries = self.makeform_sbox(sbox[0], sbox[1]) if sbox else list()

        self.func = func

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform_sbox(self, fields, default=list()):
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
    def get_list(self):
        entries = list()
        for entry, dtype in zip(self._sbox_entries, self._sbox_type):
            entries.append(eval(dtype)(entry[1].get()))
        return entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_dict(self):
        entries = dict()
        for entry, dtype in zip(self._sbox_entries, self._sbox_type):
            entries[entry[0]] = eval(dtype)(entry[1].get())
        return entries

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def fetch(self):
        entry_str = ""
        for entry in self._sbox_entries:
            field = entry[0]
            text  = eval(dtype)(entry[1].get())
            entry_str = "{} {}: {}".format(entry_str, field, text)
            
        return entry_str