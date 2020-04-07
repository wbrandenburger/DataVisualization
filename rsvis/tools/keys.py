# ===========================================================================
#   keys.py -----------------------------------------------------------------
# ===========================================================================    
#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.tools.heightmap
from rsvis.utils import imgtools

import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_keys(label_index, img_out, img_cpy, param_dist=dict(), param_msi=dict()):

    if param_msi:
        msi_index = rsvis.utils.objindex.ObjIndex(param_msi.copy())
        
    return {
        "key_e" : lambda obj: obj.set_img(
            obj.get_img(),
            show=True
        ),
        "key_n" : lambda obj: obj.set_img(
            imgtools.raise_contrast(
                np.array(obj.get_window_img()
                )
            ), 
            show=True
        ),
        "key_m" : lambda obj: obj.set_img(
            imgtools.project_and_stack(
                imgtools.get_distance_transform(
                    obj.get_img_from_spec("label")[...,0],
                    label=label_index(),
                    threshold=param_dist["threshold"]
                )
            ),            
            show=True
        ),
        "key_c": lambda obj: rsvis.tools.heightmap.main(
            np.array(obj.get_window_img()), 
            obj.get_img_from_spec("height"),
            normals=True,
            mesh=True,
            show=True
        ),       
        "key_v": lambda obj: rsvis.tools.heightmap.main(
            np.array(obj.get_window_img()),
            obj.get_img_from_spec("height"), 
            obj.get_img_from_spec("label"),
            normals=True,
            mesh=True,
            ccviewer=False,
            show=True
        ),
        "key_b": lambda obj: obj.set_img(
            rsvis.tools.heightmap.get_normal_image(
                np.array(obj.get_window_img()), 
                obj.get_img_from_spec("height"),
                show=True,
            ),
            show=True
        ), 
        "key_l": lambda obj: obj.set_img(
            imgtools.get_label_image(
                obj.get_img(), 
                obj.get_img_from_spec("label"), 
                value=label_index(),
                equal=False),                 
            show=True
        ),
        "key_p": lambda obj: img_out(obj.get_img(path=True), np.array(obj.get_window_img())
        ),
        "key_r": lambda obj: obj.set_img(
                imgtools.get_sub_img(
                    obj.get_img_from_spec("msi", show=False), 
                    msi_index()
            ),
            show=True
        ),
        "key_o": lambda obj: img_cpy(obj.get_img(path=True)),
        "key_u": lambda obj: print(np.unique(obj.get_img_from_spec("label")))
    }
