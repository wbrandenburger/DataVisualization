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

from scipy import ndimage as ndi
import matplotlib.pyplot as plt

from skimage.morphology import disk
from skimage.segmentation import watershed
from skimage import data
from skimage.filters import rank
from skimage.util import img_as_ubyte

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
    images_outs = rsio.get_img_out(img_name="gradient")
    images_log_out = rsio.get_param_out(**param_out["log"])
    # images_outs = rsio.get_img_out(img_name="attempt")
    # images_out = gu.PathCreator(**self._param_out)

    bbb = pathlib.Path(param_out["image"]["path_dir"])
    for i in images_in:    
        for j in param_exp:
            img_list = list()
            img_lists = list()
            for k in range(j["iter"]):
                
                blubb = dict()
                for e, f in j["param"].items():
                     blubb[e] = f[k]
         
                new_shape = (math.ceil(i[0].data.shape[0]*blubb["factor"]), math.ceil(i[0].data.shape[1]*blubb["factor"]))
                img = cv2.resize(i[0].data, (new_shape[1], new_shape[0]), dst=cv2.CV_8UC3, interpolation=cv2.INTER_CUBIC)
                
                # # Thresholding
                # img = cv2.bilateralFilter(img, blubb["filter"][0], blubb["filter"][1], blubb["filter"][2])
                # grayimg = imgtools.gray_image(img)
                # _ , dst = cv2.threshold(grayimg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # GRADIENTS
                grayimg = imgtools.gray_image(img)
                gradient_x = cv2.Sobel(grayimg, cv2.CV_32F, 1, 0, ksize=blubb["ksize"])
                gradient_y = cv2.Sobel(grayimg, cv2.CV_32F, 0, 1, ksize=blubb["ksize"])
                
                # calculate gradient magnitude and direction (in degrees)
                dst, angle = cv2.cartToPolar(gradient_x, gradient_y, angleInDegrees=True)

                dst = imgtools.project_data_to_img(dst)*(-1.0)+1.0
                dst = np.where(dst>0., dst, np.min(dst[dst>0.]))
                dst = imgtools.project_data_to_img(np.log(dst))*(-1.0)+1.0
                dst = np.stack([dst, dst, dst], axis= 2)
                img_lists.append(dst) 
                _, _, dst = rsvis.utils.imgseg.segmentation_slic(dst, n_segments=blubb["slic-0"], slic_zero=True) #,boundaries="find")

                # _, _, dst = rsvis.utils.imgseg.segmentation_norm(dst, n_segments=blubb["slic-0"], slic_zero=True) #,boundaries="find")


                # # denoise image
                # # img = imgtools.gray_image(img)
                # # denoised = rank.median(img, disk(2))
                # denoised = imgtools.project_data_to_img(dst, dtype=np.uint8, factor=255) 
                # # find continuous region (low gradient -
                # # where less than 10 for this image) --> markers
                # # disk(5) is used here to get a more smooth image
                # markers = rank.gradient(denoised, disk(5)) < 16
                # markers = ndi.label(markers)[0]

                # # local gradient (disk(2) is used to keep edges thin)
                # gradient = rank.gradient(denoised, disk(2))

                # # process the watershed
                # dst = watershed(gradient, markers)
                # dst = imgtools.project_data_to_img(dst, dtype=np.uint8, factor=255)

                img_list.append(dst) 
                path_dir = str(bbb / "{}-{}".format(j["name"], k))
                images_out(i[0].path, img_list[-1], path_dir=path_dir)
                images_outs(i[0].path, img_lists[-1], path_dir=path_dir)
                images_log_out(i[0].path, blubb, path_dir=path_dir)