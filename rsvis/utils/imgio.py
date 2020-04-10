# ===========================================================================
#   imgio.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
from rsvis.__init__ import _logger
from rsvis.utils import imgtools
import rsvis.utils.general as glu
import rsvis.utils.imgcontainer

import numpy as np
import pathlib
import PIL
import shutil
import tifffile

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_log(path):
    _logger.debug("[READ] '{}'".format(path))
    with open(path, "r") as f:
        return f.read()
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_image(path):
    _logger.debug("[READ] '{}'".format(path))
    
    if str(path).endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = np.asarray(PIL.Image.open(path))
    
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def save_image(dest, img):
    _logger.debug("[SAVE] '{}'".format(dest))

    if str(dest).endswith(".tif"):
        tifffile.imwrite(dest, img)
    else:
        PIL.Image.fromarray(img).write(dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path, dest):
    _logger.debug("[COPY] '{}'".format(dest))
    shutil.copy2(path, dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(
        path, 
        spec,
        param_label=dict(), 
        scale=100, 
        show=False, 
        **kwargs
    ):

    img = imgtools.resize_img(read_image(path), scale)

    if param_label and spec == "label":
        img = imgtools.labels_to_image(img, param_label)

    if show:
        img = imgtools.project_data_to_img(img, dtype=np.uint8, factor=255)
    if show:
        img =  imgtools.stack_image_dim(img)

    return img
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_data(
        files,
        specs, # list()
        param_io,
        param_label=dict(), 
        param_show=dict(), # scale=100, show=False, live=True, 
        param_log=dict() # log_dir, ext=".log"
        # default_spec="image",       
    ):

    load = lambda path, spec: get_image(
        path, 
        spec, 
        param_label=param_label, 
        **param_show # scale=100, show=False, live=True
    )
    
    img_in = list() 
    for f_set in files:
        img = rsvis.utils.imgcontainer.ImgListContainer(
            load=load, log_dir=glu.get_value(param_log, "path_dir"))
        for f, s in zip(f_set, specs):
            img.append(path = f, spec=s, **param_show)# scale=100, show=False, live=True

        img_in.append(img)

    get_path = glu.PathCreator(**param_io)

    img_out = lambda path, img, **kwargs: save_image(get_path(path, **kwargs), img)
    log_out = lambda path, **kwargs : get_path(path, **param_log, **kwargs)

    return img_in, img_out, log_out, get_path