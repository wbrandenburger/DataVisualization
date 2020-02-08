# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.tools.image
import rsvis.tools.rsshowui
import rsvis.utils.ply

import cv2
import numpy as np
import tifffile
import tempfile
from matplotlib import pyplot as plt
import pandas
import subprocess

# def get_pointcloud(image, height):
#     img = cv2.resize(image, (256, 256), interpolation = cv2.INTER_LINEAR).astype("uint8")
#     height = cv2.resize(height, (256, 256), interpolation = cv2.INTER_LINEAR).astype(float)/8
#     grid = np.indices((256, 256))
#     img_dict = np.concatenate((
#         grid[0,:,:].reshape((256*256,1)), 
#         grid[1,:,:].reshape((256*256,1)), 
#         height.reshape((256*256,1)), 
#         img[:,:,0].reshape((256*256,1)), 
#         img[:,:,1].reshape((256*256,1)), 
#         img[:,:,2].reshape((256*256,1))
#         ), axis=1)
#     # img_dict = {
#     #     'x':     [grid[0,:,:].reshape((256*256,1)).astype(float)],
#     #     'y':     [grid[1,:,:].reshape((256*256,1)).astype(float)],
#     #     'z':     [height.reshape((256*256,1)).astype(float)], 
#     #     'red':   [img[:,:,0].reshape((256*256,1))], 
#     #     'green': [img[:,:,1].reshape((256*256,1))], 
#     #     'blue':  [img[:,:,2].reshape((256*256,1))]
#     # }
#     data = pandas.DataFrame(img_dict)
#     tmp = tempfile.mkstemp(suffix=".ply")
#     # data  = pandas.DataFrame(img_list, columns=['x', 'y', 'z', 'red', 'green', 'blue'])

#     rsvis.__init__._logger.debug("Write {0}".format(tmp[1]))
#     rsvis.utils.ply.write_ply(tmp[1], points=data, mesh=None, as_text=True)
#     subprocess.Popen(['C:\\Program Files\\ccViewer\\ccViewer.exe', tmp[1]])
#     return image

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

def get_img_info(img):
    if len(img.shape) != 3: 
        img_new = np.ndarray((*img.shape,1), dtype=img.dtype)
        img_new[:,:,0] = img
        img = img_new
    return (img, img.shape[0], img.shape[1], img.shape[2], img.shape[0] * img.shape[1])

def get_histogram(img, **kwargs):
    img = get_masked_image(img, **kwargs) 

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    img, _ , _ , img_channel, img_pixel = get_img_info(img)
    for i in range(img_channel):
        histr = cv2.calcHist([img],[i],None,[256],[0,256]) / img_pixel
        plt.plot(histr)
        
    ax.set_xlim([0,256])
    # ax.legend(loc = 'upper left')
    return get_nparray_from_fig(fig)

def get_nparray_from_fig(fig):  
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data

def get_stats(img, **kwargs):
    img = get_masked_image(img, **kwargs)

    fig = plt.figure(dpi=256, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)

    img, _ , _ , img_channel, img_pixel = get_img_info(img)
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

def get_masked_image(image, ref_point=None):
    if ref_point:
        return image[
            ref_point[0][0]:ref_point[1][0],
            ref_point[0][1]:ref_point[1][1]
        ]
    return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_color(image):
    if len(image.shape)==1:
        image = np.stack((image,)*3, axis=-1)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_gray(image):
    if len(image.shape)==3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalization(image, **kwargs):
    image = convert_image_to_gray(image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    image = clahe.apply(image)
    return image


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalize_image(image):
    image = image.astype(float)
    min_max_img = (np.min(image), np.max(image))
    image = (image - min_max_img[0])/(min_max_img[1] - min_max_img[0]) * 256
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
    
    types.index("height")
    ui.set_keys( 
        {
            "h": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.get_histogram(image, **kwargs), "param" : [-1]},
            "j": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.get_stats(image, **kwargs), "param" : [-1]},
            "n": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.normalization(image, **kwargs), "param" : [-1]},
            # "r": { "func" : lambda image, height: rsvis.tools.rsshow.get_pointcloud(image, height), "param" : [-1,types.index("height")]}
        }
    )


    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.imshow("image", ui.start())
    cv2.setMouseCallback("image", ui.mouse_event)

    image = ui.show()
    while True:
        key = chr(cv2.waitKeyEx(1) & 0xFF)
        if ui.has_key(key):
            event_result = ui.key_event(key)
            if isinstance(event_result, int) == 1: 
                return 1
            elif isinstance(event_result, np.ndarray):
                image = event_result
        
            cv2.namedWindow("image", cv2.WINDOW_NORMAL)
            cv2.imshow("image",image)

    cv2.destroyAllWindows()    
