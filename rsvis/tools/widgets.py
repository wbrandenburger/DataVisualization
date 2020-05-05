# ===========================================================================
#   widgets.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from tkinter import *

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_option_menu(menubar, options, obj, label="Default"):
    optionmenu = Menu(menubar, tearoff=0)
    for option in options: 
        optionmenu.add_command(label=option["name"], command=lambda cmd=option["command"]: cmd(obj))
    
    menubar.add_cascade(label=label, menu=optionmenu)