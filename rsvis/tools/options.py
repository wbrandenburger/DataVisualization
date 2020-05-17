# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools, imgbasictools, imgcv
from rsvis.utils.height import Height

import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_options(param_specs, param_cloud=dict()):
    options = get_general_options()
    options.extend(get_object_options())
    
    options.extend(get_basic_options())
    
    if "label" in param_specs:
        options.extend(get_label_options())
    if "height" in param_specs:
        if param_cloud:
            options.extend(get_height_options(param_cloud))
    
    return options

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object_options():
    return [
        { 
            "require" : "objects",
            "label" : "Objects",
            "name" : "Grid On/Off",
            "key" : None,
            "description": "Show a grid in the currently displayed image.",
            "command": lambda obj: obj.show_grid()
        },      
        { 
            "require" : "objects",
            "label" : "Objects",
            "name" : "Objects On/Off",
            "key" : None,
            "description": "Show the bounding boxes in the currently displayed image.",
            "command": lambda obj: obj.show_objects()
        },
        { 
            "require" : "objects",
            "label" : "Objects",
            "name" : "Save objects",
            "key" : None,
            "description": "Save displayed objects.",
            "command": lambda obj: obj.write_object()
        },
        { 
            "require" : "objects",
            "label" : "Objects",
            "name" : "Remove selected object",
            "key" : None,
            "description": "Remove the selected object.",
            "command": lambda obj: obj.remove_object()
        },
        { 
            "require" : "objects",
            "label" : "Objects",
            "name" : "Bounding Box",
            "key" : "m",
            "description": "Get the bounding boxes of connected image compenents which belongs to an object class.",
            "command": lambda obj: obj.set_object_boxes(
                imgcv.get_bbox(
                    obj.get_img_from_spec("label")[...,0], 
                    obj.get_class(index=True),
                    label=obj.get_class(),
                    margin=10
                ),
                append=False
            )
        }  
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_general_options():

    return [ 
        { 
            "require" : "image",
            "label" : "Image",
            "name" : "Contrast",
            "key" : "r",
            "description": "Raise the contrast of the currently displayed image.",
            "command": lambda obj: obj.set_img(imgtools.raise_contrast(obj.get_img()))
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_options():
    
    return [ 
        { 
            "require" : "label",
            "label" : "Image",
            "name" : "Projection",
            "key" : "t",
            "description": "Show the mask of one label in current image.",
            "command": lambda obj: obj.set_img(
                imgtools.get_label_image(
                    obj.get_img_from_spec("image"), 
                    obj.get_img_from_spec("label"), 
                    index=obj.get_class(index=True),
                    equal=False)
                )
        },
        { 
            "require" : "label",
            "label" : "Image",
            "name" : "Distance Transform",
            "key" : "z",
            "description": "Compute the distance transform map of a label given by current label index.",
            "command": lambda obj: obj.set_img(imgtools.project_and_stack(
                    imgtools.get_distance_transform(
                        obj.get_img_from_spec("label")[...,0],
                        index=obj.get_class(index=True),
                    ), dtype=np.uint8, factor=255)
                )
        }     
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_basic_options():
    
    return [ 
        { 
            "require" : "basic",
            "label" : "Image",
            "name" : "Grayscale",
            "key" : None,
            "description": "Convert the current image to a grayscale image.",
            "command": lambda obj: obj.set_img(
                imgbasictools.get_gray_image(
                    obj.get_img()
                )
            )
        },
        { 
            "require" : "basic",
            "label" : "Image",
            "name" : "Inversion",
            "key" : None,
            "description": "Invert the current image.",
            "command": lambda obj: obj.set_img(
                imgbasictools.get_inverted_image(
                    # imgbasictools.get_gray_image(
                        obj.get_img()
                    #)
                )
            )
        },
        { 
            "require" : "basic",
            "label" : "Image",
            "name" : "Manipulation",
            "key" : "p",
            "description": "Manipulate the current image.",
            "command": lambda obj: obj.set_img(
                imgbasictools.get_linear_transformation(
                    obj.get_img(),
                    dm=20,
                    ds=10,
                    logger=obj.get_logger()
                )
            )
        }                
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_height_options(param=dict()):

    return [
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Pointcloud in ccViewer",
            "key" : "c",
            "description": "Open the currently displayed image in ccViewer as pointcloud.",
            "command": lambda obj: Height(param).open("pointcloud",
                [obj.get_img_from_spec("height"), obj.get_img(), []]
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Pointcloud in CC",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: Height(param).open("pointcloud",
                [obj.get_img_from_spec("height"), obj.get_img(), obj.get_img_from_spec("label")],
                opener="editor"
            )
        },           
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Mesh in ccViewer",
            "key" : "v",
            "description": "Open the currently displayed image in ccViewer as mesh.",
            "command": lambda obj: Height(param).open("mesh",
                [obj.get_img_from_spec("height"), obj.get_img(), []]
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Mesh in CC",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: Height(param).open("mesh",
                [obj.get_img_from_spec("height"), obj.get_img(), obj.get_img_from_spec("label")],
                opener="editor"
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Normal image",
            "key" : "n",
            "description": "Compute and show the normal image.",
            "command": lambda obj: obj.set_img(
                Height(param).get_normal_img(obj.get_img_from_spec("height"))
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Pointcloud with normals in CC",
            "key" : None,
            "description": "Compute and show the normal image.",
            "command": lambda obj: Height(param).open("normal", [obj.get_img_from_spec("height"),[],[]], opener="editor"
            )
        },                 
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
# img_cpy = lambda path: imgio.copy_image(path, get_path(path))
# if param_msi:
#   msi_index = rsvis.utils.objindex.ObjIndex(param_msi.copy())
# "key_r": lambda obj: obj.set_img(
#         imgtools.get_sub_img(
#             obj.get_img_from_spec("msi", show=False), 
#             msi_index()
#     ),
#     show=True
# ),
