# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.heightmap
from rsvis.utils import imgtools
import rsvis.utils.objindex
import rsvis.utils.general as glu

import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_options(param_specs, param_label=dict(), param_cloud=dict()):
    options = get_general_options()
    options.extend(get_object_options())

    if "label" in param_specs:
        options.extend(get_label_options(param_label))
    if "height" in param_specs:
        if param_cloud:
            options.extend(get_height_options())
    
    return options

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object_options():

    return [
        { 
            "label" : "objects",
            "name" : "Grid On/Off",
            "key" : None,
            "description": "Show a grid in the currently displayed image.",
            "command": lambda obj: obj.show_grid()
        },      
        { 
            "label" : "objects",
            "name" : "Objects On/Off",
            "key" : None,
            "description": "Show the bounding boxes in the currently displayed image.",
            "command": lambda obj: obj.show_objects()
        },
        { 
            "label" : "objects",
            "name" : "Save objects",
            "key" : None,
            "description": "Save displayed objects.",
            "command": lambda obj: obj.save_object()
        },
        { 
            "label" : "objects",
            "name" : "Remove selected object",
            "key" : None,
            "description": "Remove the selected object.",
            "command": lambda obj: obj.remove_object()
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_general_options():

    return [ 
        { 
            "label" : "image",
            "name" : "Contrast",
            "key" : "r",
            "description": "Raise the contrast of the currently displayed image.",
            "command": lambda obj: obj.set_img(imgtools.raise_contrast(obj.get_img()))
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_options(param_label, param=dict()):
    
    label_index = rsvis.utils.objindex.ObjIndex(imgtools.project_dict_to_img(param_label.copy(), dtype=np.uint8, factor=255))        

    return [ 
        { 
            "label" : "label",
            "name" : "Projection ",
            "key" : "t",
            "description": "Show the mask of one label in current image.",
            "command": lambda obj: obj.set_img(
                imgtools.get_label_image(
                    obj.get_img_from_spec("image"), 
                    obj.get_img_from_spec("label"), 
                    value=label_index(),
                    equal=False)
                )
        },
        { 
            "label" : "label",
            "name" : "Distance Transform",
            "key" : "z",
            "description": "Compute the distance transform map of a label given by current label index.",
            "command": lambda obj: obj.set_img(imgtools.project_and_stack(
                    imgtools.get_distance_transform(
                        obj.get_img_from_spec("label")[...,0],
                        label=label_index(),
                        **glu.get_value(param,"distance-transform", dict()),
                    ), dtype=np.uint8, factor=255)
                )
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_height_options(param=dict()):

    return [
        { 
            "label" : "height",
            "name" : "Open Pointcloud in ccViewer",
            "key" : None,
            "description": "Open the currently displayed image in ccViewer as pointcloud.",
            "command": lambda obj: rsvis.tools.heightmap.main(
                obj.get_img(), 
                obj.get_img_from_spec("height"),
                normals=False,
                mesh=False,
                show=True
            ), 
        },
        { 
            "label" : "height",
            "name" : "Open Mesh in ccViewer",
            "key" : None,
            "description": "Open the currently displayed image in ccViewer as mesh.",
            "command": lambda obj: rsvis.tools.heightmap.main(
                obj.get_img(), 
                obj.get_img_from_spec("height"),
                normals=True,
                mesh=True,
                show=True
            ), 
        },
        { 
            "label" : "height",
            "name" : "Normal image",
            "key" : None,
            "description": "Compute and show the normal image.",
            "command": lambda obj: obj.set_img(
                rsvis.tools.heightmap.get_normal_image(
                    obj.get_img(), 
                    obj.get_img_from_spec("height"),
                    show=True,
                )
            )
        },
        { 
            "label" : "height",
            "name" : "Open Pointcloud in CloudCompare",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: rsvis.tools.heightmap.main(
                obj.get_img(),
                obj.get_img_from_spec("height"), 
                obj.get_img_from_spec("label"),
                normals=False,
                mesh=False,
                ccviewer=False,
                show=True
            ),
        },        
        { 
            "label" : "height",
            "name" : "Open Mesh in CloudCompare",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: rsvis.tools.heightmap.main(
                obj.get_img(),
                obj.get_img_from_spec("height"), 
                obj.get_img_from_spec("label"),
                normals=True,
                mesh=True,
                ccviewer=False,
                show=True
            ),
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
# param_msi=dict():  
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
