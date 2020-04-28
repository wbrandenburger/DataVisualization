# ===========================================================================
#   canvas.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImageCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, grid=list(), logger=None, double_button=None, **kwargs):
        Canvas.__init__(self, parent, **kwargs)

        self.double_button = double_button if double_button else (lambda x: x)
        self.bind("<Configure>", self.resize_image)
        self.bind("<Button-1>", self.mouse_button_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_released)
        self.bind("<Double-Button-1>", self.mouse_double_button)

        self.set_size(self.winfo_reqheight()-4, self.winfo_reqwidth()-4)

        self.mouse_area = list()
        self.mouse_point = list()

        self._grid = 0
        self._grid_settings = grid if grid else [1, 1]

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
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        
        self.set_size(event.width, event.height)
        
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

        self.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_size(self, width, height):
        self.width = width-4
        self.height = height-4

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.img = Image.fromarray(img)
        self.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_img(self):
        self.img_resize = self.img.resize((self.width+4, self.height+4))
        self.set_patches()

        img = self.img_resize.copy()
        if self._grid: 
            img_grid = Image.fromarray(imgtools.get_transparent_image(
                imgtools.get_grid_image(np.asarray(self.img_resize).shape, self.patches.patch)
                )
            )
            img.paste(img_grid, (0, 0), img_grid)

        self.canvas_img = ImageTk.PhotoImage(image=img)
        self.create_image(0, 0, image=self.canvas_img, anchor=NW)

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

        self.logger("Index '{}' with value '{}'".format(idx, img[idx[0], idx[1], :])) # info
        # self.logger("point: {}, canvas: {}, image: {}".format(
        #         self. _mouse_point, 
        #         [self.width, self.height],
        #         img.shape
        #     ), 
        #     stream="debug"
        # )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_value(self):
        img = self.img_resize
        idx = [
            int(float(self.mouse_point[1])/float(self.height)*float(img.size[1])),
            int(float(self.mouse_point[0])/float(self.width)*float(img.size[0]))
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
            self.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_patches(self):
        self.patches = rsvis.utils.patches.Patches(np.asarray(self.img_resize), sub_patch=self._grid_settings)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_button(self, event):
        if self._grid:
            self.focus_set()
        
            self.mouse_point = [event.x, event.y]

            idx = self.get_img_value()

            patch = self.patches.get_patch_from_point(idx)
            self.double_button(title="Histogram", dtype="img", value=[patch,imgtools.get_histogram(patch)])