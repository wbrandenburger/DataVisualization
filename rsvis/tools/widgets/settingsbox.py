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
            func=lambda x=None: None, 
            button="", 
            **kwargs
        ):
        super(SettingsBox, self).__init__(parent, **kwargs)
        
        self._func = func

        if button:
            self._button = Button(self, text=button, command=lambda: self._func())
            self._button.pack(side=TOP, fill=X)

        self._type = sbox[2] if sbox else list()
        self._entries = self.makeform(sbox[0], sbox[1]) if sbox else list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, labels, default=list()):
        vcmd = (self.register(self.callback))

        entries = []
        for idx, (label, dtype) in enumerate(zip(labels, self._type)):
            row = Frame(self)
            lab = Label(row, width=16, text=label, anchor='w')

            ent = Entry(row, validate="all", validatecommand=(vcmd, "%P", dtype))
            ent.bind("<Return>", (lambda x=None: self._func())) 
            ent.insert(END, str(default[idx]))
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((label, ent))
            
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

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def callback(self, P, dtype):
        if dtype=="int":
            if str.isdigit(P) or P=="":
                return True
            else:
                return False
        else:
            return True