# ===========================================================================
#   extimgconcv.py- ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
import rsvis.utils.index

from rsvis.tools.canvas import extimgcv

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ExtendedImgConCv(extimgcv.ExtendedImgCv):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent,
        multi_modal=True,
        variables=dict(),         
        **kwargs
    ):

        super(ExtendedImgConCv, self).__init__(parent, **kwargs)

        self._idx_current = 0

        self._img_container = None
        self._idx_label = rsvis.utils.index.Index(0)

        self._multi_modal_flag = multi_modal
        self._labelimg = "label"
        self._heightimg = "height"

        self._variables = variables

        #   key bindings ----------------------------------------------------
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)
        self.bind("<Control-r>", self.key_ctrl_r)

        self._keys.update({
            "w": "Show the next image of the given image set.",
            "s": "Show the previous image of the given image set.",
            "ctrl+r": "Set image to current image container for further analysis." 
        })

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(ExtendedImgConCv, self).clear(**kwargs)
        self._idx_current = 0
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def reload(self):
        self.clear()
        self._idx_label.index = self._idx_current
        self.set_img_from_index(index=self._idx_current)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_labelimg(self, labelimg=None):   
        self._labelimg = "label"
        if labelimg is not None:
            self._labelimg = labelimg  
        elif "labelimg" in self._variables:
            self._labelimg = self._variables["labelimg"]()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_heightimg(self, heightimg=None):   
        self._heightimg = "height"
        if heightimg is not None:
            self._heightimg = heightimg  
        elif "heightimg" in self._variables:
            self._heightimg = self._variables["heightimg"]()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_labelimg(self):  
        return self._variables["labelimg"]() if "labelimg" in self._variables else self._labelimg

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_heightimg(self):  
        return self._variables["heightimg"]() if "heightimg" in self._variables else self._heightimg

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_to_img_container(self, img, label, **kwargs):
        if not self._img_container.is_label(label):
            self._img_container.append(img, label=label, live=False)
            self._idx_label.limit = self._idx_label.limit+1
            self._idx_label.end()
            self._idx_current = self._idx_label()
        else:
            self._logger("Specified label {} does exist in list of image containers.".format(label))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_container(self, img_container, **kwargs):
        self._img_container = img_container
        self._idx_label = rsvis.utils.index.Index(len(self._img_container))
        
        if not self._multi_modal_flag:
            self._idx_label.index = self._idx_current = 0
        else:
            self._idx_label.index = self._idx_current

        self.set_img_from_index(index=self._idx_current, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_from_index(self, index=None, **kwargs):
        self.set_img(self.get_container_img(index=index), **kwargs)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_label(self, label, **kwargs):
        if not self._img_container:
            return

        label = label.format(**{"label": self.get_labelimg(), "height": self.get_heightimg()})

        item = self._img_container.get_img_from_label(label)
        if item is not None:
            return self._img_container.get_img_from_label(label).data
        else:
            raise ValueError("Label '{}' does not exist in current image container.".format(label))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_path(self, **kwargs):
        if not self._img_container:
            return
            
        return self._img_container[self._idx_label()].path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_label(self, **kwargs):
        if not self._img_container:
            return
            
        return self._img_container[self._idx_label()].label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_container(self, index=None, **kwargs):
        if not self._img_container:
            return

        index = self._idx_label() if index is None else index
        return self._img_container[index]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_container_img(self, index=None, path=False):
        if not self._img_container:
            return
        
        index = self._idx_label() if index is None else index
        return self._img_container[index].data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_class(self, value=False, **kwargs):
        cl = gu.get_value(self._variables, "class", None)
        return None if cl is None else cl(value=value)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        self._idx_current = self._idx_label.next() 
        self.set_img_from_index()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        self._idx_current = self._idx_label.last()
        self.set_img_from_index()
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_e(self, event, **kwargs):
        """Show the current original image."""
        self.reload()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_r(self, event, **kwargs):
        """Set image to current image container for further analysis."""
        self.set_img_to_img_container(self.get_img(), self.get_labelimg())        