# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools, imgbasictools, imgcv
from rsvis.utils.height import Height

import rsvis.shadow.shdwDetection as sd

import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_options(param_specs, param_cloud=dict()):
    options = get_general_options()
    options.extend(get_object_options())
    
    options.extend(get_basic_options())
    
    options.extend(get_label_options())

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
            "key" : None,
            "description": "Get the bounding boxes of connected image compenents which belongs to an object class.",
            "command": lambda obj: obj.set_object_boxes(
                imgcv.get_bbox(
                    obj.get_img_from_label("{label}"), 
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
            "key" : None,
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
            "key" : None,
            "description": "Show the mask of one label in current image.",
            "command": lambda obj: obj.set_img(
                imgtools.get_label_image(
                    obj.get_img("image"), 
                    obj.get_img_from_label("{label}"), 
                    index=obj.get_class(index=True),
                    equal=False)
                )
        },
        { 
            "require" : "label",
            "label" : "Image",
            "name" : "Distance Transform",
            "key" : None,
            "description": "Compute the distance transform map of a label given by current label index.",
            "command": lambda obj: obj.set_img(imgtools.project_and_stack(
                    imgtools.get_distance_transform(
                        obj.get_img_from_label("{label}"),
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
                    obj.get_img(show=True)
                )
            )
        },
        { 
            "require" : "basic",
            "label" : "Image",
            "name" : "Manipulation",
            "key" : None,
            "description": "Manipulate the current image.",
            "command": lambda obj: obj.set_img(
                imgbasictools.get_linear_transformation(
                    obj.get_img(),
                    dm=20,
                    ds=10,
                    logger=obj.get_logger()
                )
            )
        },
        { 
            "require" : "label",
            "label" : "Image",
            "name" : "Shadow Detection",
            "key" : None,
            "description": "Automatic shadow detection in aerial and terrestrial images.",
            "command": lambda obj: obj.set_img(
                sd.shadowDetection_Santos_KH(
                    obj.get_img()
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
            "key" : "Control-Shift-C",
            "description": "Open the currently displayed image in ccViewer as pointcloud.",
            "command": lambda obj: Height(param).open("pointcloud",
                [obj.get_img_from_label("height"), obj.get_img(), []]
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Pointcloud in CC",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: Height(param).open("pointcloud",
                [obj.get_img_from_label("height"), obj.get_img(), obj.get_img_from_label("{label}")],
                opener="editor"
            )
        },           
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Mesh in ccViewer",
            "key" : "Control-Shift-V",
            "description": "Open the currently displayed image in ccViewer as mesh.",
            "command": lambda obj: Height(param).open("mesh",
                [obj.get_img_from_label("height"), obj.get_img(), []]
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Mesh in CC",
            "key" : None,
            "description": "Open the currently displayed image in CloudCompare as mesh.",
            "command": lambda obj: Height(param).open("mesh",
                [obj.get_img_from_label("height"), obj.get_img(), obj.get_img_from_label("{label}")],
                opener="editor"
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Normal image",
            "key" : "Control-Shift-B",
            "description": "Compute and show the normal image.",
            "command": lambda obj: obj.set_img(
                Height(param).get_normal_img(obj.get_img_from_label("height"))
            )
        },
        { 
            "require" : "height",
            "label" : "Pointcloud",
            "name" : "Open Pointcloud with normals in CC",
            "key" : None,
            "description": "Compute and show the normal image.",
            "command": lambda obj: Height(param).open("normal", [obj.get_img_from_label("height"),[],[]], opener="editor"
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
#             obj.get_img_from_label("msi", show=False), 
#             msi_index()
#     ),
#     show=True
# ),
