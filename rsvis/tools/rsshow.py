# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.tools.rsshowui
import rsvis.tools.imgcontainer
import rsvis.tools.heightmap
import rsvis.tools.imgtools
import rsvis.tools.imgio
import rsvis.utils.general
import rsvis.tools.objindex

import numpy as np
import os

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(files, specs, path_dir=os.environ.get("TEMP"), path_name="{}", regex=[".*",0], param_label=dict(), param_msi=list(), scale=100, param_dist=dict()):
    
    load = lambda path, spec: rsvis.tools.imgio.get_image(path, spec=spec, param_label=param_label, scale=scale, show=True)

    get_path = rsvis.utils.general.PathCreator(path_dir, path_name, *regex)
    save = lambda path, img: rsvis.tools.imgio.save_image(get_path(path), img)
    copy = lambda path: rsvis.tools.imgio.copy_image(path, get_path(path))

    img_set = list()
    for f_set in files:
        img = rsvis.tools.imgcontainer.ImgListContainer(load=load)
        for f, s  in zip(f_set, specs):
            live = False if s == "label" else True
            img.append(path = f, spec=s, live=live)
        img_set.append(img)

    label_index = rsvis.tools.objindex.ObjIndex(rsvis.tools.imgtools.project_dict_to_img(param_label.copy()))
    if param_msi:
        msi_index = rsvis.tools.objindex.ObjIndex(param_msi.copy())
   
    keys = {
        "key_e" : lambda obj: obj.set_img(
            obj.get_img(),
            show=True
        ),
        "key_n" : lambda obj: obj.set_img(
            rsvis.tools.imgtools.raise_contrast(
                np.array(obj.get_window_img()
                )
            ), 
            show=True
        ),
        "key_m" : lambda obj: obj.set_img(
            rsvis.tools.imgtools.project_and_stack(
                rsvis.tools.imgtools.get_distance_transform(
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
            mesh=True
        ),       
        "key_v": lambda obj: rsvis.tools.heightmap.main(
            np.array(obj.get_window_img()),
            obj.get_img_from_spec("height"), 
            obj.get_img_from_spec("label"),
            normals=True,
            mesh=True,
            ccviewer=False
        ),
        "key_b": lambda obj: obj.set_img(
            rsvis.tools.heightmap.get_normal_image(
                np.array(obj.get_window_img()), 
                obj.get_img_from_spec("height")
            ),
            show=True
        ), 
        "key_l": lambda obj: obj.set_img(
            rsvis.tools.imgtools.get_label_image(
                obj.get_img(), 
                obj.get_img_from_spec("label"), 
                value=label_index(),
                equal=False),                 
            show=True
        ),
        "key_p": lambda obj: save(obj.get_img(path=True), np.array(obj.get_window_img())
        ),
        "key_r": lambda obj: obj.set_img(
                rsvis.tools.imgtools.get_sub_img(
                    obj.get_img_from_spec("msi"), 
                    msi_index()
            ),
            show=True
        ),
        "key_o": lambda obj: copy(obj.get_img(path=True)),
        "key_u": lambda obj: print(np.unique(obj.get_img_from_spec("label")))
    }

    ui = rsvis.tools.rsshowui.RSShowUI(img_set, keys=keys)
    ui.imshow(wait=True)