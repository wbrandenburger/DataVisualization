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
class ResizingCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, logger=None, **kwargs):
        super(ResizingCanvas, self).__init__(parent, **kwargs)
        self.bind("<Configure>", lambda event=self: self.resize_image(event))

        self.shiftw = self.shifth = 0
        self.set_size(width=self.winfo_reqwidth(), height=self.winfo_reqheight()) 

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
        if not self.shiftw and not self.shifth:
            self.shiftw = self.winfo_reqwidth() + 4 - event.width
            self.shifth = self.winfo_reqheight() + 10 - event.height
            print(self.shiftw, self.shifth)
            self.set_size(width=event.width, height=event.height)

        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        
        self.set_size(width=event.width, height=event.height)
        # resize the canvas 
        self.config(width=self.width, height=self.height)

        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.img = Image.fromarray(img)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_size(self, width=None, height=None):
        self.width = width - self.shiftw
        self.height = height - self.shifth

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_image(self, **kwargs):
        img_resize = self.img.resize((self.width + self.shiftw, self.height + self.shifth))
        self.canvas_img = ImageTk.PhotoImage(image=img_resize)
        super(ResizingCanvas, self).create_image(0, 0, image=self.canvas_img, anchor=NW)

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImageCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, grid=list(), double_button=None, logger=None, **kwargs):
        Canvas.__init__(self, parent, **kwargs)

        self.double_button = double_button if double_button else (lambda x: x)

        self.bind("<Configure>", self.resize_image)
        self.bind("<Button-1>", self.mouse_button_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_released)
        self.bind("<Double-Button-1>", self.mouse_double_button)

        self.set_size([], self.winfo_reqheight(), self.winfo_reqwidth())

        self.mouse_area = list()
        self.mouse_point = list()

        self._grid = 0
        self._grid_settings = grid if grid else [1, 1]

        self._logger = logger

        self._boxes = [ [20, 30, 50, 170], [120, 260, 400, 410]]
        self._color = [23, 210, 100]

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
        
        self.set_size(event)
        
        # resize the canvas 
        self.config(width=self.width, height=self.height)

        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

        self.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_size(self, event, width=None, height=None):
        if not event:
            self.width = width-4
            self.height = height-4
        else:
            self.width = event.width-4
            self.height = event.height-4

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        
        self.img = Image.fromarray(img)
        self.show_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_scale(self):
        wscale = float(self.width+4)/self.img_width
        hscale = float(self.height+4)/self.img_height
        print(wscale, hscale)
        print(self._boxes)
        boxes = [[0,0,0,0],[0,0,0,0]]
        boxes = boxes if isinstance(boxes[0],list) else [boxes]

        for i, box in enumerate(boxes):
            box[0] = int(self._boxes[i][0]*hscale)
            box[1] = int(self._boxes[i][1]*hscale)
            box[2] = int(self._boxes[i][2]*wscale)
            box[3] = int(self._boxes[i][3]*wscale)
        return boxes

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_img(self):
        self.img_resize = self.img.resize((self.width+4, self.height+4))
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
        self.patches = rsvis.utils.patches.Patches(np.asarray(self.img_resize), sub_patch=self._grid_settings, logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_button(self, event):
        if self._grid:
            self.focus_set()
        
            self.mouse_point = [event.x, event.y]

            idx = self.get_img_value()
            
            patch = self.patches.get_patch_from_point(idx)

            # self.double_button(title="Histogram", dtype="img", value=[patch,imgtools.get_histogram(patch)])
            self.double_button(title="Histogram", dtype="img", value=patch)            