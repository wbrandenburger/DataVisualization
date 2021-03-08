# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer
import rsvis.utils.general as gu

import rsvis.utils.imgseg
import rsvis.utils.imgsegcmp

from rsvis.tools.widgets import csbox, buttonbox, scalebox
from rsvis.tools.topwindow import tw, twhist, twhfilter

from scipy.cluster.vq import vq, kmeans, kmeans2, whiten

from skimage import segmentation, color
from skimage.future import graph
from skimage.measure import label, regionprops, regionprops_table

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

# import rsvis.segmentation.unsegbp
import math

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHSeg(twhfilter.TWHFilter):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHSeg, self).__init__(parent, **kwargs)
        
        self.reset_dimage()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWHSeg, self).set_canvas(img, **kwargs)

        self._csbox_athreshold.grid_forget()
        self._csbox_edges.grid_forget()
        self._csbox_hough.grid_forget()
        self._csbox_difference.grid_forget()

        # set combobox and settingsbox for segmentation methods
        self._csbox_seg = csbox.CSBox(self, cbox=[["mode", "kind", "boundaries", "domain", "reference"], [[ "SLIC", "SLIC-0", "Normalized Cuts", "Felzenswalb", "SLIC+Felzenswalb", "KMeans"], ["avg", "overlay", "min", "max"], ["mark", "find"], ["image", "height", "label"], ["image", "height", "label"]], ["SLIC-0", "avg", "mark", "image", "image"], ["str", "str", "str", "str", "str"]], sbox = [["convert2lab", "color", "position"], [ 1, 1, 0], ["int", "int", "int"]], bbox=[["Image Segmentation", "Distance Transform"], [self.image_segmentation, self.distance_transform]]) 
        self._csbox_seg.grid(row=4, column=1, rowspan=10, sticky=N+W+S+E)

       # set combobox and settingsbox for the segmentation method felzenswalb
        self._csbox_felz = csbox.CSBox(self, sbox=[["scale", "sigma", "min_size"], [32, 0.5, 256], ["int", "float", "int"]], )
        self._csbox_felz.grid(row=14, column=1, rowspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut k-means
        self._csbox_slic = csbox.CSBox(self, sbox=[["compactness", "n_segments", "max_iter"], [10, 250, 15], ["float", "int", "int"]])
        self._csbox_slic.grid(row=17, column=1, rowspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut k-means
        self._csbox_kmeans = csbox.CSBox(self, sbox=[["n_clusters"], [6], ["int"]])
        self._csbox_kmeans.grid(row=20, column=1, rowspan=1, sticky=N+W+S+E)

        # # set combobox and settingsbox for the segmentation method grabcut
        # self._csbox_grab = csbox.CSBox(self, sbox=[["iterCount"], [5], ["int"]],  bbox=[["GrabCut Segmentation"], [self.image_segmentation_grabcut]])
        # self._csbox_grab.grid(row=20, column=1, rowspan=2, sticky=N+W+S+E)

        # # set combobox and settingsbox for the segmentation method grabcut
        # self._csbox_bp = csbox.CSBox(self, sbox=[["dim1", "dim2", "min_label", "max_label", "iterCount", "factor", "net"], [32, 64 , 4, 256, 160, 1.0, 1], ["int", "int", "int", "int", "int", "float", "int"]],  bbox=[["Unsupervised Segmentation via BP"], [self.image_segmentation_backpropagation]])
        # self._csbox_bp.grid(row=21, column=1, rowspan=7, sticky=N+W+S+E)

        self._button_quit.grid(row=27, column=0, columnspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for adding images boxes
        self._csbox_resize = csbox.CSBox(self, sbox=[["factor"], [1.0], ["float"]], bbox=[["Resize Image"], [self.resize_image]])
        self._csbox_resize.grid(row=9, column=0, rowspan=2, sticky=N+W+S+E)  

        # self._csbox_seg_mt = csbox.CSBox(self, sbox=[["factor", "n_filters"], [1.0, 3], ["float", "int"]], bbox=[["MTARSI Segmentation"], [self.mtarsi_segmentation]]) 
        # self._csbox_seg_mt.grid(row=12, column=0, rowspan=3, sticky=N+W+S+E)
        self._csbox_shdw_mt = csbox.CSBox(self, sbox=[["min_size", "n_filters", "quantize"], [50, 3, 16], ["int", "int", "int"]], bbox=[["MTARSI Shadow"], [self.mtarsi_shadow]]) 
        self._csbox_shdw_mt.grid(row=11, column=0, rowspan=4, sticky=N+W+S+E)

        # self._csbox_lthreshold = scalebox.ScaleBox(self, scbox=[["Thresh"], [[0, 100, 1, 0]], ["int"]],  orient=HORIZONTAL, func=self.set_lthreshold)
        # self._csbox_lthreshold.grid(row=16, column=0, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut
        self._csbox_bp = csbox.CSBox(self, sbox=[["dim1", "dim2", "min_label", "max_label", "iterCount", "factor", "height"], [64, 128 , 4, 32, 250, 1.0, 0], ["int", "int", "int", "int", "int", "float", "int", "bool"]],  bbox=[["Unsupervised Segmentation via BP"], [self.image_segmentation_backpropagation]])
        self._csbox_bp.grid(row=21, column=1, rowspan=6, sticky=N+W+S+E)

        self._csbox_blubb = csbox.CSBox(self, bbox=[["Blubb"], [self.blubb]]) 
        self._csbox_blubb.grid(row=15, column=0, rowspan=1, sticky=N+W+S+E)
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_lthreshold(self, event=None):
        """Set a threshold via input of windows's slider and display as a mask
        """
        from skimage import segmentation, color

        # get settings of combobox and fields 
        param = self._csbox_lthreshold.get_dict()
        thresh = param["Thresh"]
        method = cv2.THRESH_BINARY 
        
        img = self.get_obj().get_img(show=True)
        img = color.rgb2lab(img)

        print(np.min(img[:,:,0]), np.max(img[:,:,0]))
        # grayimg = imgtools.gray_image(self.get_obj().get_img(show=True))

        # # set a threshold via input of windows's slider and display as a mask
        # ret, dst = self.set_threshold() 
    
        # # visualize the binary mask in the currently displayed image   
        self.set_threshold_mask(img[:, :, 0]>thresh)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def distance_transform(self, **kwargs):
        img_list, _ = self.image_segmentation(show=False, boundaries="find")
        img_list[2] = imgtools.get_distance_transform(img_list[1], label=1)
        self._img_tw = tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def blubb(self, **kwargs):



        img = self.get_obj().get_img()
        
        param_blur = self._csbox_blur.get_dict()
        img_filtered = cv2.bilateralFilter(img, param_blur["d"], param_blur["sigmaColor"], param_blur["sigmaSpace"])
        
        seg_list_a = list()
        img_list_a = list()
       
        param_model = self._csbox_kmeans.get_dict()   
        
        param_seg = self._csbox_seg.get_dict()
        param_seg["kind"] = "overlay"
        param_seg["mode"] = "KMeans"

        param_seg["color"] = 1
        param_seg["position"] = 0
        
        n_clusters = 3
        for i in range(3):
            param_model["n_clusters"] = n_clusters 
            seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
            seg.predict(img_filtered, **param_model)

            seg_list_a.append(seg.get_seg_map())
            img_list_a.append(seg.get_seg_map_color())      
            n_clusters += 1

        param_seg["position"] = 1
        n_clusters = 3

        seg_list_b = list()
        img_list_b = list()
        n_clusters = 6
        for i in range(3):
            param_model["n_clusters"] = n_clusters 
            seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
            seg.predict(img_filtered, **param_model)

            seg_list_b.append(seg.get_seg_map())
            img_list_b.append(seg.get_seg_map_color())      
            n_clusters += 1

        # param_seg["color"] = 0
        # param_seg["position"] = 1
        # n_clusters = 3

        # seg_list_c = list()
        # img_list_c = list()
        # n_clusters = 4
        # for i in range(3):
        #     param_model["n_clusters"] = n_clusters 
        #     seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
        #     seg.predict(img_filtered, **param_model)

        #     seg_list_c.append(seg.get_seg_map())
        #     img_list_c.append(seg.get_seg_map_color())      
        #     n_clusters += 1

        img_list_a.extend(img_list_b)
        # img_list_a.extend(img_list_c)
        segcmp = rsvis.utils.imgsegcmp.ImgSegCmp()
        segcmp.predict(seg_list_a)
        segcmp.predict(seg_list_b)
        self._img_tw = tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list_a)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_image(self, show=True, **kwargs):
        """Resize image
        """

        # get the currently displayed image
        img = self.get_obj().get_img()  

        param_resize = self._csbox_resize.get_dict()
        img = imgtools.resize_image(img, param_resize["factor"])

        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mtarsi_shadow(self, show=True, **kwargs):
        # get the currently displayed image
        img = self.get_obj().get_img()

        # param_resize = self._csbox_resize.get_dict()
        # img = imgtools.resize_image(img, param_resize["factor"])

        param_blur = self._csbox_blur.get_dict()
        img_filtered = cv2.bilateralFilter(img, param_blur["d"], param_blur["sigmaColor"], param_blur["sigmaSpace"])

        param_seg = self._csbox_seg.get_dict()
        param_seg["mode"] = "SLIC-0"
        param_model = self._csbox_slic.get_dict()
        seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
        seg.predict(img_filtered, **param_model)

        seg_map_color = seg.get_seg_map_color()
        
        
        placeh, placei, placej, placex, grayimg = imgtools.get_placeholder(img, seg_map_color, min_size=self._csbox_shdw_mt.get_dict()["min_size"])

        img_list = [img, seg_map_color, grayimg]
        self._img_tw = tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)

        plt.plot(placex, placeh)
        plt.plot(placex, placei)
        plt.plot(placex, placej)
        # plt.plot(placex, placej)
        plt.ylabel('some numbers')
        plt.show()


        # watershed(-distance, markers, mask=image)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation_backpropagation(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """

        # get settings of combobox and fields 
        param_seg = self._csbox_seg.get_dict()
        param_bp = self._csbox_bp.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img()

        # resize image
        factor = param_bp["factor"]
        new_shape = (math.ceil(img.shape[0]*factor), math.ceil(img.shape[1]*factor))
        img = cv2.resize(img, (new_shape[1], new_shape[0]), dst=cv2.CV_8UC3,interpolation=cv2.INTER_CUBIC)

        mode = param_seg["mode"]
        if mode == "SLIC" or mode=="SLIC-0" or mode=="Normalized Cuts":
            param_model = self._csbox_slic.get_dict()
        elif mode == "Felzenswalb":
            param_model = self._csbox_felz.get_dict()
        elif mode == "KMeans" :
            param_model = self._csbox_kmeans.get_dict()          
 
        seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
        seg.predict(img, **param_model)


        # define image list for visualization
        img_list = [img]

        # height = imgtools.project_data_to_img(self.get_obj().get_img_from_label("height"), dtype= np.uint8, factor=255)

        # define image list for visualization
        img_list.extend([seg.get_seg_map(), seg.get_seg_map_color()])
        rsvis.segmentation.unsegbp.unsegbp(self, img, img_list, self._logger, **param_bp, segments=self._csbox_slic.get_dict()["n_segments"])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mtarsi_segmentation(self, show=True, **kwargs):
        # get the currently displayed image
        img = self.get_obj().get_img()

        param = gu.update_dict(self._csbox_seg_mt.get_dict(), self._csbox_blur.get_dict())

        # define image list for visualization
        img_list = [img]
        cluster_list = list()
         
        new_shape = (math.ceil(img.shape[0]*param["factor"]), math.ceil(img.shape[1]*param["factor"]))
        img = cv2.resize(img, (new_shape[1], new_shape[0]), dst=cv2.CV_8UC3, interpolation=cv2.INTER_CUBIC)
                        
        for i in range(param["n_filters"]):
            img = cv2.bilateralFilter(img, param["Diameter"], param["Sigma Color"], param["Sigma Space"])
        
        img_list.append(img)

        slic = rsvis.utils.imgseg.segmentation_slic(img, **gu.update_dict(self._csbox_slic.get_dict(), {"n_segments":(int(img.shape[0]+img.shape[1])*4)}), **self._csbox_bound.get_dict(), slic_zero=True)
        img_list.append(slic[1])

        cluster = rsvis.utils.imgseg.segmentation_kmeans_color(img, **self._csbox_kmeans.get_dict(), **self._csbox_bound.get_dict())    
        print(np.unique(cluster[0]))
        cluster_list.append(cluster[0])
        img_list.append(imgtools.project_data_to_img(cluster[0],dtype=np.uint8, factor=255))
        
        param_cluster = self._csbox_kmeans.get_dict()
        param_cluster["non_pos"] = 1
        cluster = rsvis.utils.imgseg.segmentation_kmeans_color_pos(img, **param_cluster, **self._csbox_bound.get_dict())    
        print(np.unique(cluster[0]))
        cluster_list.append(cluster[0])
        img_list.append(imgtools.project_data_to_img(cluster[0],dtype=np.uint8, factor=255))   

        param_cluster["non_pos"] = 0
        cluster = rsvis.utils.imgseg.segmentation_kmeans_color_pos(img, **param_cluster, **self._csbox_bound.get_dict())    
        print(np.unique(cluster[0]))
        cluster_list.append(cluster[0])
        img_list.append(imgtools.project_data_to_img(cluster[0],dtype=np.uint8, factor=255))         

        n_clusters = param_cluster["n_clusters"]

        img_new = np.zeros(img.shape[:2], dtype=np.uint8)

        clstr_img_src = cluster_list[0]
        clstr_img_dst = cluster_list[1]
        clstr_img_est = cluster_list[2]

        clstr_cmp_src_dst = np.zeros((n_clusters, 2))
        for clstr in range(n_clusters):
            # clstr_cmp = clstr_img_dst[clstr_img_src==clstr]
            # print(clstr_cmp.shape, np.unique(clstr_cmp))

            # print(clstr_img_src.shape,np.unique(clstr_img_src))
            # print(clstr_img_dst.shape,np.unique(clstr_img_dst))

            # print(clstr)
            clstr_src_dst = clstr_img_dst[(clstr_img_src==clstr).astype(np.bool)]
            # bbbb = np.where(clstr_img_src==clstr, clstr_img_dst, -1).astype(np.int8)

            # clstr_hist = np.histogram(bbbb, bins=range(0,n_clusters+1))
            # clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
            # print(clstr_hist_norm)
            clstr_hist = np.histogram(clstr_src_dst, bins=range(0,n_clusters+1))
            clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
            print(clstr_hist_norm)
            hist_max = np.amax(clstr_hist_norm)
            print(hist_max)
            hist_max_idx = int(np.where(clstr_hist_norm==hist_max)[0])
            print("Max: {}, Idx-Max: {}, Stats: {}".format(hist_max, hist_max_idx, np.std(clstr_hist_norm)))
            clstr_cmp_src_dst = hist_max_idx 

            cc = False
            if np.std(clstr_hist_norm) > 0.3:
                cc = True

            clstr_dst_src = clstr_img_src[clstr_img_dst==hist_max_idx]
            # bbbb = np.where(clstr_img_dst==hist_max_idx, clstr_img_src, -1).astype(np.int8)

            # clstr_hist = np.histogram(bbbb, bins=range(0,n_clusters+1))
            # clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
            # print(clstr_hist_norm)
            clstr_hist = np.histogram(clstr_dst_src, bins=range(0,n_clusters+1))
            clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
            print(clstr_hist_norm)
            hist_max = np.amax(clstr_hist_norm)
            print(hist_max)            
            hist_max_idx = int(np.where(clstr_hist_norm==hist_max)[0])
            print("Max: {}, Idx-Max: {}, Stats: {}".format(hist_max, hist_max_idx, np.std(clstr_hist_norm)))
            if clstr == hist_max_idx and cc:
                print("oberblubber")
                clstr_src_dst = clstr_img_est[(clstr_img_src==clstr).astype(np.bool)]
                clstr_hist = np.histogram(clstr_src_dst, bins=range(0,n_clusters+1))
                clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
                # print(clstr_hist_norm)
                hist_max = np.amax(clstr_hist_norm)
                # print(hist_max)
                hist_max_idx = int(np.where(clstr_hist_norm==hist_max)[0])
                # print("Max: {}, Idx-Max: {}, Stats: {}".format(hist_max, hist_max_idx, np.std(clstr_hist_norm)))
                clstr_cmp_src_est = hist_max_idx

                cc = False
                if np.std(clstr_hist_norm) > 0.3:
                    cc = True


                clstr_dst_src = clstr_img_src[clstr_img_est==hist_max_idx]
                clstr_hist = np.histogram(clstr_dst_src, bins=range(0,n_clusters+1))
                clstr_hist_norm = clstr_hist[0]/np.sum(clstr_hist[0])
                # print(clstr_hist_norm)
                hist_max = np.amax(clstr_hist_norm)
                # print(hist_max)            
                hist_max_idx = int(np.where(clstr_hist_norm==hist_max)[0]) 
                
                if clstr == hist_max_idx and cc:         
                    print("blubber")
                    img_new += np.where(clstr_img_src==clstr,1,0).astype(np.uint8)

        print(clstr_cmp_src_dst)

        img_list.append(img_new)


        # # # # seg_map_slic, seg_map_color_slic, seg_map_bound_slic = rsvis.utils.imgseg.segmentation_slic(img, **gu.update_dict(self._csbox_slic.get_dict(), {"n_segments":(int(img.shape[0]+img.shape[1])/2)}), **self._csbox_bound.get_dict(), slic_zero=True)

        # # # # seg_map_kmeans, seg_map_bound_kmeans = rsvis.utils.imgseg.segmentation_kmeans_color(img, **self._csbox_kmeans.get_dict(), **self._csbox_bound.get_dict())      

        # # # # # define image list for visualization
        # # # # img_list.extend([seg_map_bound_kmeans, seg_map_bound_slic])
        # # # # seg_map_bound_kmeans = imgtools.project_data_to_img(seg_map_bound_kmeans,dtype=np.uint8, factor=255)
        # # # # seg_map_kmeans = seg_map_kmeans.astype(np.uint8)
        # # # # num = np.unique(seg_map_kmeans)
        # # # # seg_map_kmeans_new= np.zeros(seg_map_kmeans.shape, dtype=np.uint8)
        # # # # for i in np.unique(seg_map_slic):
        # # # #     mask = np.where(seg_map_slic==i, 1, 0).astype(np.ubyte)
        # # # #     hist = cv2.calcHist([seg_map_kmeans], [0], mask, [len(num)], [0,len(num)])
        # # # #     hist_max_index = np.where(hist == np.amax(hist))
        # # # #     if len(hist_max_index[0]) > 1:
        # # # #         hist_max_index = hist_max_index[0]
        # # # #     seg_map_kmeans_new += mask.astype(np.uint8)[:,:,np.newaxis]*np.uint8(hist_max_index[0])
        # # # # seg_map_kmeans_new_map = imgtools.project_data_to_img(seg_map_kmeans_new, factor=255, dtype=np.uint8)
        # # # # img_list.extend([seg_map_kmeans_new_map])

        # # # # hist = cv2.calcHist([seg_map_kmeans_new], [0], None, [len(num)], [0,len(num)])
        # # # # hist_max_count = np.where(hist == np.amax(hist))
        # # # # hist_list=[hist_max_count[0]]
        # # # # for i in num:
        # # # #     hist[i] = np.mean(img[np.concatenate([seg_map_kmeans_new]*3, axis=2)==i])
        # # # # hist_min_bright = np.where(hist == np.amin(hist)) 
        # # # # hist_list.append(hist_min_bright[0])
        # # # # print(hist_list)
        # # # # aba = [i for i in num if i not in hist_list]
        # # # # # allocate mask, background and foreground model
        # # # # seg_map_kmeans_new = seg_map_kmeans_new.astype(np.uint8)
        # # # # mask = np.zeros(img.shape[:2],dtype=np.uint8)
        # # # # mask += np.uint8(2)*np.where(np.squeeze(seg_map_kmeans_new, axis=2)==np.uint8(hist_max_count),1,0).astype(np.uint8)
        # # # # mask += np.uint8(3)*np.where(np.squeeze(seg_map_kmeans_new, axis=2)==np.uint8(hist_min_bright[0]),1,0).astype(np.uint8)
        # # # # mask += np.uint8(3)*np.where(np.squeeze(seg_map_kmeans_new, axis=2)==np.uint8(aba[0]),1,0).astype(np.uint8)
        # # # # bgdModel = np.zeros((1,65),np.float64)
        # # # # fgdModel = np.zeros((1,65),np.float64)
        # # # # w,h,d = img.shape
        # # # # roi = (0,0,w,h)
        # # # # # this modifies mask 

        # # # # seg_map_slic, seg_map_color_slic, seg_map_bound_slic = rsvis.utils.imgseg.segmentation_slic(img, **gu.update_dict(self._csbox_slic.get_dict(), {"n_segments":(int(img.shape[0]+img.shape[1])*4)}), **self._csbox_bound.get_dict(), slic_zero=True)   

        # # # # img_list.extend([imgtools.project_data_to_img(mask,factor=255, dtype=np.uint8)])
        # # # # # cv2.grabCut(cv2.bilateralFilter(img, d=5, sigmaColor=100, sigmaSpace=500), mask, roi, bgdModel, fgdModel, 10, mode=cv2.GC_INIT_WITH_MASK)

        # # # # cv2.grabCut(img, mask, roi, bgdModel, fgdModel, 40, mode=cv2.GC_INIT_WITH_MASK)

        # # # # # If mask==2 or mask== 1, mask2 get 0, other wise it gets 1 as 'uint8' type.
        # # # # seg_map = np.where((mask==2)|(mask==0), 0, 1).astype('bool')
        # # # # seg_map = img*seg_map[:,:,np.newaxis]
        # # # # img_list.extend([seg_map])
        # # # # seg_map = np.where((mask==2)|(mask==0), 1, 0).astype('bool')
        # # # # seg_map = img*seg_map[:,:,np.newaxis]
        # # # # img_list.extend([seg_map])


        # open a topwindow with the segmentation results of the currently displayed image
        if show:
            self._img_tw = tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation(self, show=True, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        # get settings of combobox and fields 
        param_seg = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = imgtools.project_and_stack(self.get_obj().get_img_from_label(param_seg["domain"], dtype=np.uint8, factor=255))
        # img = self.get_obj().get_img_from_label("height")
        # param_seg["reference"] = self.get_obj().get_img_from_label("height")
        param_seg["boundaries"] = "find"
        # define image list for visualization
        img_list = [img]
        
        mode = param_seg["mode"]
        if mode == "SLIC" or mode=="SLIC-0" or mode=="Normalized Cuts":
            param_model = self._csbox_slic.get_dict()
        elif mode == "Felzenswalb":
            param_model = self._csbox_felz.get_dict()
        elif mode == "KMeans" :
            param_model = self._csbox_kmeans.get_dict()          
 
        seg = rsvis.utils.imgseg.ImgSeg(**param_seg)
        seg.predict(img, **param_model)
        img_list.extend([seg.get_seg_map_color(), seg.get_seg_map_boundaries(img=imgtools.project_and_stack(self.get_obj().get_img_from_label(param_seg["reference"]),  dtype=np.uint8, factor=255))])    
        
        print("Number of segments: {}".format(seg.get_num_label()))

        # open a topwindow with the segmentation results of the currently displayed image

        if show:
            self.get_obj().set_img(img_list[2], clear_mask=False)
            self.set_img()

            self._img_tw = tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)
        return img_list

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation_grabcut(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb' efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        # get settings of combobox and fields 
        param = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img()

        # define image list for visualization
        img_list = [img]

        # https://docs.opencv.org/master/dd/dfc/tutorial_js_grabcut.html
        
        # get the region of interest
        roi = self.get_obj().get_roi()

        # raise error if the width and height of the roi is not defined
        if not sum(roi[2:4]):
            raise IndexError("There are no images available.")
        
        # allocate mask, background and foreground model
        mask = np.zeros(img.shape[:2],np.uint8)
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)

        # this modifies mask 
        cv2.grabCut(img, mask, roi, bgdModel, fgdModel, **self._csbox_grab.get_dict(), mode=cv2.GC_INIT_WITH_RECT)

        # If mask==2 or mask== 1, mask2 get 0, other wise it gets 1 as 'uint8' type.
        seg_map = np.where((mask==2)|(mask==0), 0, 1).astype('bool')
        img_cut = img*seg_map[:,:,np.newaxis]
        
        # define image list for visualization
        img_list = [img, img_cut, img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2], :]]  

        # open a topwindow with the segmentation results of the currently displayed image      
        tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_box(self, event=None):        
        """Show list of boxes 
        """

        # get the region of interest
        roi = self.get_obj().get_roi()

        # raise error if the width and height of the roi is not defined
        if not sum(roi[2:4]):
            raise IndexError("There are no images available.")
        
        # get the currently displayed image
        img = self.get_obj().get_img(show=True)

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Boxes", dtype="img", value=[img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2], :]])

    # #   CENTROIDS -----------------------------------------------------------
    # # -----------------------------------------------------------------------

        # # set combobox and settingsbox for kmeans
        # self._csbox_centroids = csbox.CSBox(self, bbox=[["Reset Centroids", "Set Centroids", "Compute Centroids (Color)", "Compute Centroids (Color+Space)"], [self.reset_centroids, self.set_centroids, self.get_centroids_color, self.get_centroids_color_space]], sbox=[["Centroids"], [3], ["int"]])
        # self._csbox_centroids.grid(row=4, column=1, rowspan=5, sticky=W+E)


    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_cmap(self, n, name='hsv'):
    #     '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    #     RGB color; the keyword argument name must be a standard mpl colormap name.'''
    #     cmap = plt.cm.get_cmap(name, n)
    #     cmap = [list(cmap(c)[0:3]) for c in range(0, n)]

    #     return cmap

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids_color(self, event=None):
    #     img = self.get_obj().get_img(show=True).astype(np.float)
    #     self._centroids_img_shape = (img.shape[0], img.shape[1]) 

    #     data = whiten(img.reshape((-1,3)))
    #     self.get_centroids(data)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids_color_space(self, event=None):
    #     img = self.get_obj().get_img(show=True).astype(np.float)
    #     self._centroids_img_shape = (img.shape[0], img.shape[1]) 

    #     grid = np.indices((self._centroids_img_shape), dtype=np.float)
    #     data = whiten(np.stack([img[...,0], img[...,1], img[...,2], grid[0], grid[1]], axis=2).reshape((-1,5)))
    #     self.get_centroids(data)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_centroids(self, data, event=None):     
    #     if not self._centroids:
    #         number = self._csbox_centroids.get_dict()["Centroids"]
    #         codes = number
    #         minit = "++"
    #     else:
    #         number = len(self._centroids)
    #         codes = np.stack(self._centroids, axis=0).astype(np.float)
    #         minit = "matrix"

    #     centroids, label = kmeans2(data, codes, minit=minit)
    #     label = label.reshape(self._centroids_img_shape)

    #     mask_list = [np.where(label==idx, 1, 0).astype(np.uint8) for idx in range(len(centroids))]
    #     mask_color = np.random.randint(0, 255, number*3, dtype=np.uint8).reshape((number,3)).tolist()
    #     mask_alpha = [150]*number
    #     mask_invert = [False]*number

    #     self.get_obj().set_mask(mask=mask_list, color=mask_color
    #     , invert=mask_invert, alpha=mask_alpha, show=True)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def reset_centroids(self, event=None): 
    #     self._centroids = list()   

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def set_centroids(self, event=None):
    #     self._centroids.append(self.get_obj()._data_img[self.get_obj()._mouse_img[0], self.get_obj()._mouse_img[1], :])