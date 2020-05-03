# ===========================================================================
#   settingsbox.py ----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import Button, Frame, Entry, Label, StringVar, ttk, END, TOP, X, YES, LEFT, RIGHT, END

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class SettingsBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, fields, func, default=list(), **kwargs):
        Frame.__init__(self, parent, **kwargs)

        entries = self.makeform(fields, default)

        self.func = func
        self.button_set = Button(parent, text="Set", command=lambda e=entries: self.func(e))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, fields, default=list()):
        entries = []
        for index, field in enumerate(fields):
            row = Frame(self)
            lab = Label(row, width=16, text=field, anchor='w')
            ent = Entry(row)
            ent.bind("<Return>", (lambda event, e=entries: self.func(e))) 
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

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ComboBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, label, fields, func, default=0, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        self.makeform(label, fields, default)

        self.cbox.bind("<<ComboboxSelected>>", func) 
        # self.func = func
        # self.button_set = Button(parent, text="Set", command=lambda e=entries: self.func(e))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, label, fields, default=0):
        variable = StringVar(self).set(fields[default])
 
        row = Frame(self)
        lab = Label(row, width=13, text=label, anchor='w')
        self.cbox = ttk.Combobox(row, textvariable=variable, values=fields, state="readonly")
        self.cbox.current(0)
        # cbox.bind("<Return>", (lambda event, e=entries: self.func(e))) 
        row.pack(side=TOP, fill=X, padx=2, pady=2)
        lab.pack(side=LEFT)
        self.cbox.pack(side=RIGHT, expand=YES, fill=X)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self):
        return {"index": self.cbox.current(), "label": self.cbox.get()}