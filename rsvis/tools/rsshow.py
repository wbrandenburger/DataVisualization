# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.tools.image
import rsvis.tools.rsshowui
import rsvis.utils.ply
import rsvis.tools.imagestats

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
def get_image(img_path: str, img_type: str, resize=100):
    
    img = tifffile.imread(img_path)

    scale_percent = resize
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height) 
    img = cv2.resize(img, dim,  interpolation=cv2.INTER_NEAREST)
    
    img = np.expand_dims(img, axis=2) if len(img.shape) != 3 else img 
    
    if img_type == "height":
        return normalize_image(img)
    if img_type == "msi":
        img = get_msi(img)
        img_type = "img"

    return convert_image_to_color(img)

def get_img_info(img):
    if len(img.shape) != 3: 
        img_new = np.ndarray((*img.shape,1), dtype=img.dtype)
        img_new[:,:,0] = img
        img = img_new
    return (img.shape[0], img.shape[1], img.shape[2], img.shape[0] * img.shape[1], np.min(img), np.max(img))

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

def get_nparray_from_fig(fig):  
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    return data

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
def get_masked_image(img, ref_point=None):
    if ref_point:
        return img[
            ref_point[0][0]:ref_point[1][0],
            ref_point[0][1]:ref_point[1][1]
        ]
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_color(img):
    if img.shape[-1]!=3:
        return img

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_gray(img):
    if len(img.shape)==3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalization(img, **kwargs):
    for c in range(0, img.shape[2]):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img[:,:,c] = clahe.apply(img[:,:,c])
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def normalize_image(img):
    img = img.astype(float)
    min_max_img = (np.min(img), np.max(img))
    img = (img - min_max_img[0])/(min_max_img[1] - min_max_img[0]) * 255
    img = img.astype("uint8")
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_msi(img):   
    #index_list = [2,3,4]
    #for i in index_list:
       # img[:, :, i] = img[:, :, i]
    #img = correct_image(img)
    img = normalize_image(img)
    img = normalization(img)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def correct_image(img):
    img = img.astype(float) 
    img_corr = img[~np.isnan(img)]
    img = img / np.max(img_corr) * 255
    img = img.astype("uint8")
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def print_unique(img, label,**kwargs):
    img = label_to_scalar(img, label)
    img = (img.astype(float) / float(np.max(img)) * 255.0).astype("uint8")

    # unique, unique_index, unique_count = np.unique(img.flatten(), return_index=True, return_counts=True, axis=0)
    # print(unique, unique_count)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_image(img, label, cat, value=0, equal=True, **kwargs):
    label = label_to_scalar(label, cat)
    label_list = list()
    img_label = img.copy()
    for c in range(img.shape[-1]):

        if equal:
            mask = np.ma.masked_where(label[...,-1] != value, img[...,c])
        else:
            mask = np.ma.masked_where(label[...,-1] == value, img[...,c])
                    
        np.ma.set_fill_value(mask, 255)
        img_label[:,:,c] = mask.filled()
        label_list.append(mask.compressed())
    return img_label

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def label_to_scalar(img, cat):
    dim = img.shape
    img = img.reshape(-1, dim[-1])
    img = np.apply_along_axis(lambda x, cat: cat[str(x.tolist())], -1, img, cat)
    img = img.reshape( dim[0], dim[1], 1)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rs_imshow(img):

    if img.shape[-1] > 3:
        a = [2,1,6]
        b = [1,2,4]
        c = [1,5,4]
        stack_img = lambda img, x: (img[:,:,x[0]], img[:,:,x[1]], img[:,:,x[2]])
        img = np.stack(stack_img(img, a), axis=2)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.imshow("image", img)


def blubb(img, **kwargs):    
    foo = rsvis.tools.imagestats.ImageStats(
            path="A:\\VirtualEnv\\dev-rsvis\\src\\rsvis\\tmpchlgw4dk.json" 
        )
    dim = img.shape
    img = img.reshape(-1, dim[-1])
    img = np.apply_along_axis(foo.get_probability_c, -1, img)
    img = img.reshape( dim[0], dim[1], 1)
    return img

    # dim = img.shape
    # a = np.zeros((dim[0], dim[1], 1), dtype=np.float)
    # for r in range(0,dim[0]):
    #     for c in range(0,dim[1]):
    #         a[r,c,0] = foo.get_probability_c(img[r,c,:])
    # return a

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(files, types, cat=dict(), resize=100):

    load = lambda index: [rsvis.tools.rsshow.get_image(f, t, resize=resize) for f, t in zip(files[index], types)]
    ui = rsvis.tools.rsshowui.RSShowUI(len(files), load, cat=cat.values())
    ui.set_keys( 
        {   
            "l": { "func" : lambda image, label, **kwargs: rsvis.tools.rsshow.get_label_image(image, label, cat, **kwargs), "param" : [types.index("image"), types.index("label")]},
            "h": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.get_histogram(image, **kwargs), "param" : [-1]},
            "j": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.get_stats(image, **kwargs), "param" : [-1]},
            "n": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.normalization(image, **kwargs), "param" : [-1]},
            "g": { "func" : lambda image, **kwargs: rsvis.tools.rsshow.blubb(image, **kwargs),  "param" :  [types.index("msi")]}
            # foo.get_probability(img[50,30,:])
            # "r": { "func" : lambda image, height: rsvis.tools.rsshow.get_pointcloud(image, height), "param" : [-1,types.index("height")]}
        }
    )
    image = ui.show()
    
    rs_imshow(image)
    cv2.setMouseCallback("image", ui.mouse_event)

    while True:
        key = chr(cv2.waitKeyEx(1) & 0xFF)
        if ui.has_key(key):
            event_result = ui.key_event(key)
            if isinstance(event_result, int) == 1: 
                return 1
            elif isinstance(event_result, np.ndarray):
                image = event_result
            rs_imshow(image)

    cv2.destroyAllWindows()    