# ===========================================================================
#   combobox.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import Frame, StringVar, Label, ttk, TOP, X, LEFT, RIGHT, YES

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
        self.variable = StringVar(self)
        self.variable.set(fields[default])
 
        row = Frame(self)
        lab = Label(row, width=13, text=label, anchor='w')
        self.cbox = ttk.Combobox(row, textvariable=self.variable, values=fields, state="readonly")
        self.cbox.current(0)
        # cbox.bind("<Return>", (lambda event, e=entries: self.func(e))) 
        row.pack(side=TOP, fill=X, padx=2, pady=2)
        lab.pack(side=LEFT)
        self.cbox.pack(side=RIGHT, expand=YES, fill=X)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self):
        return {"index": self.cbox.current(), "label": self.cbox.get()}

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_choice(self, choice):
        self.variable.set(choice)