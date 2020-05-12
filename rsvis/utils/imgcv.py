# ===========================================================================
#   imgcv.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import cv2
import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def dilation(img, iterations=1):
    img = np.where(np.logical_and(img>0.1,  img<0.2), 1., 0.)
    img = img.astype(np.uint8)*255
    # Taking a matrix of size 5 as the kernel 
    kernel = np.ones((5,5), np.uint8) 
    img = cv2.dilate(img, kernel, iterations=iterations)
    return erosion(img)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def erosion(img, iterations=1):
    # Taking a matrix of size 5 as the kernel 
    kernel = np.ones((5,5), np.uint8)
    img = cv2.erode(img, kernel, iterations=iterations)
    return img




