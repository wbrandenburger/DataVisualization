# ===========================================================================
#   imagetools.py -----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.utils.patches

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from PIL import Image
from io import BytesIO

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_array_info(img, verbose=False):
    info_str = "Shape: {}, Type: {}, Range: {:.3f}, {:.3f}".format(img.shape, img.dtype, np.min(img), np.max(img))

    if verbose: 
        info_str = "{}, Stats: {:.3f}, {:.3f}".format(info_str, np.mean(img), np.std(img))
    
    return info_str

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_volume(array):
    volume = 1
    for item in array:
        volume *= item
    return volume

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def bool_img_to_uint8(img):
    return img.astype(np.uint8)*255

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def expand_image_dim(img):
    return np.expand_dims(img, axis=2) if len(img.shape) != 3 else img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def stack_image_dim(img):
    if len(img.shape) != 3:
        return np.stack([img]*3, axis=2)
    elif img.shape[2] == 1:
        return np.stack([img[...,0]]*3, axis=2)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def resize_img(img, scale):

    width = int(img.shape[1] * scale / 100.)
    height = int(img.shape[0] * scale / 100.)
    dim = (width, height) 

    img = cv2.resize(img, dim,  interpolation=cv2.INTER_NEAREST)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def project_and_stack(img, dtype=np.float32, factor=1.0):
    img = stack_image_dim(project_data_to_img(img, dtype=dtype, factor=factor))
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def project_data_to_img(img, dtype=np.float32, factor=1.0):
    img = img.astype(np.float32)
    min_max_img = (np.min(img), np.max(img))
    if min_max_img[1] - min_max_img[0] != 0:
        img = (img - min_max_img[0])/(min_max_img[1] - min_max_img[0]) 
    
    img *= factor
    img = img.astype(dtype)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def project_dict_to_img(obj, dtype=np.float32, factor=1.0):
    img = np.fromiter(obj.values(), dtype=dtype)
    return project_data_to_img(img, dtype=dtype, factor=factor)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_histogram(img,alpha=0.7):    
    fig = plt.figure(dpi=64)
    color = ('b','g','r')
    for channel, col in enumerate(color):
        histr = cv2.calcHist([img], [channel], None, [256], [0,256])
        plt.plot(histr, color = col)
        plt.xlim([0,256])
    plt.title('Histogram for color scale picture')

    png1 = BytesIO()
    fig.savefig(png1, format='png')
    hist = np.asarray(Image.open(png1))
    png1.close()
    plt.close()
    
    return hist

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def raise_contrast(img):
    for c in range(0, img.shape[2]):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img[:,:,c] = clahe.apply(img[:,:,c])

    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def labels_to_image(img, labels):
    img = expand_image_dim(img).astype(int)
    dim = img.shape
    label = np.zeros((img.shape[0], img.shape[1]), dtype=int)
    for c in range(img.shape[-1]):
        label += img[:, :, c]*int(pow(2, c))
    
    lut = lambda x: labels[str(x)]
    np_lut = np.vectorize(lut, otypes=[np.uint8])
    label = np_lut(label.astype(int))
    return label

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_image(img, label, value, equal=True):
    rsvis.__init__._logger.debug("Create label image '{}' with value '{}'".format(np.unique(label), value))

    img_label = img.copy()
    for c in range(img.shape[-1]):
        if equal:
            mask = np.ma.masked_where(label[...,-1] == value, img[...,c])
        else:
            mask = np.ma.masked_where(label[...,-1] != value, img[...,c])
                    
        np.ma.set_fill_value(mask, 0)
        img_label[..., c] = mask.filled()
    return img_label

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_mask(label, label_list=None, equal=True):
    if not label_list:
        label_list = np.unique(label)

    label_mask = np.ndarray(
        (label.shape[0], label.shape[1], len(label_list)), 
        dtype=np.uint8
    )

    for c, l in enumerate(label_list):
        if equal:
            mask = np.ma.masked_where(label == l, label)
        else:
            mask = np.ma.masked_where(label != l, label)
                    
        label_mask[..., c] = bool_img_to_uint8(mask.mask)
    return label_mask

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_connected_components(img, connectivity=8):
    # The components are encoded in result[1]
    return cv2.connectedComponentsWithStats(img, connectivity, cv2.CV_32S)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_distance_transform(img, label=0, threshold=10):
    mask_class = ndimage.distance_transform_edt(get_label_mask(img, label_list=[label], equal=True).astype(float))
    mask_non_class = ndimage.distance_transform_edt(get_label_mask(img, label_list=[label], equal=False).astype(float))

    distm = np.where(mask_class < threshold, mask_class, threshold) - np.where(mask_non_class < threshold, mask_non_class, threshold)
    return distm

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_sub_img(img, channels):
    return img[...,channels]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_grid_image(img, shape, bbox, color=[255, 0 ,0]):
    if not hasattr(img, "shape"):
        img = np.zeros(shape[0:2], dtype=np.uint8)

    for idx, box in enumerate(bbox):
        for i in range(len(box)):
            box[i] = box[i]-1 if box[i] else box[i]
        img[box[0]:box[1] + 1, box[2], :] = np.array(color)
        img[box[0]:box[1] + 1, box[3], :] = np.array(color)
        img[box[0], box[2]:box[3] + 1, :] = np.array(color)
        img[box[1], box[2]:box[3] + 1, :] = np.array(color)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def draw_box(img, shape, bbox, color):
    if not hasattr(img, "shape"):
        img = np.zeros(shape[0:2], dtype=np.uint8)

    for idx, box in enumerate(bbox):
        for i in range(len(box)):
            box[i] = box[i]-1 if box[i] else box[i]
        img[box[0]:box[1] + 1, box[2], :] = np.array(color[idx])
        img[box[0]:box[1] + 1, box[3], :] = np.array(color[idx])
        img[box[0], box[2]:box[3] + 1, :] = np.array(color[idx])
        img[box[1], box[2]:box[3] + 1, :] = np.array(color[idx])
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_transparent_image(img, method="any"):
    # Creating RGBA images
    # https://pythoninformer.com/python-libraries/numpy/numpy-and-images/
    alpha_img = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
    alpha_img[:, :, 0:3] = img
    if method=="any":
        alpha_img[:,:,3] = np.where(np.sum(img, axis=2)>0, 255, 0)
    return alpha_img