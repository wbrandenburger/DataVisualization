#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger

import datetime
from pathlib import Path
import shutil

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def chkdir(path, exist=True, logger=None):
    path = path if isinstance(path, list) else [path]
    for p in path:
        if exist:
            assert Path(p).exists(), "Path {} does not exist".format(p)
        else:
            assert not Path(p).exists(), "Path {} does exist".format(p)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def chkfile(path, exist=True, logger=None):
    path = path if isinstance(path, list) else [path]
    for p in path:
        if exist:
            assert Path(p).is_file(), "File {} does not exist".format(p)
        else: 
            assert not Path(p).is_file(), "File {} does exist".format(p)        

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def mkdir(path, logger=None):
    path = path if isinstance(path, list) else [path]
    for p in path:
        if not Path(p).exists():
            show_mk_str(str(p), logger=logger)
            Path(p).mkdir(parents=True, exist_ok=True)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rmdir(path, logger=None):
    path = path if isinstance(path, list) else [path]
    for p in path:
        if Path(p).exists():
            show_rm_str(str(p), logger=logger)
            shutil.rmtree(p)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_timestamp():
    return datetime.now().strftime('%y%m%d-%H%M%S')

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_info_str(path, logger=None):
    show_io_str("[INFO] {}".format(path), logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_rm_str(path, logger=None):
    show_io_str("[RM] {}".format(path), logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_mk_str(info, logger=None):
    show_io_str("[MK] {}".format(info), logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_move_str(info, logger=None):
    show_io_str("[MV] {}".format(info), logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_io_str(io_str, logger=None):
    _logger.info(io_str)

    if logger is not None:
        logger(io_str)
