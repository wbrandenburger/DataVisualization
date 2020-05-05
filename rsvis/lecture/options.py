# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools
import rsvis.utils.objindex
import rsvis.utils.general as glu
import rsvis.lecture.lecture
import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_options(param_specs, param_label=dict()):
    options = get_general_options()
    options.extend(get_object_options())

    if "label" in param_specs:
        options.extend(get_label_options(param_label))

    options.extend(rsvis.lecture.lecture.lecture_options)
    
    return options

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object_options():

    return [
        { 
            "label" : "Objects",
            "name" : "Objects On/Off",
            "key" : "g",
            "description": "Show the bounding boxes in the currently displayed image.",
            "command": lambda obj: obj.show_objects()
        },
        { 
            "label" : "Objects",
            "name" : "Save objects",
            "key" : None,
            "description": "Save displayed objects.",
            "command": lambda obj: obj.save_object()
        },
        { 
            "label" : "Objects",
            "name" : "Remove selected object",
            "key" : "h",
            "description": "Remove the selected object.",
            "command": lambda obj: obj.remove_object()
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_general_options():

    return [
        { 
            "label" : "General",
            "name" : "Grid On/Off",
            "key" : None,
            "description": "Show a grid in the currently displayed image.",
            "command": lambda obj: obj.show_grid()
        },       
        # { 
        #     "label" : "General",
        #     "name" : "Reload",
        #     "key" : "e",
        #     "description": "Return to the current original image.",
        #     "command": lambda obj: obj.set_img(obj.get_img(), show=True),
        # },
        { 
            "label" : "General",
            "name" : "Contrast",
            "key" : "r",
            "description": "Raise the contrast of the currently displayed image.",
            "command": lambda obj: obj.set_img(imgtools.raise_contrast(obj.get_window_img()), show=True)
        }
    ]

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_label_options(param_label, param=dict()):
    
    label_index = rsvis.utils.objindex.ObjIndex(imgtools.project_dict_to_img(param_label.copy(), dtype=np.uint8, factor=255))        

    return [ 
        { 
            "label" : "Label",
            "name" : "Projection ",
            "key" : "f",
            "description": "Show the mask of one label in current image.",
            "command": lambda obj: obj.set_img(
                imgtools.get_label_image(
                    obj.get_img(), 
                    obj.get_img_from_spec("label"), 
                    value=label_index(),
                    equal=False
                ), show=True
            )
        },
        { 
            "label" : "Label",
            "name" : "Distance Transform",
            "key" : "z",
            "description": "Compute the distance transform map of a label given by current label index.",
            "command": lambda obj: obj.set_img(imgtools.project_and_stack(
                    imgtools.get_distance_transform(
                        obj.get_img_from_spec("label")[...,0],
                        label=label_index(),
                        **glu.get_value(param,"distance-transform", dict()),
                    ), dtype=np.uint8, factor=255
                ), show=True
            )
        }
    ]