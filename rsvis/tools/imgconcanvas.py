# ===========================================================================
#   imgconcanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.index

import rsvis.tools.extcanvas

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgConCanvas(rsvis.tools.extcanvas.ExtendedCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent,
        multi_modal=True,
        **kwargs
    ):

        super(ImgConCanvas, self).__init__(parent, **kwargs)

        self._idx_current = 0

        self._img_container = None
        self._idx_spec = rsvis.utils.index.Index(0)

        self._multi_modal_flag = multi_modal

        #   key bindings ----------------------------------------------------
        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)

        self._keys.update({
            "w": "Show the next image of the given image set.",
            "s": "Show the previous image of the given image set."
        })

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(ImgConCanvas, self).clear(**kwargs)
        self._idx_current = 0
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_container(self, img_container, **kwargs):
        self._img_container = img_container
        self._idx_spec = rsvis.utils.index.Index(len(self._img_container))
        
        if not self._multi_modal_flag:
            self._idx_spec.index = self._idx_current = 0
        else:
            self._idx_spec.index = self._idx_current

        self.set_img_from_index(index=self._idx_current, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img_from_index(self, index=None, **kwargs):
        self.set_img(self.get_container_img(index=index), **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_spec(self, spec, **kwargs):
        if not self._img_container:
            return
            
        return self._img_container.get_img_from_spec(spec).data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_path(self, **kwargs):
        if not self._img_container:
            return
            
        return self._img_container[self._idx_spec()].path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_spec(self, **kwargs):
        if not self._img_container:
            return
            
        return self._img_container[self._idx_spec()].spec

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_container(self, index=None, **kwargs):
        if not self._img_container:
            return

        index = self._idx_spec() if index is None else index
        return self._img_container[index]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_container_img(self, index=None, path=False, show=True):
        if not self._img_container:
            return
        
        index = self._idx_spec() if index is None else index
        return self._img_container[index].data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        self._idx_current = self._idx_spec.next() 
        self.set_img_from_index()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        self._idx_current = self._idx_spec.last()
        self.set_img_from_index()
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_e(self, event, **kwargs):
        """Show the current original image."""
        self.clear()
        self._idx_spec.index = self._idx_current
        self.set_img_from_index(index=self._idx_current)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_class(self, **kwargs):
        pass