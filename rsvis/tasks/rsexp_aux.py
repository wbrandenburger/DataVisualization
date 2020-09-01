# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.rsioobject
import rsvis.utils.general as gu
from rsvis.utils import opener, imgtools
import rsvis.utils.logger

from rsvis.utils.height import Height

import cv2
import math
import numpy as np
import pathlib

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
    # images_log_out = rsio.get_param_out(**param_out["log"])

    str_basis_path = pathlib.Path(param_out["image"]["path_dir"])
    for img_container in images_in:    
        for exp in param_exp:
            # dst_list = list()
            # con = None
            for idx_exp in range(exp["iter"]):

                param = dict()
                for key, item in exp["param"].items():
                     param[key] = item[idx_exp]

                src_img = img_container.get_img_from_label(exp["label"]).data
                src_path = img_container.get_img_from_label(exp["label"]).path

                if exp["name"] == "normal":
                    dst = set_normal_img(src_img, param, param_cloud)
            
                path_dir = str(str_basis_path / "{}-{}".format(exp["name"], idx_exp))
                images_out(src_path, dst, path_dir=path_dir)
                # images_log_out(src_path, param, path_dir=path_dir)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def set_normal_img(src, param, param_cloud):
    height = Height(param_cloud)

    height.set_level()
    height.set_param_normal(**param)  
    dst = height.get_normal_img(src,**param)

    return dst
    