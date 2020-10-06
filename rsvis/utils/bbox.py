# ===========================================================================
#   bbox.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET

import numpy as np

# difference between coco, pascal voc and ylo format
# https://towardsdatascience.com/coco-data-format-for-object-detection-a4c5eaf518c5

# voc: x_min, y_min, x_max, y_max
# coco: x_min, y_min, width, height
# yolo: x_mid, y_mid, width, height


class BaseBBoxConverter():
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, format_in='YOLO', format_out='VOC', **kwargs):

        formats = ['YOLO', 'VOC', 'COCO']

        self.format_in = format_in
        self.format_out = format_out

        assert self.format_in in formats
        assert self.format_out in formats

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def convert_in(self, *args):
        if self.format_in=='YOLO':
            args = self.bbox_yolo_to_coco(*args)
        if self.format_in=='VOC':
            args = self.bbox_voc_to_coco(*args)

        if self.format_out =='YOLO':
            args = self.bbox_coco_to_yolo(*args)
        if self.format_out=='VOC':
            args = self.bbox_coco_to_voc(*args)

        return args[0], args[1], args[2], args[3]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def convert_out(self, *args):
        if self.format_out=='YOLO':
            args = self.bbox_yolo_to_coco(*args)
        if self.format_out=='VOC':
            args = self.bbox_voc_to_coco(*args)

        if self.format_in =='YOLO':
            args = self.bbox_coco_to_yolo(*args)
        if self.format_in=='VOC':
            args = self.bbox_coco_to_voc(*args)

        return args[0], args[1], args[2], args[3]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_voc_to_coco(self, x1, y1, x2, y2):
        # creating bounding in coco format from voc
        width = x2 - x1
        height = y2 - y1
        return x1, y1, width, height   

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_voc_to_yolo(self, x1, y1, x2, y2):
        # creating bounding in yolo format from voc
        _, _, width, height =  self.bbox_voc_to_coco(x1, y1, x2, y2)
        xm, ym, _, _ = self.bbox_coco_to_yolo(self, x1, y1, width, height)
        return xm, ym, width, height    

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_coco_to_yolo(self, x1, y1, width, height):
        # creating bounding in yolo format from coco
        xm = int(x1 + width/2)
        ym = int(y1 + height/2)
        return xm, ym, width, height

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_coco_to_voc(self, x1, y1, width, height):
        # creating bounding in voc format from coco
        x2 = int(x1 + width)
        y2 = int(y1 + height)
        return x1, y1, x2, y2

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_yolo_to_coco(self, xm, ym, width, height):
        # creating bounding in coco format from yolo
        x1 = int(1 if xm - width/2 <= 0 else int(xm - width/2))
        y1 = int(1 if ym - height/2 <= 0 else int(ym - height/2))
        return x1, y1, width, height

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_yolo_to_voc(self, xm, ym, width, height):
        # creating bounding in voc format from yolo
        x1, y1, _, _  = self.bbox_yolo_to_coco(xm, ym, width, height)
        _, _, x2, y2 = self.bbox_coco_to_voc(self, x1, y1, width, height)
        return x1, y1, x2, y2

