# ===========================================================================
#   imgcv.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.logger

import logging
import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            shift=[4,4],
            sensitivity = 4,
            logger=None, 
            **kwargs
        ):
        super(ImgCanvas, self).__init__(parent)
        self.bind("<Configure>", self.resize_image)

        self._mask = [None]
        self._mask_alpha = [150]
        self._mask_color = [[0,0,0]]
        self._mask_invert = [False]
        
        self._shift = shift
        self._scale = [1.0, 1.0]

        self.set_size([self.winfo_reqwidth(), self.winfo_reqheight()]) 
        
        self._parent = parent

        self._logger = rsvis.utils.logger.Logger(logger=logger)

        #   key bindings ----------------------------------------------------
        self._mouse_sensitivity = 4
        self._mouse_box = [0, 0, 0, 0]
        self._mouse_point = [0, 0]
        self._mouse_event = [0, 0]
        self._mouse_img = [0, 0]
        
        self._keys = dict()
        
        self.bind("<Button-1>", self.mouse_button_1_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_1_released)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_keys(self, **kwargs):
        return self._keys

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_logger(self):
        return self._logger

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_image(self, event):
        # determine the ratio of old width/height to new width/height
        event_size = [event.width, event.height] #####################
        self._scale = [float(e)/s for e, s in zip(event_size, self._size)]
        
        self.set_size(event_size)
        # resize the canvas 
        self.config(width=self._size[0], height=self._size[1]) #################

        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, self._scale[0], self._scale[1]) ################

        self.create_image()
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_boxes(self, boxes, inversion=False):
        scale = [float(s)/i for s, i in zip(self.get_size(), self._img_size)]

        if inversion:
            scale = [1/s for s in scale]

        boxes = boxes if isinstance(boxes[0], list) else [boxes]
        return [self.resize_bbox(box, scale) for box in boxes]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_bbox(self, box, scale):  
        return [
            int(box[0]*scale[1]), int(box[1]*scale[1]), 
            int(box[2]*scale[0]), int(box[3]*scale[0])
        ]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_points(self, points, inversion=False):
        scale = [float(s)/i for s, i in zip(self.get_size(), self._img_size)]

        if inversion:
            scale = [1/s for s in scale]

        points = points if isinstance(points[0], list) else [points]
        return [self.resize_point(point, scale) for point in points]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_point(self, point, scale):  
        return [int(point[0]*scale[1]), int(point[1]*scale[0])]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_event(self, event):
        ev = [event.y, event.x]

        ev[0] = ev[0] if ev[0] >= 0 else 0 
        ev[0] = ev[0] if ev[0] < self._img_draw.size[1] else self._img_draw.size[1]-1
        
        ev[1] = ev[1] if ev[1] >= 0 else 0 
        ev[1] = ev[1] if ev[1] < self._img_draw.size[0] else self._img_draw.size[0]-1
        
        return ev

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_event_box(self, event):
        return [ 
            min([self._mouse_point[0], self._mouse_event[0]]),
            max([self._mouse_point[0], self._mouse_event[0]]),
            min([self._mouse_point[1], self._mouse_event[1]]),
            max([self._mouse_point[1], self._mouse_event[1]])
        ]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, clear_mask=True):
        if not isinstance(img, np.ndarray):
            return

        self._img_size = [img.shape[1], img.shape[0]]
        self._data_img = imgtools.expand_image_dim(img)
        if not isinstance(img.dtype, np.uint8):
            img = imgtools.project_and_stack(img, dtype=np.uint8, factor=255)
        
        self._img = Image.fromarray(img)
            
        if clear_mask:
            self.set_mask(show=False)

        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_mask(self, mask=None, show=True, alpha=150, color=[0,0,0], invert=False):
        self._mask = mask if isinstance(mask, list) else [mask]
        self._mask_alpha = alpha  if isinstance(alpha, list) else [alpha]
        self._mask_color = color if isinstance(color[0], list) else [color]
        self._mask_invert= invert if isinstance(invert, list) else [invert]
        if show:
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_mask(self, index=None, resize=False):
        if index is None:
            mask = self._mask[0]
            for idx in range(1, len(self._mask)):
                if isinstance(self._mask[idx], np.ndarray):
                    mask = np.where(np.logical_and(mask, self._mask[idx]), 1, 0).astype(np.uint8)
            return mask
        else:
            if isinstance(self._mask[index], np.ndarray):
                return np.asarray(Image.fromarray(self._mask[index]).resize(self.get_size())) if resize else self._mask[index]
            else:
                return self._mask[index]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def is_mouse_event(self, bbox):
        if not (bbox[1]-bbox[0] > self._mouse_sensitivity and bbox[3]-bbox[2] > self._mouse_sensitivity):
            return False
        return True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img(self, show=False):
        if show:
            return np.asarray(self._img).copy()
        return self._data_img.copy()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_size(self, size):
        self._size = [s - sh for s, sh in zip(size, self._shift)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_size(self):
        return [s + sh for s, sh in zip(self._size, self._shift)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_shape(self):
        size = self.get_size()
        return (size[1], size[0], 3)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_intial_draw_image(self):
        return np.zeros(self.get_shape(), dtype=np.int16) - 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def create_image(self, **kwargs):
        self._img_draw = self._img.resize(self.get_size())

        if isinstance(self._mask[0], np.ndarray):
            for idx, (mask, color, alpha, invert) in enumerate(zip(self._mask, self._mask_color, self._mask_alpha, self._mask_invert)):
                mask = self.get_mask(index=idx, resize=True)
                mask = mask if not invert else imgtools.invert_bool_img(mask)
                mask = Image.fromarray(
                    imgtools.get_transparent_image(
                        imgtools.bool_to_img(mask, value=-1, dtype=np.int16, color=color, factor=255),
                        value=alpha
                    )
                )
                self._img_draw.paste(mask, (0, 0), mask)

        image = Image.fromarray(
            imgtools.get_transparent_image(self.draw_image(), value=200))
        self._img_draw.paste(image, (0, 0), image)
        
        self._img_canvas = ImageTk.PhotoImage(image=self._img_draw)
        super(ImgCanvas, self).create_image(0, 0, image=self._img_canvas, anchor=NW)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_assembly = self.get_intial_draw_image()
        return img_assembly

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        self.focus_set()
        self._mouse_event = self.resize_event(event)
        self._mouse_point = [self._mouse_event[0], self._mouse_event[1]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        self.focus_set()
        self._mouse_event = self.resize_event(event)
        self._mouse_box = self.get_event_box(event)

        self._mouse_img = self.resize_points(self._mouse_event, inversion=True)[0]

        self._logger("[MOUSE] Pixel: {},  Value: {}".format(self._mouse_img,
            self._data_img[self._mouse_img[0], self._mouse_img[1], :]
            )
        )