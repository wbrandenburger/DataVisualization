# ===========================================================================
#   imgio.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.utils.general as gu
import rsvis.utils.imgcontainer
from rsvis.utils import imgtools

import numpy as np
import pathlib
import PIL
import shutil
import tifffile

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_info_str(info, logger=None):
    info_str = "[INFO] '{}'".format(info)
    show_io_str(info_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_read_str(path, logger=None):
    read_str = "[READ] '{}'".format(path)
    show_io_str(read_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_copy_str(path, logger=None):
    copy_str = "[COPY] '{}'".format(path)
    show_io_str(copy_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_write_str(path, logger=None):
    write_str = "[WRITE] '{}'".format(path)
    show_io_str(write_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_io_str(io_str, logger=None):
    _logger.info(io_str)

    if logger is not None:
        logger(io_str)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_object(path, logger=None):
    show_read_str(path, logger=logger)

    objects = rsvis.utils.yaml.yaml_to_data(path)
    return objects

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_object(path, obj, logger=None,):
    show_write_str(path, logger=logger)

    rsvis.utils.yaml.data_to_yaml(path, obj) 

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object(path, scale=100, default=list(), logger=None, **kwargs):
    if not pathlib.Path(path).exists():
        return default
    obj = read_object(path, logger=logger)

    if scale != 100 and obj is not None:
        for o in obj:
            o["box"] = [int(box*(float(scale)/100.0)) for box in o["box"]]
    
    return obj if obj else default

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def set_object(path, obj, scale=100, logger=None, **kwargs):
    if scale != 100:
        for o in obj:
            o["box"] = [int(box/(float(scale)/100.0)) for box in o["box"]]
    
    write_object(path, obj, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_log(path, logger=None):
    show_read_str(path, logger=logger)

    with open(path, "r") as f:
        return f.read()
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_log(path, log, logger=None):
    show_write_str(path, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_log(path, default="", logger=None, **kwargs):
    if not pathlib.Path(path).exists():
        return default
    return read_log(path, logger=logger)
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_image(path, logger=None,):
    show_read_str(path, logger=logger)
    
    if str(path).endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = np.asarray(PIL.Image.open(path))
    
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_image(path, img, logger=None,):
    show_write_str(path, logger=logger)

    if str(path).endswith(".tif"):
        tifffile.imwrite(path, img)
    else:
        PIL.Image.fromarray(img).write(path)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path, dest, logger=None,):
    show_copy_str(dest, logger=logger)
    shutil.copy2(path, dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(
        path, 
        spec,
        label=dict(), 
        scale=100, 
        show=False, 
        logger=None,
        **kwargs
    ):

    img = read_image(path, logger=logger)

    if show:
        show_info_str(imgtools.get_array_info(img), logger=logger)

    if scale < 100:
        img = imgtools.resize_img(img, scale)

    if label and spec == "label":
        img = imgtools.labels_to_image(img, label)

    if show:
        img = imgtools.project_data_to_img(
            imgtools.stack_image_dim(img), dtype=np.uint8, factor=255
        )

    return img