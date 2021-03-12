# ===========================================================================
#   imagetools.py -----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.utils.patches
import rsvis.utils.bbox

import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as clr
from scipy import ndimage
from scipy.stats import norm
from PIL import Image
from io import BytesIO
from skimage import morphology, color


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def plot_image(w, h, plot_list):
    dpi = 100
    fig = Figure(figsize=(5, 5), dpi=dpi)
    # A canvas must be manually attached to the figure (pyplot would automatically do it).  This is done by instantiating the canvas with the figure as argument https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
    canvas = FigureCanvas(fig)
    # fig.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
    #             hspace = 0, wspace = 0)

    ax = fig.add_subplot(111)
    ax=fig.add_axes([0,0,1,1]) #position: left, bottom, width, height
    ax.set_axis_off()

    for pl in plot_list:
        pl(ax)

    canvas.draw()
    s, (width, height) = canvas.print_to_buffer()

    # Option 2a: Convert to a NumPy array.
    plot = np.fromstring(s, np.uint8).reshape((height, width, 4))
    return plot

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def plot_laplacian(img, threshold=0):

    # convert gray image
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # define the colormap
    cmap = plt.get_cmap('PuOr')

    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    cmaplist = cmaplist[::-1]
    # create the new map
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # Set color value depending on the Laplacian
    C = cv2.Laplacian(img_gray, cv2.CV_16S)

    # x, y are coordinates for the scatter plot and val represents the
    # Laplacian value at the corresponding coordinates
    x = []
    y = []
    val = []

    for iy, col in enumerate(C):
        for ix, row in enumerate(col):
           if(abs(row) >= threshold):
               x.append(ix)
               y.append(iy)
               val.append(row)

    plot_list = []
    # Generate scatter plot and show image
    plot_list.append(lambda ax: ax.imshow(img_gray, cmap="gray"))
    plot_list.append(lambda ax: ax.scatter(x, y, c=val, cmap=cmap, linewidths=2.5))

    return plot_image(img.shape[0], img.shape[1], plot_list)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------


def plot_gradient(img, threshold=0):

    # convert gray image
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate gradients
    # The gradient is computed using central differences in the interior and first differences
    # at the boundaries.
    dY, dX = np.gradient(img_gray)

    C = []
    X = []
    Y = []
    dXFiltered = []
    dYFiltered = []

    rowcount, colcount = dX.shape

    # Filter gradients by grad_threshold
    # Normalize gradients for equal arrow size in quiver plot
    # Set C as the magnitude for color representation of grad strength
    for irow in range(0, rowcount):
        for icol in range(0, colcount):
            gradx = dX[irow][icol]
            grady = dY[irow][icol]
            magnitude = math.sqrt(gradx**2 + grady**2)

            if magnitude >= threshold:
                X.append(icol)
                Y.append(irow)
                dXFiltered.append(gradx / magnitude)
                dYFiltered.append(grady / magnitude)
                C.append(magnitude)

    # Generate plot
    q = plt.quiver(X, Y, dXFiltered, dYFiltered, C, cmap="Reds", units="dots")

    plot_list = []
    # Generate scatter plot and show image
    plot_list.append(lambda ax: ax.imshow(img_gray, cmap="gray"))
    plot_list.append(lambda ax: ax.quiver(X, Y, dXFiltered, dYFiltered, C, cmap="Reds", units="dots"))

    return plot_image(img.shape[0], img.shape[1], plot_list)

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
    return img.astype(np.uint8)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def img_to_bool(img, inverted=False):
    img = np.where(img>0, 1, 0).astype(np.uint8)
    return img if not inverted else invert_bool_img(img) 

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_color_map(seg_map, img, alpha=0.0):
    img = stack_image_dim(img)
    img_color = color.label2rgb(np.squeeze(seg_map), img, kind="overlay", bg_label=-1, alpha=alpha)
    print(img_color.shape)
    return img_color


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def invert_bool_img(img):
    img = np.where(img==0, 1, 0).astype(np.uint8)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def bool_to_img(img, color=[1., 1., 1.], dtype=np.float32, factor=1., value=0):
    img = img.astype(dtype)
    color = [c/factor for c in color]

    img_list = list()
    for idx, c in enumerate(color):
        img_list.append(np.where(img==0, value, c))
    return np.stack(img_list, axis=2)*factor

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
def resize_image(img, factor):
    new_shape = (math.ceil(img.shape[0]*factor), math.ceil(img.shape[1]*factor))
    img = cv2.resize(img, (new_shape[1], new_shape[0]), interpolation=cv2.INTER_CUBIC)
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
def zeros_from_img(img, dtype=None, **kwargs):
    dtype = img.dtype if dtype is None else dtype
    return zeros_from_shape(img.shape, dtype=dtype, **kwargs)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def zeros_from_shape(shape, value=0, dtype=np.float32):
    return np.zeros(shape, dtype=dtype) + value

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def gray_image(img):
    if len(img.shape)>2 and img.shape[2]==3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def invert_image(img):
    return cv2.LUT(img, lut = np.arange(255, -1, -1, dtype=np.uint8))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def quantize_image(img, values=8):
    lut = np.array([ np.floor(float(i)/(256./values)) for i in range(0, 256)], dtype=np.uint8)
    return cv2.LUT(gray_image(img), lut = lut)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_linear_transformation(img, dm=0, ds=0, logger=None):

    img_mean_old = np.mean(img)
    img_std_old = np.std(img)

    param_b = (img_std_old + ds) / img_std_old
    param_a = img_mean_old + dm - param_b * img_mean_old

    # lut =  np.array([param_a + float(i) * param_b for i in range(0, 256)], dtype=np.uint8)
    img_new = (param_a+img.astype(np.float)*param_b)
    img_new = np.where(img_new<0.0, 0.0, img_new)
    img_new = np.where(img_new>255.0, 255.0, img_new)
    img_new = img_new.astype(np.uint8)
    
    if logger:
        logger("[MEAN] {:.2f}->{:.2f} [STD] {:.2f}->{:.2f}".format(img_mean_old, np.mean(img_new), img_std_old, np.std(img_new)))

    return img_new

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_histogram(img, mask=None, logger=None):    
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
        hist_channel = cv2.calcHist([img], [channel], mask, [256], [0,256]) / get_area(img)
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
    # labelimg = reduce_image_dim(labelimg)
    if index is not None:
        value = np.unique(label)[index]

    # rsvis.__init__._logger.debug("Create label image '{}' with value '{}'".format(np.unique(label), value))

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
def get_mask_image(labelimg, value=None, index=None, equal=True):
    labelimg = reduce_image_dim(labelimg)
    if index is not None:
        value = np.unique(labelimg)[index]

    if equal:
        maskimg = np.ma.masked_where(labelimg == value, labelimg)
    else:
        maskimg = np.ma.masked_where(labelimg != value, labelimg)
    
    return bool_img_to_uint8(maskimg.mask)

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

