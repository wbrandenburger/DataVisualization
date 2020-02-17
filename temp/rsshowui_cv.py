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
    def __init__(self, data, keys=dict()):
        self._data = data
        self.set_keys(keys)

        self.clear()
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_keys(self, keys):
        if isinstance(keys, dict):
            self._keys = keys
        else:
            self._keys = dict()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_key_event_name(self, arg):
        return 'key_' + str(arg)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def has_key(self, arg):
        return hasattr(self, self.get_key_event_name(arg)) or arg in self._keys 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_event(self, arg, **kwargs):
        # Get the method from 'self'. Default to a lambda.
        key_event_name = self.get_key_event_name(arg)
        if hasattr(self, key_event_name):
            method = getattr(self, key_event_name, lambda: "Invalid key")
            # Call the method as we return it
            return method()
        elif arg in self._keys:

            param = [self.show(index=p) for p in self._keys[arg]["param"]]
            return self._keys[arg]["func"](
                *param, 
                ref_point =self._ref_point,
                **kwargs 
            )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self):
        self._mouse_area = None
        self._mouse_point = None

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imshow(self, wait=False):
        
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.imshow("image", self._data[0][0].data)

        if wait:
            self.wait()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def wait(self):
        while True:
            key = chr(cv2.waitKeyEx(1) & 0xFF)
            if self.has_key(key):
                event_result = self.key_event(key)
                if isinstance(event_result, int) == 1: 
                    return 1
                elif isinstance(event_result, np.ndarray):
                    image = event_result
                self.imshow(image)
        
        cv2.destroyAllWindows() 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_q(self, **kwargs):
        return 1

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_event(self, event, x, y, flags, param):
        
        # If the left mouse button was clicked, record the starting
	    # (x, y) coordinates and indicate that cropping is being
	    # performed
        point = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self._mouse_area = [point]

        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            self._mouse_area.append(point)
            self._mouse_point = point