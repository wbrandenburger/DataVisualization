# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

import cv2

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSShowUI():

    _keys = dict()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, files, loads, keys = dict()):
        self._files = files
        self._load = loads

        self._image_index = 0
        self._file_index = 0
        self.load()

        self._ref_point = []
        
        self.set_keys(keys)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_keys(self, keys):
        if isinstance(keys, dict):
            self._keys = keys

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def load(self):
        self._images = self._load(self._file_index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_event(self, argument):
        # Get the method from 'self'. Default to a lambda.
        if hasattr(self, self.get_method_name(argument)):
            method = getattr(self, self.get_method_name(argument), lambda: "Invalid key")
            # Call the method as we return it
            return method()
        elif argument in self._keys:


            param = [self.show(index=p) for p in self._keys[argument]["param"]]
            # if isinstance(self._keys[argument]["param"], list):
            #     param = [self.show(index=p) for p in self._keys[argument]["param"]]
            #     return self._keys[argument]["func"](*param)
            # else:
            return self._keys[argument]["func"](
                *param, 
                ref_point =self._ref_point 
            )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_event(self, event, x, y, flags, param):
        
        # If the left mouse button was clicked, record the starting
	    # (x, y) coordinates and indicate that cropping is being
	    # performed
        if event == cv2.EVENT_LBUTTONDOWN:
            self._ref_point = [(x, y)]

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            self._ref_point.append((x, y))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def start(self):
        return self.show() 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show(self, index=None):
        if not index or index == -1:
            return self._images[self._image_index]
        return self._images[index]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_method_name(self, argument):
        return 'key_' + str(argument)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def has_key(self, argument):
        return hasattr(self, self.get_method_name(argument)) or argument in self._keys 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_e(self, **kwargs):
        return self.show()

#   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_p(self, **kwargs):
        print("Image: '{0}', Channel: '{1}'\nRegion of Interest: '{2}'".format(self._files, self._image_index, self._ref_point))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_c(self, **kwargs):
        self._ref_point = []

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, **kwargs):
        self._image_index -= 1
        if self._image_index == -1:
            self._image_index = len(self._images)-1
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, **kwargs):
        self._image_index += 1
        if self._image_index == len(self._images):
            self._image_index = 0
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, **kwargs):
        self._file_index -= 1
        if self._file_index == -1:
            self._file_index = self._files-1
        self.load()
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, **kwargs):
        self._file_index += 1
        if self._file_index == self._files:
            self._file_index = 0
        self.load()
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, **kwargs):
        return 1