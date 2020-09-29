# ===========================================================================
#   patches_ordered_ext.py --------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.patches_ordered

import math
import numpy as np

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class OrderedPatchesExt(rsvis.utils.patches_ordered.OrderedPatches):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        img,
        stride=list(),
        **kwargs
    ):
        super(OrderedPatchesExt, self).__init__(img, **kwargs)

        self._stride = stride if stride else list()
        strides_tmp=[0,0,0,0]
        self._strides=list()

        spacing=self.spacing
        if stride:
            bboxes = self._bbox.copy()

            for idx in stride:
                strides_tmp[0] = int(math.floor(idx[0]*spacing[0]))
                strides_tmp[1] = int(math.floor(idx[0]*spacing[0]))
                strides_tmp[2] = int(math.floor(idx[1]*spacing[1]))
                strides_tmp[3] = int(math.floor(idx[1]*spacing[1]))

                self._strides.append(strides_tmp.copy())

                for bbox in bboxes:
                    bbox_temp =  [bbox[0]+strides_tmp[0], bbox[1]+strides_tmp[1], bbox[2]+strides_tmp[2], bbox[3]+strides_tmp[3]]
                    if not bbox_temp[1] > img.shape[0] and not bbox_temp[3] > img.shape[1]: 
                        self._bbox.append(bbox_temp)

        self._len = len(self._bbox)
