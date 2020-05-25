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
    def __init__(
            self, 
            parent, 
            label, 
            fields, 
            func, 
            default=0, 
            **kwargs
        ):
        Frame.__init__(self, parent, **kwargs)

        self.makeform(label, fields, default=default)

        self._cbox.bind("<<ComboboxSelected>>", func) 
        # self.func = func
        # self.button_set = Button(parent, text="Set", command=lambda e=entries: self.func(e))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def makeform(self, label, fields, default=0):
        self._variable = StringVar(self)
        
        row = Frame(self)
        lab = Label(row, width=13, text=label, anchor='w')
        self._cbox = ttk.Combobox(row, textvariable=self._variable, values=fields, state="readonly")
        self._cbox.current(0)
        # cbox.bind("<Return>", (lambda event, e=entries: self.func(e))) 
        row.pack(side=TOP, fill=X, padx=2, pady=2)
        lab.pack(side=LEFT)
        self._cbox.pack(side=RIGHT, expand=YES, fill=X)

        self._variable.set(fields[default])
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self, index=False):
        return self._cbox.current() if index else self._cbox.get()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_variable(self, choice):
        self._variable.set(choice)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_variable(self):
        return self._variable
    