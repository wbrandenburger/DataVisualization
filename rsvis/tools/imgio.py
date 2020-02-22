# ===========================================================================
#   imgio.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__

import numpy as np
import PIL
import shutil
import tifffile

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def save_image(dest,  img):
    rsvis.__init__._logger.debug("Save img to '{}'".format(dest))
    if dest.endswith(".tif"):
        tifffile.imwrite(dest, img)
    else:
        img = PIL.Image.fromarray(img)
        img = img.write(dest)
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path,  dest):
    rsvis.__init__._logger.debug("Copy img to '{}'".format(dest))
    shutil.copy2(path, dest)


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(path, spec, labels=dict(), msi=list(), scale=100):
    
    if path.endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = np.asarray(PIL.Image.open(path))

    img = rsvis.tools.imgtools.resize_img(img, scale)

    if spec == "label":
        img = rsvis.tools.imgtools.labels_to_image(img, labels)

    if spec in ["label", "height", "msi"]:
        img = rsvis.tools.imgtools.project_data_to_img(img)

    if spec == "msi" and msi:
        img = np.stack((img[:,:,msi[0][0]], img[:,:,msi[0][1]], img[:,:,msi[0][2]]), axis=2)

    img =  rsvis.tools.imgtools.stack_image_dim(img)

    return img
    
