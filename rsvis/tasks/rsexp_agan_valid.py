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

    # images_in = rsio.get_img_in()
    # images_out = rsio.get_img_out(img_name="image")
    # images_log_out = rsio.get_log_out(**param_out["log"])

    param = param_exp
    path = param["dir"]
    # files = glob.glob(param_exp["hr"])

    if not os.path.exists(param["val_dir"]):
        os.mkdir(param["val_dir"])

    for key in path.keys():
        val_dir = os.path.join(param["val_dir"], key)
        if not os.path.exists(val_dir):
            os.mkdir(val_dir)


    for key in tqdm(path.keys()):

        filepaths_log = [f for f in os.listdir(path[key]) if f.endswith(".txt")]
        filepaths_img = [f for f in os.listdir(path[key]) if not f.endswith(".txt")]

        empty_files = list()
        for file_log, file_img in zip(filepaths_log, filepaths_img):
            filepath_log = os.path.join(path[key],file_log)
            filepath_img = os.path.join(path[key],file_img)
            with open(filepath_log) as f:
                for line in f:
                    values = (line.split())
                    if "\ufeff" in values[0]:
                        values[0] = values[0][-1]
                    
                    value = int(values[0])
                    if value == 0:
                        empty_files.append([filepath_log, filepath_img])

        print("Empty patches: {}/{}".format(len(empty_files),len(filepaths_log)))

        if not param["remove"]:
            break

        if len(empty_files)>0:
            step = math.floor(len(filepaths_log)/((len(filepaths_log)-len(empty_files))*param["empty_factor"]))
            
            remain = 0
            for idx, file in enumerate(empty_files):
                if idx % step != 0:
                    os.remove(file[0])
                    os.remove(file[1])
                else: 
                    remain += 1

            print("Remaining empty patches: {} of {}".format(remain, len(empty_files)))

    if param["use_val"] != 0:
        for key in tqdm(path.keys()):
            filepaths = [f for f in os.listdir(path[key]) if not f.endswith(".txt")]

            remain = len(filepaths)*param["val_factor"]
            step = int(len(filepaths)/remain)
            file_range = range(0, len(filepaths), step)

            for idx_file in file_range:
                # print(filepaths[idx_file])

                file = filepaths[idx_file]

                val_dir = os.path.join(param["val_dir"], key)
                basename, ext = os.path.splitext(file)
                
                src_img  = os.path.join(path[key], file)
                dest_img = os.path.join(val_dir, file)

                if param["action"]=="move":
                    shutil.move(src_img, dest_img)
                else:
                    shutil.copy(src_img, dest_img)
                
                src_meta  = os.path.join(path[key], basename + ".txt")
                dest_meta = os.path.join(val_dir, basename + ".txt")
                
                if param["action"]=="move":
                    shutil.move(src_meta, dest_meta)
                else:
                    shutil.copy(src_meta, dest_meta)            

                # print(src_img)
                # print(dest_img)
                # print(src_meta)
                # print(dest_meta)
