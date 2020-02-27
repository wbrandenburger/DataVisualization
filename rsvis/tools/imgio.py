# ===========================================================================
#   imgio.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.tools.imgtools

import numpy as np
import PIL
import shutil
import tifffile

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_image(path):
    rsvis.__init__._logger.debug("Read image '{}'".format(path))
    
    if str(path).endswith(".tif"):
        return tifffile.imread(path)
    else:
        return np.asarray(PIL.Image.open(path))
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def save_image(dest,  img):
    rsvis.__init__._logger.debug("Save img to '{}'".format(dest))

    if str(dest).endswith(".tif"):
        tifffile.imwrite(dest, img)
    else:
        PIL.Image.fromarray(img).write(dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path,  dest):
    rsvis.__init__._logger.debug("Copy img to '{}'".format(dest))
    shutil.copy2(path, dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(path, spec="image", param_label=dict(), scale=100, show=False):
    img = rsvis.tools.imgtools.resize_img(read_image(path), scale)
    if param_label and spec == "label":
        img = rsvis.tools.imgtools.labels_to_image(img, param_label)
    if show and spec in ["label", "height", "msi"]:
        img = rsvis.tools.imgtools.project_data_to_img(img)
    if show:
        img =  rsvis.tools.imgtools.stack_image_dim(img)
    return img
    
