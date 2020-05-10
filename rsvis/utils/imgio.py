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
def read_object(path):
    _logger.info("[READ] '{}'".format(path))

    objects = rsvis.utils.yaml.yaml_to_data(path)
    return objects

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_object(path, obj):
    _logger.info("[SAVE] '{}'".format(path))

    rsvis.utils.yaml.data_to_yaml(path, obj) 

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object(path, scale=100, default=list(), **kwargs):
    if not pathlib.Path(path).exists():
        return default
    obj = read_object(path)

    if scale != 100 and obj is not None:
        for o in obj:
            o["box"] = [int(box*(float(scale)/100.0)) for box in o["box"]]
    
    return obj if obj else default

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def set_object(path, obj, scale=100, **kwargs):
    if scale != 100:
        for o in obj:
            o["box"] = [int(box/(float(scale)/100.0)) for box in o["box"]]
    
    write_object(path, obj)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_log(path):
    _logger.info("[READ] '{}'".format(path))

    with open(path, "r") as f:
        return f.read()
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_log(path, log):
    _logger.info("[SAVE] '{}'".format(path))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_log(path, default="", **kwargs):
    if not pathlib.Path(path).exists():
        return default
    return read_log(path)
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_image(path):
    _logger.info("[READ] '{}'".format(path))
    
    if str(path).endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = np.asarray(PIL.Image.open(path))
    
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_image(path, img):
    _logger.info("[SAVE] '{}'".format(path))

    if str(path).endswith(".tif"):
        tifffile.imwrite(path, img)
    else:
        PIL.Image.fromarray(img).write(path)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path, dest):
    _logger.info("[COPY] '{}'".format(dest))
    shutil.copy2(path, dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(
        path, 
        spec,
        label=dict(), 
        scale=100, 
        show=False, 
        **kwargs
    ):

    img = read_image(path)

    if show:
        _logger.info(imgtools.get_array_info(img))

    if scale < 100:
        img = imgtools.resize_img(img, scale)

    if label and spec == "label":
        img = imgtools.labels_to_image(img, label)

    if show:
        img = imgtools.project_data_to_img(
            imgtools.stack_image_dim(img), dtype=np.uint8, factor=255
        )

    return img