# #   function ----------------------------------------------------------------
# # ---------------------------------------------------------------------------
# def get_distance_transform(labelimg, label=0, index=None, threshold=10):
#     labelimg = reduce_image_dim(labelimg)

#     if index is not None:
#         label = np.unique(labelimg)[index]

#     mask_class = ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=True).astype(float))
#     mask_non_class = ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=False).astype(float))

#     distanceimg = np.where(mask_class < threshold, mask_class, threshold) - np.where(mask_non_class < threshold, mask_non_class, threshold)
#     return distanceimg

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_distance_transform(labelimg, label=0, index=None, non_class=True,**kwargs):
    labelimg = reduce_image_dim(labelimg)

    if index is not None:
        label = np.unique(labelimg)[index]

    if non_class:
        return ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=False).astype(float))
    else:
        return ndimage.distance_transform_edt(get_label_mask(labelimg, label_list=[label], equal=True).astype(float))
    
    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_sub_img(img, channels):
    return img[...,channels]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def draw_box(img, shape, boxes, color=[255, 255, 255], dtype=np.uint8):
    if not hasattr(img, "shape"):
        img = np.zeros(shape, dtype=dtype)

    boxes = boxes if isinstance(boxes[0], list) and len(boxes[0])!=2 else [boxes]
    for idx, box in enumerate(boxes):
        c = color if isinstance(color[0], int) else color[idx]
        box = np.int0(np.array(rsvis.utils.bbox.BBox().get_polyline(box)))
        img = cv2.drawContours(img, [box], -1, c, 1)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def draw_box_ext(img, shape, boxes, color=[255, 255, 255], dtype=np.uint8):
    if not hasattr(img, "shape"):
        img = np.zeros(shape, dtype=dtype)

    boxes = boxes if isinstance(boxes[0], list) and len(boxes[0])!=2 else [boxes]
    for idx, box in enumerate(boxes):
        c = color if isinstance(color[0], int) else color[idx]
        box = np.int0(np.array(rsvis.utils.bbox.BBox().get_polyline(box)))
        img = cv2.drawContours(img, [box], -1, c, 1)
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def draw_detection_boxes(img, shape, boxes, color=[255, 255, 255], dtype=np.uint8):
    if not hasattr(img, 'shape'):
        img = np.zeros(shape, dtype=dtype)

    # boxes = boxes if isinstance(boxes[0], list) and len(boxes[0])!=2 else [boxes]
    for idx, box in enumerate(boxes):
        c = color if isinstance(color[0], int) else color[idx]
        # print(c)
        #print(box['box'])
        box_poly = np.int0(np.array(rsvis.utils.bbox.BBox().get_polyline(box['bbox'])))
        img = cv2.drawContours(img, [box_poly], -1, c, 1)
        font = cv2.FONT_HERSHEY_SIMPLEX

        box_min = rsvis.utils.bbox.BBox().get_min(box_poly, 'polyline')
        cv2.putText(img, "{}/{:.2f}".format(box['label'], float(box['probability'])), (box_min[1]-2, box_min[0]-2), font, 0.275, c, 1, cv2.LINE_AA)
    
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_transparent_image(img, method="any", value=255, dtype=np.uint8):
    # Creating RGBA images
    # https://pythoninformer.com/python-libraries/numpy/numpy-and-images/
    alpha_img = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.int16)
    alpha_img[:, :, 0:3] = img
    if method=="any":
        alpha_img[:,:,3] = np.where(np.sum(img, axis=2)>=0, value, 0)
    alpha_img = alpha_img.astype(dtype)
    return alpha_img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def apply_colormap(img, colormap=cv2.COLORMAP_JET):
    if not len(img.shape)==2 and img.shape[2]>1:
        return img

    if not isinstance(img.dtype, np.uint8):
        img = project_data_to_img(img, dtype=np.uint8, factor=255)
    img = cv2.applyColorMap(img, colormap)
    return img

