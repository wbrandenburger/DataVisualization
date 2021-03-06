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
        label_id[c["name"]] = c["id"]

    aircraft_rejected = 0
    count_patches = 0
    param = param_exp
    for img_container in tqdm(images_in):              

        src_img = img_container.get_img_from_label(param["label"]).data
        src_path = img_container.get_img_from_label(param["label"]).path

        
        patches = rsvis.utils.patches_ordered_ext.OrderedPatchesExt(src_img, limit=param["limit"], num_patches=param["num_patches"], stride=param["stride"])

        objects = objects_cowc = list()
        if param["objects"]:
            objects = rsio.get_object_in(src_path)
            objects_cowc = [rsvis.utils.bbox.BBox().get_cowc(obj["box"], dtype="polyline") for obj in objects]

        for patch in patches:
            patch_meta_write=""

            if param["objects"]:
                for obj, obj_cowc in zip(objects, objects_cowc):
                    if patch.is_point_in_current_bbox([obj_cowc[0], obj_cowc[1]]):
                        count_patches += 1
                        point_x= (obj_cowc[1]-patch.bbox[2])/patches.spacing[1]
                        diff_x = obj_cowc[3]/patches.spacing[1]
                        point_y=(obj_cowc[0]-patch.bbox[0])/patches.spacing[0]
                        diff_y = obj_cowc[2]/patches.spacing[0]
                        cowc=[point_x, point_y, diff_x, diff_y]
                        
                        if cowc[2] < param["reject"][0] or cowc[3] < param["reject"][0] or cowc[2] > param["reject"][1] or cowc[3] > param["reject"][1]:
                            aircraft_rejected += 1
                        else:
                            label = 1
                            if param["use-class"]:
                                label = label_id[obj["label"]]
                            patch_meta_write = "{}{} {} {} {} {}\n".format(patch_meta_write, label, *cowc)

            if param["empty_patches"] or patch_meta_write:

                if patch_meta_write == "":
                    patch_meta_write = "0"

                patch_data = dict()
                patch_raw = patch.get_current_patch()
                width = int(np.floor(patch_raw.shape[1] / param["mod_scale"]))
                height = int(np.floor(patch_raw.shape[0] / param["mod_scale"]))

                if "hr" in param["process"]:
                    if len(patch_raw.shape) == 3:
                        patch_data["hr"] = patch_raw[0:param["mod_scale"]* height, 0:param["mod_scale"] * width, :]
                    else:
                        patch_data["hr"] = patch_raw[0:param["mod_scale"] * height, 0:param["mod_scale"] * width]
                if "lr" in param["process"]:
                    patch_data["lr"] = rsvis.utils.utils_gan.imresize_np(patch_data["hr"], 1 / param["up_scale"], True)
                if "bic" in param["process"]:
                    patch_data["bic"] = rsvis.utils.utils_gan.imresize_np(patch_data["lr"], param["up_scale"], True)

                for patch_key in param["process"]:
                    
                    name="{}-{}-{}-{}-{}-{{}}".format(patch_key, *patch.bbox)
                    images_out(src_path, patch_data[patch_key], **param["dir"][patch_key], name=name)
                    
                    if param["objects"]:
                        images_log_out(src_path, patch_meta_write, **param["dir"][patch_key], name=name)


                    # images_log_out(src_path, param, path_dir=path_dir)

    print("Out: {}, Rejected: {}".format(count_patches-aircraft_rejected, aircraft_rejected))
