# ===========================================================================
#   patches_ordered.py ------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.patches

from functools import reduce

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class OrderedPatches(rsvis.utils.patches.Patches):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        img, 
        limit=list(), 
        margin=list(), 
        pad=0, 
        num_patches=list(), 
        **kwargs
    ):
        super(OrderedPatches, self).__init__(img, **kwargs)

        self._limit = limit if limit else self._img.shape[0:2]
        self._margin = margin if margin else [0, 0]

        self._num_patches = num_patches if num_patches else [self.get_num_patches(self._img.shape[i], self._limit[i], self._margin[i]) for i in range(2)] 
        
        self._len = reduce((lambda x, y: x * y), self._num_patches)

        self.set_patches()

        self._dtype = "ORDERED"

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_num_patches(self, shape, limit, margin):
        num_patches = 1
        while (num_patches * limit - (num_patches-1)*margin) < shape: 
            num_patches = num_patches + 1
        return num_patches

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_num_patches_indices(self, number, shape):    
        indices = [i*int(shape/float(number)) for i in range(number+1)]
        indices[-1] = shape
        return indices

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_bbox_margins(self, bbox, margin):
        shape = self._img.shape
        bbox[0] = bbox[0]-margin[0] if bbox[0]-margin[0] > 0 else bbox[0]
        bbox[1] = bbox[1]+margin[0] if bbox[1]+margin[0] < shape[0] else bbox[1]
        bbox[2] = bbox[2]-margin[1] if bbox[2]-margin[1] > 0 else bbox[2]
        bbox[3] = bbox[3]+margin[1] if bbox[3]+margin[1] < shape[1] else bbox[3]
        return bbox

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_patches(self):    
        self._bbox = [[0,0,0,0] for i in range(self._len)]
        self._bbox_margin = [[0,0,0,0] for i in range(self._len)]
        
        steps = [self.get_num_patches_indices(self._num_patches[i], self._img.shape[i]) for i in range(2)]
        for y in range(self._num_patches[1]):
            for x in range(self._num_patches[0]):
                self._bbox[self._num_patches[0]*y+x] = [steps[0][x], steps[0][x+1], steps[1][y], steps[1][y+1]]
                self._bbox_margin[self._num_patches[0]*y+x] = self.set_bbox_margins(self._bbox[self._num_patches[0]*y+x].copy(), self._margin)