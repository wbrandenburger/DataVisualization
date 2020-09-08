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


from PIL import Image
import matplotlib.pyplot as plt


#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def run(
        files, 
        label, 
        param_in,
        param_out=dict(),
        param_exp=list(),
        param_cloud=dict(),
        param_show=dict()
    ):

    rsvis.utils.logger.Logger().get_logformat("Start RSExp with the following parameters:", param_label=label, param_in=param_in, param_out=param_out, param_cloud=param_cloud, param_show=param_show)

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    rsio = rsvis.utils.rsioobject.RSIOObject(files, label, param_in, param_out, param_show)

    images_in = rsio.get_img_in()
    images_out = rsio.get_img_out(img_name="image")
    # images_log_out = rsio.get_param_out(**param_out["log"])

    # str_basis_path = pathlib.Path(param_out["image"]["path_dir"])
    for exp in param_exp:
        img_list = list()
        img_list_b =list()
        for idx_exp in range(*exp["range"]):
            a = images_in[idx_exp][0].data
            a = (a -np.mean(a))/np.std(a)
            # a = np.where(a<=-1,-1,a)
            # a = np.where(a>=1,1,a)
            img_list.append(np.squeeze(imgtools.project_data_to_img(a)))
            print(np.mean(img_list[-1]), np.std(img_list[-1]))
        # img_list_stacked = np.stack(img_list, axis=2)
        # img_list_stacked_mean = np.mean(img_list_stacked, axis=2)
        # img_list_stacked_std = np.std(img_list_stacked, axis=2)

        img_list_stacked = np.stack(img_list, axis=2)
        # img_list_stacked_mean = np.expand_dims(np.mean(img_list_stacked, axis=2), axis=2)
        img_list_stacked_mean = np.mean(img_list_stacked, axis=2)
        # for idx_exp in range(*exp["range"]):


        # mean_ = np.mean(np.abs(img_list_stacked -  np.stack([img_list_stacked_mean]*len(range(*exp["range"])), axis=2)), axis=2)
        # mean_error = np.mean(np.abs(img_list_stacked - np.stack([np.squeeze(images_in[0][0].data)]*len(range(*exp["range"])), axis=2)), axis=2)
        
        b =  images_in[0][0].data
        # b = (b-0.5)*2.0
        mean_ = imgtools.project_data_to_img(np.mean(np.abs(img_list_stacked -  np.expand_dims(img_list_stacked_mean, axis=2)), axis=2))
        mean_error = np.mean(np.abs(img_list_stacked - images_in[0][0].data), axis=2)

        # np.abs(img_list_stacked- images_in[0][0]).mean(axis=2)
         
        # dst = mean_error
        dst = mean_
        # dst = imgtools.project_data_to_img(img_list_stacked_std)
                # path_dir = str(str_basis_path / "{}-{}".format(exp["name"], idx_exp))
        
        # Get the color map by name:
        cm = plt.get_cmap("jet") #https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
        # Apply the colormap like a function to any array:
        colored_image = cm(dst).reshape((dst.shape[0], dst.shape[1], 4))
        
        dst = (colored_image[:, :, :3] * 255).astype(np.uint8)
        # dst = np.uint8(cm.jet(dst)*255)

        images_out("huhu", dst)
                # images_log_out(src_path, param, path_dir=path_dir)

        dst = mean_error
        # dst = imgtools.project_data_to_img(img_list_stacked_std)
                # path_dir = str(str_basis_path / "{}-{}".format(exp["name"], idx_exp))
        
        # Get the color map by name:
        cm = plt.get_cmap("jet")
        # Apply the colormap like a function to any array:
        colored_image = cm(dst).reshape((dst.shape[0], dst.shape[1], 4))
        
        dst = (colored_image[:, :, :3] * 255).astype(np.uint8)
        # dst = np.uint8(cm.jet(dst)*255)

        images_out("huhu", dst, name="huhu")
                # images_log_out(src_path, param, path_dir=path_dir)