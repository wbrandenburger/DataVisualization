# ===========================================================================
#   widgets.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *

# If you program Tk using the Tcl language, you can ask the system to let you know when a variable is changed. The Tk toolkit can use this feature, called tracing, to update certain widgets when an associated variable is modified.

# There’s no way to track changes to Python variables, but Tkinter allows you to create variable wrappers that can be used wherever Tk can use a traced Tcl variable.

# https://effbot.org/tkinterbook/variable.htm

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_option_menu(menubar, options, parent, obj, label="Default"):
    optionmenu = Menu(menubar, tearoff=0)
    for option in options: 
        name = option["name"]
        if option["key"] is not None:
            name = "{} ({})".format(name, option["key"])
        optionmenu.add_command(label=name, command=lambda cmd=option["command"]: cmd(obj))
    
    menubar.add_cascade(label=label, menu=optionmenu)

    #   key bindings ------------------------------------------------
    for option in options:
        if option["key"] is not None:
            parent.bind("<{}>".format(option["key"]), lambda event, cmd=option["command"]: cmd(obj))