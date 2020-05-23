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
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as clr
from scipy import ndimage
from scipy.stats import norm
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
def get_area(array):
    return array.shape[0] * array.shape[1]

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
def reduce_image_dim(img):
    return np.squeeze(img, axis=2) if len(img.shape) == 3 and img.shape[2]== 1 else img

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
def project_and_stack(img, **kwargs):
    img = stack_image_dim(project_data_to_img(img, **kwargs))
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def project_data_to_img(img, dtype=np.float32, factor=1.0, force=True, limits=list()):
    if not img.dtype == np.uint8 or force:
        img = img.astype(np.float32)
        if not limits:
            limits = [np.min(img), np.max(img)]
        else:
            img = np.where(img<limits[0], limits[0], img)
            img = np.where(img>limits[1], limits[1], img)
            
        if limits[1] - limits[0] != 0:
            img = (img - limits[0])/(limits[1] - limits[0]) 
        
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
def get_histogram(img, alpha=0.7, logger=None):    
    fig = Figure(figsize=(5, 4), dpi=100)
    # A canvas must be manually attached to the figure (pyplot would automatically do it).  This is done by instantiating the canvas with the figure as argument https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
    canvas = FigureCanvas(fig)
    
    ax = fig.add_subplot(111)
    
    if img.shape[-1] == 1:
        color = ("k")
    else:
        color = ("b", "g", "r")
    
    log_mean = "[MEAN]"
    log_std = "[STD]"
    for channel, col in enumerate(color):
        hist_channel = cv2.calcHist([img], [channel], None, [256], [0,256]) / get_area(img)
        ax.plot(hist_channel, color=col)
        
        img_mean = np.mean(img[...,channel])
        img_std = np.std(img[...,channel])
        
        ax.plot(norm.pdf(np.arange(0, 256, 1), img_mean, img_std), color=col, linestyle="--", linewidth=1 )

        ax.set_xlim([0,256])

        log_mean = "{} {}: {:.2f}".format(log_mean, col, img_mean)
        log_std = "{} {}: {:.2f}".format(log_std, col, img_std)
    
    if logger is not None:
        logger("{}\n{}\n".format(log_mean, log_std))

    
    canvas.draw()
    s, (width, height) = canvas.print_to_buffer()

    # Option 2a: Convert to a NumPy array.
    hist_img = np.fromstring(s, np.uint8).reshape((height, width, 4))
    return hist_img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def raise_contrast(img):
    img = stack_image_dim(img)
    for c in range(0, img.shape[2]):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img[:,:,c] = clahe.apply(img[:,:,c])

    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def labels_to_image(labelimg, colors):
    label = np.zeros((labelimg.shape[0], labelimg.shape[1]), dtype=np.uint8)
    for idx, color in enumerate(colors):
        if len(labelimg.shape)==3:
            label += np.uint8(idx+1)*np.all(labelimg==color, axis=-1)
        else:
            label += np.where(labelimg==color, np.uint8(idx+1), np.uint8(0))
    return label

# #   function ----------------------------------------------------------------
# # ---------------------------------------------------------------------------
# def image_to_labels(img, colors):
#     print(np.unique(img))
#     fig = Figure(figsize=(5, 4), dpi=100)
#     canvas = FigureCanvas(fig)
#     colormap = clr.ListedColormap(np.array(colors)/255.)
#     plt.imshow(img, cmap=colormap, vmin=0, vmax=len(colors)-1)
#     canvas.draw()
#     s, (width, height) = canvas.print_to_buffer()
#     labelimg = np.fromstring(s, np.uint8).reshape((height, width, 4))*255
#     return labelimg

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_image(labelimg, label, value=None, index=None, equal=True):
    labelimg = reduce_image_dim(labelimg)
    if index is not None:
        value = np.unique(label)[index]

    rsvis.__init__._logger.debug("Create label image '{}' with value '{}'".format(np.unique(label), value))

    labelimg_new = labelimg.copy()
    for c in range(labelimg.shape[-1]):
        if equal:
            mask = np.ma.masked_where(label[...,-1] == value, labelimg[...,c])
        else:
            mask = np.ma.masked_where(label[...,-1] != value, labelimg[...,c])
                    
        np.ma.set_fill_value(mask, 0)
        labelimg_new[..., c] = mask.filled()
    return labelimg_new

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_mask(labelimg, label_list=None, equal=True):
    if not label_list:
        label_list = np.unique(labelimg)

    label_mask = np.ndarray(
        (labelimg.shape[0], labelimg.shape[1], len(label_list)), 
        dtype=np.uint8
    )

    for c, l in enumerate(label_list):
        if equal:
            mask = np.ma.masked_where(labelimg == l, labelimg)
        else:
            mask = np.ma.masked_where(labelimg != l, labelimg)
                    
        label_mask[..., c] = bool_img_to_uint8(mask.mask)
    return label_mask

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_connected_components(img, connectivity=8):
    # The components are encoded in result[1]
    # num_labels, labels, stats, centroids =  cv2.connectedComponentsWithStats(img, connectivity, cv2.CV_32S)
    return cv2.connectedComponentsWithStats(img, connectivity, cv2.CV_32S)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_distance_transform(labelimg, label=0, index=None, threshold=10):
    labelimg = reduce_image_dim(labelimg)

    if index is not None:
        label = np.unique(labelimg)[index]

    mask_class = ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=True).astype(float))
    mask_non_class = ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=False).astype(float))

    distanceimg = np.where(mask_class < threshold, mask_class, threshold) - np.where(mask_non_class < threshold, mask_non_class, threshold)
    return distanceimg

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_sub_img(img, channels):
    return img[...,channels]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def draw_box(img, shape, boxes, color=[255, 255, 255], dtype=np.uint8):
    if not hasattr(img, "shape"):
        img = np.zeros(shape, dtype=dtype)

    boxes = boxes if isinstance(boxes[0], list) else [boxes]
    for idx, box in enumerate(boxes):
        box = box.copy()
        for i in range(len(box)):
            box[i] = box[i]-1 if box[i] else box[i]

        c = color if isinstance(color[0], int) else color[idx]
   
        img[box[0]:box[1] + 1, box[2], :] = np.array(c)
        img[box[0]:box[1] + 1, box[3], :] = np.array(c)
        img[box[0], box[2]:box[3] + 1, :] = np.array(c)
        img[box[1], box[2]:box[3] + 1, :] = np.array(c)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_transparent_image(img, method="any", dtype=np.uint8):
    # Creating RGBA images
    # https://pythoninformer.com/python-libraries/numpy/numpy-and-images/
    alpha_img = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.int16)
    alpha_img[:, :, 0:3] = img
    if method=="any":
        alpha_img[:,:,3] = np.where(np.sum(img, axis=2)>=0, 255, 0)
    alpha_img = alpha_img.astype(dtype)
    return alpha_img