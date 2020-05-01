# ===========================================================================
#   canvas.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW, N

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ResizingCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, shift=[4,4], logger=None, **kwargs):
        super(ResizingCanvas, self).__init__(parent, **kwargs)
        self.bind("<Configure>", self.resize_image)

        self.shift = shift
        self.set_size([self.winfo_reqwidth(), self.winfo_reqheight()]) 

        self._logger = logger

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
    def resize_image(self, event):
        # determine the ratio of old width/height to new width/height
        event_size = [event.width, event.height]
        scale = [float(e)/s for e, s in zip(event_size, self.size)]
        
        self.set_size(event_size)
        # resize the canvas 
        self.config(width=self.size[0], height=self.size[1])

        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, scale[0], scale[1])

        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.img = Image.fromarray(img)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_size(self, size):
        self.size = [s - sh for s, sh in zip(size, self.shift)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_size(self):
        return [s + sh for s, sh in zip(self.size, self.shift)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_image(self, **kwargs):
        self.img_resize = self.img.resize(self.get_size())
        self.canvas_img = ImageTk.PhotoImage(image=self.img_resize)
        super(ResizingCanvas, self).create_image(0, 0, image=self.canvas_img, anchor=NW)

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImageCanvas(ResizingCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, grid=list(), double_button=None, logger=None, **kwargs):
        super(ImageCanvas, self).__init__(parent, shift=[4,4], **kwargs)

        self.double_button = double_button if double_button else (lambda x: x)

        self.bind("<Button-1>", self.mouse_button_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_released)
        self.bind("<Double-Button-1>", self.mouse_double_button)

        self.mouse_area = list()
        self.mouse_point = list()

        self._grid = 0
        self._grid_settings = grid if grid else [1, 1]

        self._boxes = [ [20, 30, 50, 170], [120, 260, 400, 410]]
        self._color = [23, 210, 100]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.img_size = [img.shape[1], img.shape[0]]
        
        self.img = Image.fromarray(img)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_scale(self):
        scale = [float(s)/i for s, i in zip(self.get_size(), self.img_size)]

        boxes = [[0,0,0,0],[0,0,0,0]]
        boxes = boxes if isinstance(boxes[0],list) else [boxes]

        for i, box in enumerate(boxes):
            box[0] = int(self._boxes[i][0]*scale[1])
            box[1] = int(self._boxes[i][1]*scale[1])
            box[2] = int(self._boxes[i][2]*scale[0])
            box[3] = int(self._boxes[i][3]*scale[0])
        return boxes

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_image(self):
        self.img_resize = self.img.resize(self.get_size())
        self.set_patches()

        img = self.img_resize.copy()
        if self._grid:
            img_grid  = imgtools.get_grid_image(np.asarray(self.img_resize).shape, self.patches.patch)
            img_grid  = imgtools.draw_box(img_grid, [],  self.get_scale(), self._color)
            img_grid = Image.fromarray(
                imgtools.get_transparent_image(img_grid)
            )
            img.paste(img_grid, (0, 0), img_grid)

        self.canvas_img = ImageTk.PhotoImage(image=img)
        super(ResizingCanvas, self).create_image(0, 0, image=self.canvas_img, anchor=NW)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_pressed(self, event):
        self.focus_set()

        self.mouse_area = [(event.x, event.y)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_released(self, event):
        self.focus_set()

        self.mouse_area.append([event.x, event.y])
        self.mouse_point = [event.x, event.y]

        idx = self.get_img_value()
        img = np.asarray(self.img_resize)

        self.logger("Index '{}' with value '{}'".format(idx, img[idx[0], idx[1], :])) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_value(self):
        img = self.img_resize
        idx = [
            int(float(self.mouse_point[1])/float(self.size[1])*float(img.size[1])),
            int(float(self.mouse_point[0])/float(self.size[0])*float(img.size[0]))
        ]
        idx[0] = idx[0] if idx[0] <= img.size[1] else img.size[1]
        idx[1] = idx[1] if idx[1] <= img.size[0] else img.size[0]
        
        return idx

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self):
        self._grid = 0 if self._grid else 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid_settings(self, grid):
        self._grid_settings = grid
        if self._grid: 
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_patches(self):
        self.patches = rsvis.utils.patches.Patches(np.asarray(self.img_resize), sub_patch=self._grid_settings, logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_button(self, event):
        if self._grid:
            self.focus_set()
        
            self.mouse_point = [event.x, event.y]

            idx = self.get_img_value()
            
            patch = self.patches.get_patch_from_point(idx)

            self.double_button(title="Histogram", dtype="img", value=[patch,imgtools.get_histogram(patch)])
            # self.double_button(title="Histogram", dtype="img", value=patch)            