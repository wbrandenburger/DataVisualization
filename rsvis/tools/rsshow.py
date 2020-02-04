# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.tools.image
import rsvis.tools.rsshowui

import cv2
import numpy as np
import tifffile
import tempfile
from matplotlib import pyplot as plt

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(image_path: str, image_type: str):
    image = tifffile.imread(image_path)
    
    if image_type == "height":
        return normalize_image(image)
    if image_type == "msi":
        image = get_msi(image)
        image_type = "image"

    image = convert_image_to_color(image)
    if image_type == "label":
        return label_to_image(image)
    if image_type == "image":
        return image

    return image

def get_histogram(img):

    hist,bins = np.histogram(img.flatten(),256,[0,256])

    cdf = hist.cumsum()
    cdf_normalized = cdf * hist.max()/ cdf.max()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(cdf_normalized, color = 'b')
    ax.hist(img.flatten(),256,[0,256], color = 'r')
    ax.set_xlim([0,256])
    ax.legend(('cdf','histogram'), loc = 'upper left')

    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_color(image):
    if len(image.shape)==1:
        image = np.stack((image,)*3, axis=-1)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalization(image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    image = clahe.apply(image)
    return image


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalize_image(image):
    image = image.astype(float)
    min_img = np.min(image)
    max_img = np.max(image)
    image = (image - min_img)/(max_img - min_img) * 256
    image = image.astype("uint8")
    return image
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_msi(image):   
    index_list = [2,3,4]
    for i in index_list:
        image[:, :, i] = image[:, :, i]
    image = image[:, :, np.array(index_list)]
    image = correct_image(image)
    return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def correct_image(image):
    image = image.astype(float) 
    image_corr = image[~np.isnan(image)]
    image = image / np.max(image_corr) * 256
    image = image.astype("uint8")
    return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def label_to_image(image):
    return image


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(files, types):

    load = lambda index: [rsvis.tools.rsshow.get_image(f, t) for f, t in zip(files[index], types)]
    ui = rsvis.tools.rsshowui.RSShowUI(len(files), load) 

    ui.set_keys( 
        {
            "h": lambda image: rsvis.tools.rsshow.get_histogram(image),
            "n": lambda image: rsvis.tools.rsshow.normalization(image)
        }
    )


    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.imshow('image', ui.start())

    while True:
        key = chr(cv2.waitKeyEx(1) & 0xFF)
        if ui.has_key(key):
            image = ui.event(key)
            if image is not None: 
                cv2.namedWindow('image', cv2.WINDOW_NORMAL)
                cv2.imshow('image',image)
            else:
                return 1
    cv2.destroyAllWindows()    
