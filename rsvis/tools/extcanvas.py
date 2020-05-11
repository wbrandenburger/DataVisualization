# ===========================================================================
#   rescanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools

import rsvis.tools.rescanvas

from PIL import Image, ImageTk
import numpy as np
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ExtendedCanvas(rsvis.tools.rescanvas.ResizingCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        shift=[4,4], 
        **kwargs
    ):

        super(ExtendedCanvas, self).__init__(parent, shift=shift, **kwargs)
        
        self._channel_flag = 0
        self._index_channel = self._index_channel = rsvis.utils.index.Index(3)

        #   key bindings ----------------------------------------------------
        self.bind("<x>", self.key_x)
        self.bind("<y>", self.key_y)
        self.bind("<e>", self.key_e)

        self._keys.update({
            "e": "Show the current original image.",
            "x": "Show the next single channel of current image.",
            "y": "Show the previous single channel of current image."
        })

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(ExtendedCanvas, self).clear(**kwargs)
        self.remove_channel()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        super(ExtendedCanvas, self).set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_channel(self):
        self._channel_flag = 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_channel(self):
        self._channel_flag = 0
        self._index_channel.index = 0

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_resize = super(ExtendedCanvas, self).draw_image(**kwargs)
        # consider alpha channel
        if self._channel_flag:
            img_resize = Image.fromarray(imgtools.project_and_stack(
                np.asarray(img_resize)[..., self._index_channel()], 
                    dtype=np.uint8, 
                    factor=255
                )
            )
 
        return img_resize

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_e(self, event, **kwargs):
        """Show current original image."""
        self.clear()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_x(self, event, **kwargs):
        """Show the next single channel of current image."""
        self._index_channel.next()
        self.show_channel()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_y(self, event, **kwargs):
        """Show the previous single channel of current image."""
        self._index_channel.last()
        self.show_channel()
        self.create_image()
