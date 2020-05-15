# ===========================================================================
#   widgets.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *

# If you program Tk using the Tcl language, you can ask the system to let you know when a variable is changed. The Tk toolkit can use this feature, called tracing, to update certain widgets when an associated variable is modified.

# There’s no way to track changes to Python variables, but Tkinter allows you to create variable wrappers that can be used wherever Tk can use a traced Tcl variable.

# https://effbot.org/tkinterbook/variable.htm

#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def quit(window, title=None, **kwargs):
    """Exit Window."""   
    # if title=="Help":
    #     self._popup_help = 0
    window.quit()
    window.destroy()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_option_menu(menubar, options, parent, obj):

    labels = list()
    for o in options:
        if o["label"] not in labels:
            labels.append(o["label"])

    for l in labels:
        menu = Menu(menubar, tearoff=0)
        for o in options:
            if not o["label"] == l:
                continue

            name = o["name"]
            if o["key"] is not None:
                name = "{} ({})".format(name, o["key"])
                #   key bindings --------------------------------------------
                parent.bind("<{}>".format(o["key"]), lambda event, cmd=o["command"]: cmd(obj))

            menu.add_command(label=name, command=lambda cmd=o["command"]: cmd(obj))
        
        menubar.add_cascade(label=l, menu=menu)

# ---------------------------------------------------------------------------
def add_info_menu(menubar, parent, obj, command):
    options = [{ 
        "name" : "Help",
        "key" : "F1",
        "label": "Information",
        "description": "Show help.",
        "command": command
    }]
    add_option_menu(menubar, options, parent, obj)