class BBoxConverter(BaseBBoxConverter):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self,
        img_width, 
        img_height,
        scale='OBJABS',
        **kwargs
        ):
        super(BBoxConverter, self).__init__(**kwargs)

        scales = ['OBJREL', 'OBJABS']

        self.img_width = img_width
        self.img_height = img_height

        self.scale = scale

        assert self.scale in scales

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def convert_in(self, *args):
        if self.scale == 'OBJREL':
            args = self.rescale_bbox_OBJABS(*args)

        args = super(BBoxConverter, self).convert_in(*args)

        return args[0], args[1], args[2], args[3]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def convert_out(self, *args):
        args = super(BBoxConverter, self).convert_out(*args)

        if self.scale == 'OBJREL':
            args = self.rescale_bbox_OBJREL(*args)

        return args[0], args[1], args[2], args[3]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def rescale_bbox_OBJABS(self, *args):
        # get coordinates within height width range
        x1 = float(args[0])*self.img_width
        y1 = float(args[1])*self.img_height
        x2 = float(args[2])*self.img_width
        y2 = float(args[3])*self.img_height
        return x1, y1, x2, y2

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def rescale_bbox_OBJREL(self, *args):
        # get coordinates within height width range
        x1 = float(args[0])/self.img_width
        y1 = float(args[1])/self.img_height
        x2 = float(args[2])/self.img_width
        y2 = float(args[3])/self.img_height
        return x1, y1, x2, y2

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_coco_to_yolo(self, x1, y1, width, height):
        # creating bounding in yolo format from coco
        xm = int(self.img_width-1 if x1 + width/2 >= self.img_width-1 else int(x1 + width/2))
        ym = int(self.img_height-1 if y1 + height/2 >= self.img_height-1 else int(y1 + height/2))
        return xm, ym, width, height

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def bbox_coco_to_voc(self, x1, y1, width, height):
        # creating bounding in voc format from coco
        x2 = int(self.img_width-1 if x1 + width >= self.img_width-1 else int(x1 + width))
        y2 = int(self.img_height-1 if y1 + height >= self.img_height-1 else int(y1 + height))
        return x1, y1, x2, y2



#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class BBox():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def corner2polyline(self, box):
        return [[box[2], box[0]], 
                [box[2], box[1]],
                [box[3], box[1]],
                [box[3], box[0]],
                [box[2], box[0]]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def polyline2corner(self, box):
        box_arr = np.array(box)
        box_min = np.min(box_arr, axis=0)
        box_max = np.max(box_arr, axis=0)
        return [box_min[1], box_max[1], box_min[0], box_max[0]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def coco2polyline(self, box):
        return [[box[0], box[1]], 
                [box[2], box[3]],
                [box[4], box[5]],
                [box[6], box[7]],
                [box[0], box[1]]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def polyline2cowc(self, box):
        minmax = self.polyline2minmax(box)
        box_0_diff = minmax[3] - minmax[1] # [box_max[0]-box_min[0] 
        box_1_diff = minmax[2] - minmax[0] # box_max[1]-box_min[1] 
        return [minmax[0]+ box_1_diff/2, minmax[1] + box_0_diff/2, box_1_diff, box_0_diff]


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def cowc2polyline(self, box):
        return self.corner2polyline([int(box[1]-box[3]/2),  int(box[1]+box[3]/2), int(box[0]-box[2]/2), int(box[0]+box[2]/2)])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def cowc2minmax(self, box):
        return [ int(box[0]-box[2]/2),  int(box[1]-box[3]/2),int(box[0]+box[2]/2), int(box[1]+box[3]/2)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def polyline2minmax(self, box):
        box_arr = np.array(box)
        box_min = np.min(box_arr, axis=0)
        box_max = np.max(box_arr, axis=0)
        return [box_min[1], box_min[0], box_max[1], box_max[0]]

#   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def minmax2polyline(self, box):
        return [[box[0], box[1]], 
                [box[2], box[1]],
                [box[2], box[3]],
                [box[0], box[3]]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_polyline(self, box, dtype=None):
        dst = box
        if dtype=="corner":
            dst = self.corner2polyline(box)
        elif dtype=="coco_polyline":
            dst = self.coco2polyline(box)
        elif dtype=="cowc":
            dst = self.cowc2polyline(box)
        elif dtype=="minmax":
            dst = self.minmax2polyline(box)
        elif len(box)==4:
            dst = self.corner2polyline(box)
        return dst
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_corner(self, box, dtype=None):
        dst = box
        if dtype=="corner":
            dst = self.polyline2corner(box)
        elif len(box)==5:
            dst = self.polyline2corner(box)
        return dst
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_cowc(self, box, dtype=None):
        dst = box
        if dtype=="polyline":
            dst = self.polyline2cowc(box)            
        return dst
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_minmax(self, box, dtype=None):
        dst = box
        if dtype=="cowc":
            dst = self.cowc2minmax(box)
        if dtype=="polyline":
            dst = self.polyline2minmax(box)                    
        return dst

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_min(self, box, dtype=None):
        dst = box
        if dtype=="cowc":
            dst = self.cowc2minmax(box)            
        if dtype=="polyline":
            dst = self.polyline2minmax(box)
        return dst[0:2]        