# ===========================================================================
#   combobox.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ComboBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            cbox=list(),
            func=lambda x=None: None,
            **kwargs
        ):
        super(ComboBox, self).__init__(parent, **kwargs)

        self._func = func

        self._type = cbox[3] if cbox else list()
        self._fields = cbox[1] if cbox else list()
        self._entries = self.makeform(cbox[0], cbox[1], cbox[2]) if cbox else list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, labels, fields, default):
        entries = []
        for idx, label in enumerate(labels):
            row = Frame(self)
            lab = Label(row, width=16, text=label, anchor='w')

            variable = StringVar(self)
            variable.set(default[idx])
            cbox = ttk.Combobox(row, textvariable=variable, values=fields[idx], state="readonly")
            cbox.bind("<<ComboboxSelected>>", self._func)

            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)
            cbox.pack(side=RIGHT, expand=YES, fill=X)
            entries.append((label, variable))

        return entries

        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self, index=0, value=True):
        entry = eval(self._type[index])(self._entries[index][1].get())
        return  entry if value else self._fields[index].index(entry)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_label(self, choice, index=0):
        self._entries[index][1].set(choice)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_label(self, index=0):
        return self._entries[index][1]
    
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