# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.rsioobject
import rsvis.utils.general as gu
from rsvis.utils import opener, imgtools
import rsvis.utils.logger

import rsvis.utils.bbox 
import rsvis.utils.patches_ordered_ext
import rsvis.utils.utils_gan

import cv2
import math
import numpy as np
import pathlib
from tqdm import tqdm
import torch
import os
import shutil


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def run(
        files, 
        label, 
        param_in,
        param_out=dict(),
        param_classes=list(),
        param_exp=list(),
        param_cloud=dict(),
        param_show=dict()
    ):

    rsvis.utils.logger.Logger().get_logformat("Start RSExp with the following parameters:", param_label=label, param_in=param_in, param_out=param_out, param_classes=param_classes, param_cloud=param_cloud, param_show=param_show)

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = [c["label"] for c in param_classes]
    param_color = [c["color"] for c in param_classes]
    rsio = rsvis.utils.rsioobject.RSIOObject(files, label, param_in, param_out, param_show, label=param_label, color=param_color
    )

    images_in = rsio.get_img_in()
    images_out = rsio.get_img_out(img_name="image")
    images_log_out = rsio.get_log_out(**param_out["log"])

    label_id = dict()
    for c in param_classes:
        label_id[str(c["id"])] = c["name"]
    # print(label_id)

    param = param_exp
    filepaths = [f for f in os.listdir(param["results"]) if f.endswith(".txt")]
    
    img_obj = [list() for i in range(0, len(images_in))]
    for file in tqdm(filepaths):
        filename, file_extension = os.path.splitext(file) 
        img_param = [int(f) for i, f in enumerate(filename.split("-")) if i > 0]
        
        img_obj[img_param[4]-1].append({'box': img_param[0:4], "file": file})

    for img_idx, (img, obj) in tqdm(enumerate(zip(rsio.get_img_in(), img_obj))):
        msg = ""
        for o in obj:
            root=list()
            with open(os.path.join(param["results"],o["file"]), "r") as f:
                root = ([o.split(" ") for o in f.read().splitlines()])

        
            for r in root:
                if(r):
                    
                    box = [float(r[1])*255, float(r[2])*255, float(r[3])*255, float(r[4])*255]
                    box = rsvis.utils.bbox.BBox().get_minmax(box, dtype="cowc")
                    box = [box[0]+o["box"][2], box[1]+o["box"][0], box[2]+o["box"][2], box[3]+o["box"][0]]
                    msg = "{}{} : {} :  [{}, {}, {}, {}]\n".format(
                        msg, label_id[r[0]], float(r[5])*100, *box
                    )
            
        src_path = img.get_img_from_label(param["label"]).path
        images_log_out(src_path, msg)


    # if not os.path.exists(param["val_dir"]):
    #     os.mkdir(param["val_dir"])

    # for key in path.keys():
    #     val_dir = os.path.join(param["val_dir"], key)
    #     if not os.path.exists(val_dir):
    #         os.mkdir(val_dir)

    # for key in tqdm(path.keys()):
    #     filepaths = [f for f in os.listdir(path[key]) if not f.endswith(".txt")]

    #     remain = len(filepaths)*param["factor"]
    #     step = int(len(filepaths)/remain)
    #     file_range = range(0, len(filepaths), step)

    #     for idx_file in file_range:
    #         # print(filepaths[idx_file])

    #         file = filepaths[idx_file]

    #         val_dir = os.path.join(param["val_dir"], key)
    #         basename, ext = os.path.splitext(file)
            
    #         src_img  = os.path.join(path[key], file)
    #         dest_img = os.path.join(val_dir, file)
    #         shutil.move(src_img, dest_img)
            
    #         src_meta  = os.path.join(path[key], basename + ".txt")
    #         dest_meta = os.path.join(val_dir, basename + ".txt")
    #         shutil.move(src_meta, dest_meta)

    #         # print(src_img)
    #         # print(dest_img)
    #         # print(src_meta)
    #         # print(dest_meta)
