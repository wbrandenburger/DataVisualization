# ===========================================================================
#   histogram.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import cv2
import numpy as np
from matplotlib import pyplot as plt

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_img_info(img):
    if len(img.shape) != 3: 
        img_new = np.ndarray((*img.shape,1), dtype=img.dtype)
        img_new[:,:,0] = img
        img = img_new
    return (img.shape[0], img.shape[1], img.shape[2], img.shape[0] * img.shape[1], np.min(img), np.max(img))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_histogram(img, **kwargs):
    img = get_masked_image(img, **kwargs) 

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    _ , _ , img_channel, img_pixel, _, _ = get_img_info(img)
    for i in range(img_channel):
        histr = cv2.calcHist([img],[i],None,[256],[0,256]) / img_pixel
        plt.plot(histr)
        
    ax.set_xlim([0,256])
    # ax.legend(loc = 'upper left')
    return get_nparray_from_fig(fig)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_nparray_from_fig(fig):  
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_stats(img, **kwargs):
    img = get_masked_image(img, **kwargs)

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    _ , _ , img_channel, img_pixel, _, _ = get_img_info(img)
    for i in range(img_channel):
        vector = img[:,:,i].flatten()
        hist, _ = np.histogram(vector , 256, [0,256])

        cdf = hist.cumsum()
        cdf_normalized = cdf * hist.max()/ cdf.max() / img_pixel
        
        histr = cv2.calcHist([img],[i],None,[256],[0,256]) / img_pixel
        plt.plot(histr)
        plt.plot(cdf_normalized, color = 'b')
    
    ax.set_xlim([0,256])
    # ax.legend(loc = 'upper left')
    return get_nparray_from_fig(fig)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
# get the area of two points
def get_masked_image(img, ref_point=None):
    if ref_point:
        return img[
            ref_point[0][0]:ref_point[1][0],
            ref_point[0][1]:ref_point[1][1]
        ]
    return img
