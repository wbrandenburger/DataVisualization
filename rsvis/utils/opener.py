# ===========================================================================
#   opener.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgio
import rsvis.utils.logger
import os
import subprocess

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Opener():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, opener, logger=None):
        self._opener = opener
        self._logger = rsvis.utils.logger.Logger(logger=logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __call__(self, opener, *args, wait=False):
        cmd = self.get_args(self._opener[opener], *args)
        self._logger("[CMD] {}".format(cmd))
        process = subprocess.Popen(cmd)
        if wait:
            process.wait()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_args(self, cmd, *args):
        cmd = cmd.copy() if isinstance(cmd, list) else [cmd]
        for a in args:
            cmd.extend(*self.to_list(a))
        
        return " ".join(cmd)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def to_list(self, *args):
        return (x if isinstance(x, list) or x is None else [x] for x in args)

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class GeneralOpener(Opener):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, opener=dict(), **kwargs):

        opener.update({
                "files": "explorer.exe"
            }
        )

        super(GeneralOpener, self).__init__(opener, **kwargs)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __call__(self, opener, path, wait=False):
        imgio.show_open_str(path, self._logger)

        dir = os.path.dirname(__file__)
        if not os.path.isabs(path):
            path = os.path.join(dir, path)   
            
        process = subprocess.Popen(self.get_args(self._opener[opener], path))
        if wait:
            process.wait()
