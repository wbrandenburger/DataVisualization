# ===========================================================================
#   patches.py --------------------------------------------------------------
# ===========================================================================

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Patches():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, img, bbox=list(), logger=None, **kwargs):

        self._img = img

        self._bbox = bbox
        self._len = len(bbox)

        self._logger = logger

        self._index = -1

        self._dtype = "UNORDERED"

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
    def bbox(self):
        if self._index >= 0:    
            return self._bbox[self._index]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def patch(self):
        if self._index >= 0:    
            return self.get_patch(index=self._index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def append(self, bbox):
        self._bbox.append(bbox)
        self._len += 1
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def extend(self, bbox):
        self._bbox.extend(bbox)
        self._len += len(bbox)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_bbox(self, index=None):
        if index:
            return self._bbox[index]
        return self._bbox

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_patch(self, bbox=list(), index=None):
        if index:
            bbox = self._bbox[index]
        return self._img[bbox[0]:bbox[1], bbox[2]:bbox[3], :]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_patches(self, indices=list()):
        if indices:
            return [self.get_patch(index=idx) for idx in indices]
        return [self.get_patch(bbox=box) for box in self._bbox]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_patch_from_point(self, point, patches=list(), indices=list()):
        for idx, bbox in enumerate(self._bbox):
            if point[0] >= bbox[0] and point[0] < bbox[1] and point[1] >= bbox[2] and point[1] < bbox[3]:

                patches.append(self.get_patch(bbox=bbox))
                indices.append(idx)

                if self._dtype=="ORDERED":
                    self.logger("Patch '{}' with index '{}'".format(bbox, idx))
                    return patches[-1]
