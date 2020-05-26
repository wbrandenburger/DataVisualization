# ===========================================================================
#   extimgcv.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

from rsvis.tools.canvas import imgcv

from PIL import Image, ImageTk
import numpy as np
import numpy
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ExtendedImgCv(imgcv.ImgCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        grid=list(), 
        **kwargs
    ):

        super(ExtendedImgCv, self).__init__(parent, **kwargs)
        
        self._channel_flag = 0
        self._idx_channel = self._idx_channel = rsvis.utils.index.Index(3)
        
        #   grid ------------------------------------------------------------
        self._grid_flag = 1
        self._grid_bboxes = None
        self._grid_color = [150, 100, 150]
        self._grid_default = [3, 3]
        self.set_grid(grid=grid)

        #   selection -------------------------------------------------------
        self._selection_color = [100, 150, 100]
        self._selection = { "temporary": list(), "selection": list() }

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
        super(ExtendedImgCv, self).clear(**kwargs)
        self.remove_channel()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear_selection(self, label):
        self._selection[label] = list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_channel(self):
        self._channel_flag = 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_channel(self):
        self._channel_flag = 0
        self._idx_channel.index = 0

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_selection(self, box, label, resize=True):
        self._selection[label] = self.resize_boxes(box, inversion=True)[0] if resize else box

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_selection(self, label, resize=True):
         return self.resize_boxes(self._selection[label])[0] if resize else self._selection[label]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, **kwargs):
        super(ExtendedImgCv, self).set_img(img, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_assembly = super(ExtendedImgCv, self).draw_image(**kwargs)
        
        #   draw grid -------------------------------------------------------
        self.set_grid_bboxes(np.asarray(self._img_draw))
        if self._grid_flag:            
            img_assembly =  imgtools.draw_box(img_assembly, [], self.get_grid_bboxes(), color=self._grid_color, dtype=np.int16)

        #   draw selection --------------------------------------------------
        for selection in self._selection.keys():
            if self._selection[selection]:
                img_assembly = imgtools.draw_box(img_assembly, [], self.get_selection(selection), self._selection_color, dtype=np.int16)

        #   consider alpha channel
        if self._channel_flag:
            self._img_draw = Image.fromarray(
                imgtools.stack_image_dim(
                    np.asarray(self._img_draw)[..., self._idx_channel()]
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
        self.create_image()

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
        self._idx_channel.next()
        self.show_channel()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_ctrl_y(self, event, **kwargs):
        """Show the previous single channel of current image."""
        self._idx_channel.last()
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
        self.set_selection(self.get_event_box(event), "temporary")
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        super(ExtendedImgCv, self).mouse_button_1_pressed(event)
        self.clear_selection("temporary")
        self.clear_selection("selection")

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        super(ExtendedImgCv, self).mouse_button_1_released(event)
        self._mouse_selection = self.get_selection("temporary", resize=False)
        
        self.clear_selection("temporary")
        self.create_image()