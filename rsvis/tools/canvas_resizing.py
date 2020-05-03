# ===========================================================================
#   canvas_resizing.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from PIL import Image, ImageTk
from tkinter import Canvas, NW

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