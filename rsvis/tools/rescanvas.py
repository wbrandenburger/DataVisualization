# ===========================================================================
#   rescanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ResizingCanvas(Canvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent, 
            shift=[4,4], 
            logger=None, 
            **kwargs
        ):
        super(ResizingCanvas, self).__init__(parent)
        self.bind("<Configure>", self.resize_image)
        
        self._shift = shift
        self.set_size([self.winfo_reqwidth(), self.winfo_reqheight()]) 

        self._parent = parent

        self._logger = logger

        #   key bindings ----------------------------------------------------
        self.bind("<Button-1>", self.mouse_button_1_pressed)

        self._keys = list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        self.focus_set()

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
    def clear(self, **kwargs):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_keys(self, **kwargs):
        return self._keys

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_image(self, event):
        # determine the ratio of old width/height to new width/height
        event_size = [event.width, event.height]
        scale = [float(e)/s for e, s in zip(event_size, self._size)]
        
        self.set_size(event_size)
        # resize the canvas 
        self.config(width=self._size[0], height=self._size[1])

        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, scale[0], scale[1])

        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img):
        self._img = Image.fromarray(img)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img(self):
        return np.asarray(self._img).copy()

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
    def create_image(self, **kwargs):
        self._img_resize = self._img.resize(self.get_size())
        hm = self.draw_image()
        self._canvas_img = ImageTk.PhotoImage(image=hm)
        super(ResizingCanvas, self).create_image(0, 0, image=self._canvas_img, anchor=NW)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        return self._img_resize
