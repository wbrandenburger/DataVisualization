# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__

import cv2
import numpy as np
import tifffile

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(image_path: str, image_type: str):
    image = tifffile.imread(image_path)
    
    if image_type == "msi":
        return show_msi(image)

    image = convert_image_to_color(image)
    if image_type == 'height':
        return correct_image(image)
    elif image_type == 'label':
        return label_to_image(image)
    elif image_type == 'image':
        return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def convert_image_to_color(image):
    if len(image.shape)==1:
        image = np.stack((image,)*3, axis=-1)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_msi(image):   
    image = image.astype(float) 
    index_list = [2,5,7]
    for i in index_list:
        image[:, :, i] = correct_image(image[:, :, i])
    return image[:, :, np.array(index_list)]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def correct_image(image):
    image_corr = image[~np.isnan(image)]
    image = (image - np.min(image_corr)) / np.max(image_corr)
    return image

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def label_to_image(image):
    return image

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSShowUI():
    
    _file_index = 0
    _image_index = 0

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, files, types):
        self._files = files
        self._types = types

        self.load_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def load_image(self):
        self._images = [get_image(f, t) for f, t in zip(self._files[self._file_index], self._types)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def event(self, argument):
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, self.get_method_name(argument), lambda: "Invalid key")
        # rsvis.__init__._logger.debug("Class RSShowUI, method '{0}'".format(self.get_method_name(argument)))
        # Call the method as we return it
        return method()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def start_ui(self):
        self.show_image() 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_image(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image',
            self._images[self._image_index]
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_method_name(self, argument):
        return 'key_' + str(argument)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def has_method(self, argument):
        return hasattr(self, self.get_method_name(argument))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self):
        self._image_index -= 1
        if self._image_index == -1:
            self._image_index = len(self._images)-1
        self.show_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self):
        self._image_index += 1
        if self._image_index == len(self._images):
            self._image_index = 0
        self.show_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self):
        self._file_index -= 1
        if self._file_index == -1:
            self._file_index = len(self._files)-1
        self.load_image()
        self.show_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self):
        self._file_index += 1
        if self._file_index == len(self._files):
            self._file_index = 0
        self.load_image()
        self.show_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self):
        cv2.destroyAllWindows()
        return 1

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(files, types):

    ui = RSShowUI(files, types)
    ui.start_ui()

    while True:
        key = chr(cv2.waitKeyEx(1) & 0xFF)
        if ui.has_method(key):
            if ui.event(key):
                return 1
            
