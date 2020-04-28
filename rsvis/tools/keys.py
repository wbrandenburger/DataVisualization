# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.heightmap
from rsvis.utils import imgtools
import rsvis.utils.general as glu

import numpy as np


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_keys(param_specs, img_out, param_label=dict()):
    keys, keys_description = get_general_keys(img_out)
    if "label" in param_specs:
        keys_optional = get_label_keys(param_label)
    
    keys.update(keys_optional[0])
    keys_description.update(keys_optional[1])

    return keys, keys_description

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_general_keys(img_out):

    keys = {
        # Return to the current original image."
        "key_e" : lambda obj: obj.set_img(obj.get_img(), show=True),
        
        # Save the currently displayed image to a given folder.
        "key_r": lambda obj: img_out(obj.get_img(path=True), obj.get_window_img()),
        
        # Raise the contrast of the currently displayed image.
        "key_t" : lambda obj: obj.set_img(imgtools.raise_contrast(obj.get_window_img()), show=True),

        # # Show the histogram of the displayed image.
        # "key_1" : lambda obj:  obj.set_pop_up_img(imgtools.get_histogram(obj.get_window_img())),
    }

    keys_description = {
        "e" : "Return to the current original image.",
        "r" : "Save the currently displayed image to a given folder.",
        "t" : "Raise the contrast of the currently displayed image."
    }

    return keys, keys_description

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_keys(param_label, param=dict()):
    
    label_index = rsvis.utils.objindex.ObjIndex(imgtools.project_dict_to_img(param_label.copy(), dtype=np.uint8, factor=255))        

    keys = {
        # Show the mask of one label in current image."
        "key_f": lambda obj: obj.set_img(imgtools.get_label_image(
                obj.get_img(), 
                obj.get_img_from_spec("label"), 
                value=label_index(),
                equal=False), show=True
        ),  
        # distance transform (label)
        "key_z" : lambda obj: obj.set_img(imgtools.project_and_stack(
                imgtools.get_distance_transform(
                    obj.get_img_from_spec("label")[...,0],
                    label=label_index(),
                    **glu.get_value(param,"distance-transform", dict()),
                ), dtype=np.uint8, factor=255
            ), show=True
        )
    }

    keys_description = {
        "f" : "Show the mask of one label in current image.",
        "z" : "Compute the distance transform map of a label given by current label index."
    }

    return keys, keys_description

# def get_keys(param_msi=dict():        

#         # cloud compare (height)
#         "key_c": lambda obj: rsvis.tools.heightmap.main(
#             obj.get_window_img(), 
#             obj.get_img_from_spec("height"),
#             normals=True,
#             mesh=True,
#             show=True
#         ),       
#         "key_v": lambda obj: rsvis.tools.heightmap.main(
#             obj.get_window_img(),
#             obj.get_img_from_spec("height"), 
#             obj.get_img_from_spec("label"),
#             normals=True,
#             mesh=True,
#             ccviewer=False,
#             show=True
#         ),
#         "key_b": lambda obj: obj.set_img(
#             rsvis.tools.heightmap.get_normal_image(
#                 obj.get_window_img(), 
#                 obj.get_img_from_spec("height"),
#                 show=True,
#             ),
#             show=True
#         )
#     }

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
# "key_u": lambda obj: print(np.unique(obj.get_img_from_spec("label"))), debug

#in rsshow img_cpy = lambda path: rsvis.utils.imgio.copy_image(path, get_path(path))
# "key_o": lambda obj: img_cpy(obj.get_img(path=True)),

# # MSI
# if param_msi:
#   msi_index = rsvis.utils.objindex.ObjIndex(param_msi.copy())
# "key_r": lambda obj: obj.set_img(
#         imgtools.get_sub_img(
#             obj.get_img_from_spec("msi", show=False), 
#             msi_index()
#     ),
#     show=True
# ),
