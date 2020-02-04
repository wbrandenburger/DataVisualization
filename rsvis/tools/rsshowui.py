# ===========================================================================
#   rsshowui.py -------------------------------------------------------------
# ===========================================================================

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
    def event(self, argument):
        # Get the method from 'self'. Default to a lambda.
        if hasattr(self, self.get_method_name(argument)):
            method = getattr(self, self.get_method_name(argument), lambda: "Invalid key")
            # Call the method as we return it
            return method()
        elif argument in self._keys:
            return self._keys[argument](self.show())
    
        # return

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def start(self):
        return self.show() 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show(self):
        return self._images[self._image_index]

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
    def key_e(self):
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self):
        self._image_index -= 1
        if self._image_index == -1:
            self._image_index = len(self._images)-1
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self):
        self._image_index += 1
        if self._image_index == len(self._images):
            self._image_index = 0
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self):
        self._file_index -= 1
        if self._file_index == -1:
            self._file_index = self._files-1
        self.load()
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self):
        self._file_index += 1
        if self._file_index == self._files:
            self._file_index = 0
        self.load()
        return self.show()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self):
        return None
