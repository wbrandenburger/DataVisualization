# ===========================================================================
#   extcanvas.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

import rsvis.tools.rescanvas

from PIL import Image, ImageTk
import numpy as np
import numpy
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ExtendedCanvas(rsvis.tools.rescanvas.ResizingCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        grid=list(), 
        **kwargs
    ):

        super(ExtendedCanvas, self).__init__(parent, **kwargs)
        
        self._channel_flag = 0
        self._index_channel = self._index_channel = rsvis.utils.index.Index(3)
        
        #   grid ------------------------------------------------------------
        self._grid_flag = 1
        self._grid_bboxes = None
        self._grid_color = [150, 100, 150]
        self._grid_default = [3, 3]
        self.set_grid(grid=grid)

        #   selection -------------------------------------------------------
        self._selection_color = [150, 100, 150]
        self._selection = list()

        #   key bindings ----------------------------------------------------
        self.bind("<B1-Motion>", self.mouse_motion)

        self.bind("<Control-x>", self.key_ctrl_x)
        self.bind("<Control-y>", self.key_ctrl_y)
        self.bind("<Control-e>", self.key_ctrl_e)
        self.bind("<Control-Shift-F>", self.key_ctrl_shift_f)

        self._keys.update({
            "ctrl+e": "Show the current original image.",
            "ctrl+x": "Show the next single channel of current image.",
            "ctrl+y": "Show the previous single channel of current image.",
            "ctrl+shift+f": "Show or hide a grid in current image."
        })

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(ExtendedCanvas, self).clear(**kwargs)
        self.remove_channel()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear_selection(self):
        self._selection = list()

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
    def set_selection(self, box, resize=True):
        self._selection = self.resize_boxes(box, inversion=True)[0] if resize else box

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_selection(self, resize=True):
         return self.resize_boxes(self._selection)[0] if resize else self._selection

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        super(ExtendedCanvas, self).set_img(img)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_assembly = super(ExtendedCanvas, self).draw_image(**kwargs)
        
        #   draw grid -------------------------------------------------------
        self.set_grid_bboxes(np.asarray(self._img_draw))
        if self._grid_flag:            
            img_assembly =  imgtools.draw_box(img_assembly, [], self.get_grid_bboxes(), color=self._grid_color, dtype=np.int16)

        #   draw selection --------------------------------------------------
        if self._selection:
            img_assembly =  imgtools.draw_box(img_assembly, [], self.get_selection(), self._selection_color, dtype=np.int16)

        #   consider alpha channel
        if self._channel_flag:
            self._img_draw = Image.fromarray(imgtools.project_and_stack(
                np.asarray(self._img_draw)[..., self._index_channel()], 
                    dtype=np.uint8, 
                    factor=255
                )
            )

        return img_assembly

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self, grid=list()):
        self._grid = grid if grid else self._grid_default

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_grid_bbox(self, event):
        return self._grid_bboxes.get_bbox_from_point(
            self.resize_event(event))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_grid_bboxes(self):
        return self._grid_bboxes.get_bbox()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid_bboxes(self, img):
        self._grid_bboxes = rsvis.utils.patches_ordered.OrderedPatches(
            img, num_patches=self._grid)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_grid(self):
        self._grid_flag = 0 if self._grid_flag else 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_e(self, event, **kwargs):
        """Show current original image."""
        self.clear()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_x(self, event, **kwargs):
        """Show the next single channel of current image."""
        self._index_channel.next()
        self.show_channel()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_y(self, event, **kwargs):
        """Show the previous single channel of current image."""
        self._index_channel.last()
        self.show_channel()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_shift_f(self, event, **kwargs):
        """Show or hide a grid in current image."""
        self.show_grid()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_motion(self, event):
        self.focus_set()
        self._mouse_event = self.resize_event(event)
        self.set_selection(self.get_event_box(event))
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        super(ExtendedCanvas, self).mouse_button_1_released(event)
        self._mouse_selection = self._selection
        self.clear_selection()