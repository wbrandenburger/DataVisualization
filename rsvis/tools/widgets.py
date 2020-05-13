# ===========================================================================
#   widgets.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.topwindow

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
def add_option_menu(menubar, options, parent, obj, label="Default"):
    menu = Menu(menubar, tearoff=0)
    for option in options: 
        name = option["name"]
        if option["key"] is not None:
            name = "{} ({})".format(name, option["key"])
        menu.add_command(label=name, command=lambda cmd=option["command"]: cmd(obj))
    
    menubar.add_cascade(label=label, menu=menu)

    #   key bindings ------------------------------------------------
    for option in options:
        if option["key"] is not None:
            parent.bind("<{}>".format(option["key"]), lambda event, cmd=option["command"]: cmd(obj))

# ---------------------------------------------------------------------------
def add_info_menu(menubar, parent, obj, command):
    options = [{ 
        "name" : "Help",
        "key" : "F1",
        "description": "Show help.",
        "command": command
    }]
    add_option_menu(menubar, options, parent, obj, label="Information")

#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def set_popup(parent, **kwargs):
    t = rsvis.tools.topwindow.TopWindow(
        parent, 
        q_cmd=rsvis.tools.widgets.quit, 
        **kwargs
    )
    t.mainloop()