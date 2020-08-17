# ===========================================================================
#   segmentation.py ---------------------------------------------------------
# ===========================================================================

import rsvis.utils.imgtools as imgtools

import numpy as np

from skimage import segmentation, color
from skimage.future import graph
from skimage.measure import label

from sklearn.utils import shuffle
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn import preprocessing

from scipy.stats import wasserstein_distance


import cv2
import matplotlib.pyplot as pl

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgSegCmp:
    """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

    https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
    """

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, **kwargs):
        self.set_param(**kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_param(self, **param):
        self._mode = param["mode"] if "mode" in param.keys() else "KMeans"
        self._kind = param["kind"] if "kind" in param.keys() else "avg"
        self._boundaries = param["boundaries"] if "boundaries" in param.keys() else "mark"
        self._convert2lab = param["convert2lab"] if "convert2lab" in param.keys() else True
        self._color = param["color"] if "color" in param.keys() else True
        self._position = param["position"] if "position" in param.keys() else False

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def predict(self, seg_list, **kwargs):        
        # from sklearn.cross_decomposition import CCA
        # X = [[0., 0., 1.], [1.,0.,0.], [2.,2.,2.], [3.,5.,4.]]
        # Y = [[0.1], [0.9], [6.2], [11.9]]
        # cca = CCA(n_components=1)
        # cca.fit(X, Y)
        # X_c, Y_c = cca.transform(X, Y)
        # print(X_c, Y_c)


        for idx in range(len(seg_list)-1):
            seg_a = seg_list[idx]
            seg_b = seg_list[idx+1]
            w, h = original_shape = tuple(seg_a.shape)
            seg_a = np.reshape(np.array(seg_a, dtype=np.float32)/np.max(seg_a), (w * h))
            seg_b = np.reshape(np.array(seg_b, dtype=np.float32)/np.max(seg_b), (w * h))

            # seg_as = seg_list[idx]
            # seg_bs = seg_list[idx+1]
            # seg_a = self.add_position_array(imgtools.expand_image_dim(seg_as))
            # seg_b = self.add_position_array(imgtools.expand_image_dim(seg_bs))
            # w, h, _ = original_shape = tuple(seg_a.shape)

            # seg_a = np.reshape(np.array(seg_a, dtype=np.float32), (w * h, 3))
            # seg_b = np.reshape(np.array(seg_b, dtype=np.float32), (w * h, 3))
            # # print(seg_a.shape)
            # seg_a = scale(seg_a)         
            # seg_b = scale(seg_b)    

            # seg_a = np.squeeze(np.reshape(np.array(seg_a, dtype=np.float32), (w * h * 3)))
            # seg_b = np.squeeze(np.reshape(np.array(seg_b, dtype=np.float32), (w * h * 3)))

            # print("A->B:{}".format(cv2.EMD(seg_a, seg_b, cv2.DIST_L2)))
            print("A->B:{}".format(wasserstein_distance(seg_a, seg_b)))
            for a_idx in np.unique(seg_a):
                seg_a_label = seg_a == a_idx
                # seg_a_label = self.add_position_array(imgtools.expand_image_dim(seg_as == a_idx))
                # seg_a_label = np.reshape(np.array(seg_a_label, dtype=np.float32), (w * h , 3))

                # seg_a_label = scale(seg_a_label)         
                # seg_a_label = np.squeeze(np.reshape(np.array(seg_a_label, dtype=np.float32), (w * h * 3)))
                for b_idx in np.unique(seg_b):
                    seg_b_label = seg_b == b_idx
                        # seg_b_label = self.add_position_array(imgtools.expand_image_dim(seg_bs == b_idx))
                        # seg_b_label = np.reshape(np.array(seg_b_label, dtype=np.float32), (w * h , 3))

                        # seg_b_label = scale(seg_b_label)
                        # seg_b_label = np.squeeze(np.reshape(np.array(seg_b_label,   dtype=np.float32), (w * h * 3)))
                    # print("A({})->B({}):{}".format(seg_a_label, seg_b_label, cv2.EMD(seg_a_label, seg_b_label)))
                    print("A({})->B({}):{}".format(a_idx, b_idx, wasserstein_distance(seg_a_label, seg_b_label)))


    # https://pythonot.github.io/ !!!
    # https://stats.stackexchange.com/questions/404775/calculate-earth-movers-distance-for-two-grayscale-images             
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html
    # https://github.com/wmayner/pyemd
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_data_from_img(self):
        w, h, d = original_shape = tuple(self._img.shape)

        factor = 1.0
        if self._img.dtype == np.uint8:
            factor = 255

        img = self._img.copy()
        if self._convert2lab == True:
            img = color.rgb2lab(img)
        elif not self._color:
            img = np.expand_dims(imgtools.gray_image(img), axis=2)  
            d -= 2     

        if self._position:
            img = self.add_position_array(img)
            d += 2

        return np.reshape(np.array(img, dtype=np.float64) / factor, (w * h, d))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_position_array(self, img):
        w, h, _ = original_shape = tuple(img.shape)

        x = np.linspace(0, 1, h)
        y = np.linspace(0, 1, w)
        xv, yv = np.meshgrid(x,y)
        xv = np.expand_dims(xv, axis=2)
        yv = np.expand_dims(yv, axis=2)
        
        return np.concatenate((img, xv, yv), axis=2)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_seg_map_from_data(self, pred):
        w, h, _ = original_shape = tuple(self._img.shape)

        return np.squeeze(np.reshape(pred, (w, h, 1)).astype(np.int32))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_seg_map(self):
        return self._seg_map
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_num_label(self):
        return len(self.get_label())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_label(self):
        return np.unique(self._seg_map)

