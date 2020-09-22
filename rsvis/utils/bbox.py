# ===========================================================================
#   bbox.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
from rsvis.__init__ import _logger

import numpy as np
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
        box_arr = np.array(box)
        box_min = np.min(box_arr, axis=0)
        box_max = np.max(box_arr, axis=0)
        box_0_diff = box_max[0]-box_min[0] 
        box_1_diff = box_max[1]-box_min[1] 
        return [box_min[1]+ box_1_diff/2, box_min[0]+ box_0_diff/2, box_1_diff, box_0_diff]


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_polyline(self, box, dtype=None):
        dst = box
        if dtype=="corner":
            dst = self.corner2polyline(box)
        elif dtype=="coco_polyline":
            dst = self.coco2polyline(box)
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
        
    

    
