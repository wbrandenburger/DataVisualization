# ===========================================================================
#   imagetools.py -----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.utils.patches
from rsvis.utils import imgtools

import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import ndimage
from scipy.stats import norm
from PIL import Image
from io import BytesIO

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_gray_image(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_inverted_image(img):
    return cv2.LUT(img, lut = np.arange(255, -1, -1, dtype=np.uint8))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_manipulated_image(img, logger=None):
    img_mean_old = np.mean(img)
    img_std_old = np.std(img)

    param_b = (img_std_old-10.)/img_std_old
    param_a = img_mean_old+20.-param_b*img_mean_old

    img_new= (param_a+img*param_b).astype(np.uint8)
    if logger:
        logger("[MEAN] {:.2f}->{:.2f} [STD] {:.2f}->{:.2f}".format(img_mean_old, np.mean(img_new), img_std_old, np.std(img_new)))
    return img_new