# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================

# #   method --------------------------------------------------------------
# # -----------------------------------------------------------------------
# def key_event(self, event):
#     # Get the method from 'self'. Default to a lambda.
#     key_event_name = "key_".format(str(event.char))

#     if hasattr(self._canvas, key_event_name):
#         method = getattr(self, key_event_name, lambda: "Invalid key")
#         # Call the method as we return it
#         return method()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def update_key_list(key_list):
    keys = dict()
    for k in key_list:
        keys.update(k)
    return keys
