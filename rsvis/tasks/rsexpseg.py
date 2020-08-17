# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.rsioobject
import rsvis.utils.general as gu
from rsvis.utils import opener, imgtools
import rsvis.utils.logger
import rsvis.utils.imgseg

import rsvis.tools.options
import rsvis.tools.rsshowui

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
        param_show=dict()
    ):

    rsvis.utils.logger.Logger().get_logformat("Start RSExp with the following parameters:", param_label=label, param_in=param_in, param_out=param_out, param_classes=param_classes, param_show=param_show)

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = [c["label"] for c in param_classes]
    param_color = [c["color"] for c in param_classes]
    rsio = rsvis.utils.rsioobject.RSIOObject(files, label, param_in, param_out, param_show, label=param_label, color=param_color
    )

    # #   set the input / output logger
    # logger =  rsvis.utils.logger.Logger(logger=lambda log: self._textbox.insert("1.0", "{}\n".format(log)))
    # data.logger = self._logger
    # opener = opener.GeneralOpener(logger=logger)

    # rsio self._data = data
    images_in = rsio.get_img_in()
    images_out = rsio.get_img_out(img_name="image")
    images_log_out = rsio.get_param_out(**param_out["log"])
    # images_outs = rsio.get_img_out(img_name="attempt")
    # images_out = gu.PathCreator(**self._param_out)

    str_basis_path = pathlib.Path(param_out["image"]["path_dir"])
    for img_container in images_in:    
        for exp in param_exp:
            # dst_list = list()
            # con = None
            for idx_exp in range(exp["iter"]):

                param = dict()
                for key, item in exp["param"].items():
                     param[key] = item[idx_exp]

                img = img_container[0].data
                if "filter" in exp.keys():
                    img = cv2.bilateralFilter(img, **exp["filter"])

                if exp["name"] == "felz": 
                    param["min_size"] = int((img.shape[0]+img.shape[1])/4)
                    _, _, dst = rsvis.utils.imgseg.segmentation_felzenswalb(img, **param) #,boundaries="find")
                elif exp["name"] == "slic": 
                    _, _, dst = rsvis.utils.imgseg.segmentation_slic(img, **param) #,boundaries="find")
                elif exp["name"] == "kmeans": 
                    _, _, dst = rsvis.utils.imgseg.segmentation_kmeans_color(img, **param) #,boundaries="find")                    
                elif exp["name"] == "slic-0": 
                    _, _, dst = rsvis.utils.imgseg.segmentation_slic(img, **param, slic_zero=True) #,boundaries="find")
                elif exp["name"] == "norm": 
                    _, _, dst = rsvis.utils.imgseg.segmentation_norm(img, **param, slic_zero=True) #,boundaries="find")
                dst = imgtools.project_data_to_img(dst, dtype=np.uint8, factor=255) # if boundaries without find

                # dst = imgtools.get_distance_transform(dst, label=1)
                # dst = dst*-1. + 1.

                # if con is None:
                #     con = dst 
                # else:
                #     con += dst
                # dst_list = dst
    
                path_dir = str(str_basis_path / "{}-{}".format(exp["name"], idx_exp))
                images_out(img_container[0].path, dst, path_dir=path_dir)
                images_log_out(img_container[0].path, param, path_dir=path_dir)





            # con /= 9
            # path_dir = str(bbb / "{}-{}".format(exp["name"], "dist"))
            # images_out(img[0].path, con, path_dir=path_dir)
            # log_str = json.dumps(self._csbox_slic.get_dict())