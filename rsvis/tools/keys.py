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
def update_keys(list_x, list_y):
    list_c = list_x.copy() if len(list_x) <= len(list_y) else list_y.copy()
    for y in list_y:
        add_flag = True
        
        for x in list_x:
            if y["key"] == x["key"]:
                add_flag = False
        
        if add_flag:
            list_c.append(y)

    return list_c

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def update_key_list(key_list):
    list_c = list()
    for k in key_list:
        list_c = update_keys(list_c, k)
    return list_c