#   function ------------------------------------------------------------
# -----------------------------------------------------------------------
def set_threshold_mask(dst, mask):      
    dst = img_to_bool(dst)
    dst_inv = invert_bool_img(dst)

    if not isinstance(mask, np.ndarray):
        mask = zeros_from_shape(dst.shape, value=1, dtype=np.uint8)

    mask_list = [mask] if isinstance(mask, np.ndarray) else list()
    mask_list.extend([np.where(np.logical_and(dst_inv==1, mask!=0), 1, 0).astype(np.uint8)]) 

    mask_color = [[0, 0, 0]] if isinstance(mask, np.ndarray) else list()
    mask_color.extend([[255, 255, 0]])
    
    mask_alpha = [150] if isinstance(mask, np.ndarray) else list()
    mask_alpha.extend([75])

    mask_invert = [True] if isinstance(mask, np.ndarray) else list()
    mask_invert.extend([False])

    return mask_list, mask_color, mask_invert, mask_alpha

#   function ------------------------------------------------------------
# -----------------------------------------------------------------------
def get_placeholder(img, seg_map,start=1, stop=255, step=3, min_size=200, **kwargs):

    grayimg = gray_image(img)
    gray_seg_map = gray_image(seg_map)
    grayimga = np.where(gray_seg_map<255, grayimg, 255)
    # grayimg = quantize_image(img, 32)
    placex = np.arange(start, stop, step)
    placeh = np.zeros((len(placex)))
    placei = np.zeros((len(placex)))
    placej = np.zeros((len(placex)))

    for value in range(len(placeh)):
        thresh_img = np.where(grayimg<(value+1)*step, 1, 0).astype(np.bool)
        thresh_img_label, num = morphology.label(thresh_img, connectivity=1, return_num=True)
        placeh[value] = num
        thresh_img_label_hist = np.histogram(thresh_img_label, range(0, len(np.unique(thresh_img_label))+1))
        pp = thresh_img_label_hist[0]>min_size
        placei[value-1] = np.count_nonzero(thresh_img_label_hist[0]>min_size)

    for value in range(len(placeh)):
        thresh_img = np.where(grayimga<(value+1)*step, 1, 0).astype(np.bool)
        thresh_img_label, num = morphology.label(thresh_img, connectivity=1, return_num=True)
        placej[value] = num
        # thresh_img_label_hist = np.histogram(thresh_img_label, range(0, len(np.unique(thresh_img_label))+1))
        # pp = thresh_img_label_hist[0]>min_size
        # placei[value-1] = np.count_nonzero(thresh_img_label_hist[0]>min_size)

    placeh = placeh/np.max(placeh)
    placej = placej/np.max(placej) 
    # placej = (placej)/np.max(placej)
    return placeh, placej, placej, placex, grayimga
