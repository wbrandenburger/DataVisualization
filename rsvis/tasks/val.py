# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger

import rsvis.tasks.tasks

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    """Default task of set 'test'"""
    _logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow():
    """Call the main routine for evaluation of a single task classification model"""

    rsvis.tasks.tasks.task_rsshow(setting="val")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_auxiliary_data():
    """Call the main routine for evaluation of a single task classification model"""

    rsvis.tasks.tasks.task_auxiliary_data(setting="val")    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_gaofen_data():
    """Call the main routine for evaluation of a single task classification model"""

    rsvis.tasks.tasks.task_gaofen_data(setting="val")    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_agan_join():
    """Call the main routine for evaluation of a single task classification model"""

    rsvis.tasks.tasks.task_agan_join(setting="val")    
