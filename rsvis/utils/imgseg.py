# ===========================================================================
#   segmentation.py ---------------------------------------------------------
# ===========================================================================

import rsvis.utils.imgtools as imgtools

import cv2

import numpy as np

from skimage import segmentation, color
from skimage.future import graph
from skimage.measure import label

from sklearn.utils import shuffle
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from sklearn import preprocessing

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgSeg:
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
        self._mode = param["mode"] if "mode" in param.keys() else "SLIC-0"
        self._kind = param["kind"] if "kind" in param.keys() else "avg"
        self._boundaries = param["boundaries"] if "boundaries" in param.keys() else "mark"
        self._convert2lab = param["convert2lab"] if "convert2lab" in param.keys() else True
        self._color = param["color"] if "color" in param.keys() else True
        self._position = param["position"] if "position" in param.keys() else False

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def predict(self, img, **kwargs):
        self._img = img

        if self._mode == "SLIC":
            self.segmentation_slic(**kwargs)
        elif self._mode == "SLIC-0":
            self.segmentation_slic_zero(**kwargs)
        elif self._mode == "Felzenswalb":
            self.segmentation_felzenswalb(**kwargs)
        elif self._mode == "Normalized Cuts":
            self.segmentation_normalized_cuts(**kwargs)
        elif self._mode == "KMeans":
            self.segmentation_kmeans(**kwargs)                       

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_data_from_img(self):
        w, h, d = original_shape = tuple(self._img.shape)

        factor = 1.0
        if self._img.dtype == np.uint8:
            factor = 255

        img = self._img.copy()
        if not self._color:
            img = np.expand_dims(imgtools.gray_image(img), axis=2)  
            d -= 2
            self._convert2lab = False
            
        if self._convert2lab == True:
            img = color.rgb2lab(img)

        if self._position:
            img = self.add_position_array(img)
            d += 2

        return np.reshape(np.array(img, dtype=np.float64) / factor, (w * h, d))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_position_array(self, img):
        w, h, _ = original_shape = tuple(self._img.shape)

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

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------  
    def get_seg_map_color(self):
        if self._kind=="avg" or self._kind=="overlay":
            seg_map_color = color.label2rgb(self._seg_map, self._img, kind=self._kind, bg_label=-1)
        elif self._kind == "min" or self._kind == "max":
            factor = -1.0 if self._kind == "min" else 1.0
            seg_map_color = np.zeros(self._img.shape, dtype=np.uint8)
            for label in self.get_label():
                values = self._img[self._seg_map==label]
                
                value = np.mean(values, axis=0) + factor*np.std(values, axis=0)
                value = np.where(value<0, 0, value)
                value = np.where(value>255, 255, value)

                seg_map_color[self._seg_map==label] = value

                # seg_map_color[self._seg_map==label] = np.std(values, axis=0)
                # seg_map_color = imgtools.project_data_to_img(seg_map_color, dtype=np.uint8, factor=255)
        return seg_map_color
                # print(np.mean(values, axis=0))
                # print(np.std(values, axis=0))


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_seg_map_boundaries(self, img=None):
        # colored boundaries
        # seg_map_bin = segmentation.find_boundaries(self._seg_map, mode="subpixel")
        # return cv2.resize(self._img, (seg_map_bin.shape[1],seg_map_bin.shape[0]))*seg_map_bin[:,:,np.newaxis]

        if not isinstance(img, np.ndarray):
            img = self._img
        
        # img = imgtools.stack_image_dim(img)

        seg_map_bin = segmentation.find_boundaries(self._seg_map, mode="inner")
        img =cv2.resize(img, (seg_map_bin.shape[1],seg_map_bin.shape[0]))
        img_y = np.stack([np.zeros(seg_map_bin.shape, dtype=np.uint8),np.full(seg_map_bin.shape, 255, dtype=np.uint8), np.zeros(seg_map_bin.shape, dtype=np.uint8)], axis=2)
        return (img+1)*np.invert(seg_map_bin)[:,:,np.newaxis] + img_y
        # if self._boundaries=="mark":
        #     return segmentation.mark_boundaries(self._img, self._seg_map, mode="subpixel")
        # elif self._boundaries=="find":
        #     return segmentation.find_boundaries(self._seg_map, mode="subpixel")

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_visualization(self):
        img_list = [self.get_seg_map_color()]
        if self._mode != "KMeans":
            img_list.append(self.get_seg_map_boundaries())
        return img_list

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def segmentation_kmeans(self, **kwargs):
        """ 
            https://towardsdatascience.com/introduction-to-image-segmentation-with-k-means-clustering-83fd0a9e2fc3
            https://towardsdatascience.com/k-means-clustering-with-scikit-learn-6b47a369a83c
        """
        data = scale(self.get_data_from_img())
        km = KMeans(**kwargs, init="random").fit(data)
        pred = km.predict(data)
        
        self._seg_map = self.get_seg_map_from_data(pred)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def segmentation_slic(self, **kwargs):
        """ 
            n_segments = the (approximate) number of labels in the segmented output image.
            compactness: balances color proximity and space proximity.
            max_iter: maximum number of iterations of k-means.
            https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
        """
        self._seg_map = segmentation.slic(self._img, **kwargs, start_label=1)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def segmentation_slic_zero(self, **kwargs):
        """ https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
        """
        self.segmentation_slic(slic_zero=True, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def segmentation_felzenswalb(self, **kwargs):
        """ https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.felzenszwalb.
        """
        self._seg_map = segmentation.felzenszwalb(self._img, **kwargs)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def segmentation_normalized_cuts(self, **kwargs):
        """ https://scikit-image.org/docs/stable/api/skimage.future.graph.html#skimage.future.graph.cut_normalized
            https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_ncut.html
        """ 
        self.segmentation_slic_zero(**kwargs)
        slic_graph = graph.rag_mean_color(self._img, self._seg_map, mode='similarity') # parameter?
        self._seg_map = graph.cut_normalized(self._seg_map, slic_graph)

# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segmentation_felzenswalb(img, boundaries="mark", **kwargs):
# # #     # param_str = "felz-{}".format("-".join([str(e) for e in **kwargs]))
# # #     seg_map = segmentation.felzenszwalb(img, **kwargs)
# # #     seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=-1)
# # #     seg_map_color_bound = segementation_get_boundaries(seg_map_color, seg_map, boundaries=boundaries)
    
# # #     # define image list for visualization
# # #     return seg_map, seg_map_color, seg_map_color_bound

# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segmentation_slic(img, boundaries="mark", **kwargs):
# # #     seg_map = segmentation.slic(img, **kwargs, start_label=1)
# # #     seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=-1)
# # #     seg_map_color_bound = segementation_get_boundaries(seg_map_color, seg_map, boundaries=boundaries)
    
# # #     # define image list for visualization
# # #     return seg_map, seg_map_color, seg_map_color_bound

# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segmentation_norm(img, boundaries="mark", **kwargs):
# # #     seg_map = segmentation.slic(img, **kwargs, start_label=1)
# # #     g = graph.rag_mean_color(img, seg_map, mode='similarity')
# # #     seg_map = graph.cut_normalized(seg_map, g)
# # #     seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=-1)
# # #     seg_map_color_bound = segementation_get_boundaries(seg_map_color, seg_map, boundaries=boundaries)
    
# # #     # define image list for visualization
# # #     return seg_map, seg_map_color, seg_map_color_bound

# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segmentation_kmeans_color(img, boundaries="mark", non_pos=True, lab=True, **kwargs):
# # #     """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation    

# # #     https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
# # #     """    
# # #     # https://towardsdatascience.com/introduction-to-image-segmentation-with-k-means-clustering-83fd0a9e2fc3
# # #     # https://towardsdatascience.com/k-means-clustering-with-scikit-learn-6b47a369a83c
# # #     if lab:
# # #         data_img = color.rgb2lab(img.copy())

# # #     w, h, d = original_shape = tuple(data_img.shape)

# # #     image_array = np.reshape(np.array(data_img, dtype=np.float64) / 255, (w * h, d))

# # #     # Fitting model on a small sub-sample of the data"
# # #     # image_array_sample = shuffle(image_array, random_state=0)[:1000]
# # #     km = KMeans(**kwargs, init="random").fit(image_array)
# # #     pred = km.predict(image_array)
# # #     seg_map = np.squeeze(np.reshape(pred, (w, h, 1)).astype(np.int32))
# # #     seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=-1)
# # #     # seg_map_color = color.lab2rgb(np.reshape(km.cluster_centers_[km.labels_], (w, h, d)))
 
# # #     # print(seg_map.dtype)
# # #     # print(seg_map_color.dtype)

# # #     return seg_map, seg_map_color

# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segmentation_kmeans_color_pos(img, boundaries="mark", non_pos=True, lab=True, **kwargs):
# # #     """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation    

# # #     https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
# # #     """    
# # #     # https://towardsdatascience.com/introduction-to-image-segmentation-with-k-means-clustering-83fd0a9e2fc3
# # #     # https://towardsdatascience.com/k-means-clustering-with-scikit-learn-6b47a369a83c
    
# # #     if non_pos:
# # #         if lab:
# # #             data_img = color.rgb2lab(img.copy())
# # #     else:
# # #         data_img = imgtools.gray_image(img)
# # #         data_img = np.expand_dims(data_img, axis=2)
        
# # #     w, h, d = original_shape = tuple(data_img.shape)
    
# # #     x = np.linspace(0, 1, h)
# # #     y = np.linspace(0, 1, w)
# # #     xv, yv = np.meshgrid(x,y)
# # #     xv = np.expand_dims(xv, axis=2)
# # #     yv = np.expand_dims(yv, axis=2)

# # #     img_data = np.array(data_img, dtype=np.float64) / 255
# # #     data = np.concatenate((img_data, xv, yv), axis=2)
# # #     data_array = np.reshape(data, (w * h, d + 2))
# # #     # Fitting model on a small sub-sample of the data"
# # #     # image_array_sample = shuffle(image_array, random_state=0)[:1000]
# # #     data_array_scaled = preprocessing.scale(data_array)
# # #     km = KMeans(**kwargs, init="random").fit(data_array_scaled)
# # #     pred = km.predict(data_array_scaled)
# # #     seg_map = np.squeeze(np.reshape(pred, (w, h, 1)).astype(np.int32))
# # #     seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=-1)
# # #     # seg_map_color = np.reshape(km.cluster_centers_[:,:d][km.labels_], (w, h, d))
    
# # #     # print(seg_map.dtype)
# # #     # print(seg_map_color.dtype)

# # #     return seg_map, seg_map_color


# # # #   function ----------------------------------------------------------------
# # # # ---------------------------------------------------------------------------
# # # def segementation_get_boundaries(img, seg_map, boundaries="mark", **kwargs):
# # #     if boundaries == "mark":
# # #         seg_map_bound = segmentation.mark_boundaries(img, seg_map, mode="subpixel")
# # #     elif boundaries == "find":
# # #         seg_map_bound = segmentation.find_boundaries(seg_map, mode="subpixel")
    
# # #     return seg_map_bound