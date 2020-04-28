# ===========================================================================
#   patches.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from functools import reduce

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Patches():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, img, limit=list(), margin=list(), pad=0, sub_patch=list(), logger=None):

        self._img = img

        self._limit = limit if limit else self._img.shape[0:2]
        self._margin = margin if margin else [0, 0]

        self._sub_patch = sub_patch if sub_patch else [self.get_sub_patch(self._img.shape[i], limit[i], margin[i]) for i in range(2)] 
        
        self._len = reduce((lambda x, y: x * y), self._sub_patch)

        self.set_patches()

        self._logger = logger

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __len__(self):
        return self._len

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __iter__(self):
        self._index = -1
        return self

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __next__(self):
        if self._index < self._len-1:
            self._index += 1
            return self
        else:
            raise StopIteration

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def logger(self, log_str, stream="info"):
        if self._logger is None:
            return

        if stream == "info":
            self._logger.info(log_str)
        elif stream == "debug":
            self._logger.debug(log_str)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def patch(self):
        return self._patch

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def patch_margin(self):
        return self._patch_margin

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_patch(self, patch):
        return self._img[patch[0]:patch[1], patch[2]:patch[3], :]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_patch_from_point(self, point):
        for patch in self._patch:
            if point[0] >= patch[0] and point[0] < patch[1] and point[1] >= patch[2] and point[1] < patch[3]:

                self.logger("Patch: {}".format(patch))
                return self.get_patch(patch)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_sub_patch(self, shape, limit, margin):
        sub_patch = 1
        while (sub_patch * limit - (sub_patch-1)*margin) < shape: 
            sub_patch = sub_patch + 1
        return sub_patch

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_sub_patch_indices(self, sub_patch, shape):    
        indices = [i*int(shape/float(sub_patch)) for i in range(sub_patch+1)]
        indices[-1] = shape
        return indices

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_patch_margins(self, patch, margin, shape):
        patch[0] = patch[0]-margin[0] if patch[0]-margin[0] > 0 else patch[0]
        patch[1] = patch[1]+margin[0] if patch[1]+margin[0] < shape[0] else patch[1]
        patch[2] = patch[2]-margin[1] if patch[2]-margin[1] > 0 else patch[2]
        patch[3] = patch[3]+margin[1] if patch[3]+margin[1] < shape[1] else patch[3]
        return patch

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_patches(self):    
        self._patch = [[0,0,0,0] for i in range(self._len)]
        self._patch_margin = [[0,0,0,0] for i in range(self._len)]
        
        steps = [self.get_sub_patch_indices(self._sub_patch[i], self._img.shape[i]) for i in range(2)]
        for y in range(self._sub_patch[1]):
            for x in range(self._sub_patch[0]):
                self._patch[self._sub_patch[0]*y+x] = [steps[0][x], steps[0][x+1], steps[1][y], steps[1][y+1]]
                self._patch_margin[self._sub_patch[0]*y+x] = self.set_patch_margins(self._patch[self._sub_patch[0]*y+x].copy(), self._margin, self._img.shape)