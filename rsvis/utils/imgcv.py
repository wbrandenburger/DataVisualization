# ===========================================================================
#   imgcv.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools

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

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_bbox(labelimg, index, label=None, margin=0, connectivity=8, equal=True):
    labelimg = imgtools.reduce_image_dim(labelimg)
    shape = labelimg.shape

    img_label_value = np.unique(labelimg)[index]
    img = imgtools.get_label_mask(labelimg, label_list=[img_label_value], equal=equal)
    
    num_labels, labels , stats, centroids= cv2.connectedComponentsWithStats(img, connectivity, cv2.CV_32S)

    boxes = list()
    for s in stats[1:]:
        boxes.append({
                "box": crop_box([
                    s[1]-margin, 
                    s[1]+s[3]+margin, 
                    s[0]-margin, 
                    s[0]+s[2]+margin
                ], shape), 
                "label": label
            }
        )
    return boxes

#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def crop_box(box, shape):
    point_min = crop_point([box[0], box[2]], shape)
    point_max = crop_point([box[1], box[3]], shape)

    return [point_min[0], point_max[0], point_min[1], point_max[1] ]


#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def crop_point(point, shape):
    point[0] = 0 if point[0] < 0 else point[0]
    point[0] = shape[0] - 1 if point[0] >= shape[0] else point[0]
    
    point[1] = 0 if point[1] < 0 else point[1] 
    point[1] = shape[1] - 1 if point[1] >= shape[1] else point[1]  
    return point


