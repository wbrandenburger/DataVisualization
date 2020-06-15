# ===========================================================================
#   twhlecture.py -----------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox, settingsbox, combobox
from rsvis.tools.topwindow import tw, twhist

from skimage import segmentation, color
from skimage.future import graph

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHLecture(twhist.TWHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHLecture, self).__init__(parent, **kwargs)

        self.reset_dimage()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """
        super(TWHLecture, self).set_canvas(img, **kwargs)

        # set combobox and settingsbox for blurring parameters
        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Median", "Binomial", "Gaussian"]], ["Average"], ["str"]], sbox=[["Kernel Size", "Sigma"], [5, 1.], ["int", "float"]], bbox=[["Blur Image", "Gradient Image"], [self.blur_image, self.gradient_image]])
        self._csbox_blur.grid(row=2, column=0, rowspan=5, sticky=N+W+E)

        # set combobox and settingsbox for segmentation methods
        self._csbox_seg = csbox.CSBox(self, cbox=[["Model"], [[ "SLIC",  "Normalized Cuts", "GrabCut",]], ["SLIC"], ["str"]], bbox=[["Image Segmentation"], [self.image_segmentation]]) # "Felzenswalb"
        self._csbox_seg.grid(row=7, column=0, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut k-means
        self._csbox_slic = csbox.CSBox(self, sbox=[["compactness", "n_segments", "max_iter"], [10, 300, 25], ["float", "int", "int"]])
        self._csbox_slic.grid(row=9, column=0, rowspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for the segmentation method grabcut
        self._csbox_grab = csbox.CSBox(self, sbox=[["iterCount"], [5], ["int"]])
        self._csbox_grab.grid(row=12, column=0, rowspan=1, sticky=N+W+S+E)

        # set combobox and settingsbox for thresholding parameters    
        self._csbox_threshold = scalebox.ScaleBox(self, scbox=[["Thresh"], [[0, 255, 2, 0]], ["int"]],  orient=HORIZONTAL, func=self.set_simple_threshold, button="Simple Thresholding") 
        self._csbox_threshold.grid(row=2, column=1, rowspan=2, sticky=N+W+S+E)

        # set combobox and settingsbox for building difference images
        self._csbox_difference = csbox.CSBox(self, bbox=[["Clear Image List", "Add Image to Image List", "Compute Difference (Image)", "Show Image List"], [self.reset_dimage, self.set_dimage, self.compute_dimage, self.show_dimage]])
        self._csbox_difference.grid(row=4, column=1, rowspan=4, sticky=N+W+S+E)        

        # set combobox and settingsbox for adding images boxes
        self._csbox_boxes = csbox.CSBox(self, bbox=[[ "Show Box"], [self.show_box]])
        self._csbox_boxes.grid(row=8, column=1, rowspan=1, sticky=N+W+S+E)  

        self._button_quit.grid(row=13, column=0, columnspan=3, sticky=N+W+S+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def blur_image(self):
        """Blur the currently displayed image with an average or median filter
        """
        # get settings of combobox and fields 
        param = self._csbox_blur.get_dict()
        kernel_size = (param["Kernel Size"], param["Kernel Size"])

        if (kernel_size[0]%2)==0 or kernel_size[0]>32:
            raise ValueError("Kernel size  must be odd and not larger than 31.")

        # set the border mode used to extrapolate pixels outside of the image, see https://docs.opencv.org/master/d2/de8/group__core__array.html#ga209f2f4869e304c82d07739337eae7c5
        param["BorderType"] = cv2.BORDER_REFLECT
        
        # get the currently displayed image
        img = self.get_obj().get_img(show=True)
        
        # blur the image with selected model
        if param["Model"] == "Average":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#gad533230ebf2d42509547d514f7d3fbc3
            img = cv2.boxFilter(img, -1, kernel_size, normalize=True, borderType=param["BorderType"])
        elif param["Model"] == "Median":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9
            img = cv2.medianBlur(img, kernel_size[0])
        elif param["Model"] == "Binomial":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga27c049795ce870216ddfb366086b5a04
            kernel = self.get_binomial_kernel2d(kernel_size[0])
            img = cv2.filter2D(img, -1, kernel, borderType=param["BorderType"])
        elif param["Model"] == "Gaussian":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
            img = cv2.GaussianBlur(img, kernel_size, param["Sigma"], borderType=param["BorderType"])

        # set image in canvas and update histogram
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def reset_dimage(self, event=None):
        """Reset list of difference images
        """  
        self._dimage = list()   

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_dimage(self, event=None):        
        """Append list of difference images with the currently displayed image
        """
        self._dimage.append(self.get_obj().get_img(show=True))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_dimage(self, event=None):        
        """Show list of difference images in a own topwindow   
        """

        if not len(self._dimage):
            raise IndexError("There are no images available.")

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Difference of images", dtype="img", value=self._dimage)

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

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def compute_dimage(self, event=None):
        """Compute the difference image of the currently images in 'd_image'
        """
        
        # continue if two images are provided
        if len(self._dimage)<2:
            raise IndexError("There are not enough images available to compute the difference.")

        # compute the difference image of the currently images in 'd_image'
        img_a = self._dimage[-1]
        img_b = self._dimage[-2]

        # compute the difference image of the currently images in 'd_image'
        img = np.absolute(imgtools.gray_image(img_a.astype(np.float32))-imgtools.gray_image(img_b.astype(np.float32)))

        #check wheter the image is not empty
        if np.sum(img) == 0:
            raise ValueError("Sum of differences is zero.")

        img = imgtools.project_data_to_img(img)

        # set image in canvas and update histogram
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Difference of images", dtype="img", value=[img, img_a, img_b])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def gradient_image(self):
        """Calculate the horizontal and vertical gradients of the currently displayed image
        """

        # https://www.learnopencv.com/histogram-of-oriented-gradients/
        
        # get settings of combobox and fields 
        param = self._csbox_blur.get_dict()
        kernel_size = param["Kernel Size"]

        if (kernel_size%2)==0 or kernel_size>32:
            raise ValueError("Kernel size  must be odd and not larger than 31.")
        
        # get the currently displayed image
        img = imgtools.project_data_to_img(imgtools.gray_image(self.get_obj().get_img(show=True)))

        # calculate gradient
        gradient_x = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=kernel_size)
        gradient_y = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=kernel_size)
        
        # calculate gradient magnitude and direction (in degrees)
        magnitude, angle = cv2.cartToPolar(gradient_x, gradient_y, angleInDegrees=True)

        # set image in canvas and update histogram
        # self.get_obj().set_img(magnitude, clear_mask=False)
        # self.set_img()

        # open a topwindow with gradient images
        tw.TopWindow(self, title="Gradient Image", dtype="img", value=[img, magnitude, gradient_x, gradient_y])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def image_segmentation(self, **kwargs):
        """Compute low-level segmentation methods like felzenswalb'efficient graph based segmentation or k-means based image segementation

        https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_segmentations.html#sphx-glr-auto-examples-segmentation-plot-segmentations-py
        """
        
        # get settings of combobox and fields 
        param = self._csbox_seg.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img(show=True)

        if param["Model"]=="SLIC" or param["Model"]=="Normalized Cuts":
            # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
            # n_segments = the (approximate) number of labels in the segmented output image.
            # compactness: balances color proximity and space proximity.
            # max_iter: maximum number of iterations of k-means.
            seg_map = segmentation.slic(img, **self._csbox_slic.get_dict(), start_label=1, convert2lab=1)
            seg_map_bound = segmentation.mark_boundaries(img, seg_map)
            seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=0)

            img_list = [seg_map_bound, seg_map_color]

        if param["Model"]=="Normalized Cuts":
            # https://scikit-image.org/docs/stable/api/skimage.future.graph.html#skimage.future.graph.cut_normalized
            # https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_ncut.html
            g = graph.rag_mean_color(img, seg_map, mode='similarity')
            seg_map = graph.cut_normalized(seg_map, g)
            seg_map_bound = segmentation.mark_boundaries(img, seg_map)
            seg_map_color = color.label2rgb(seg_map, img, kind='avg', bg_label=0) 
            img_list.extend([seg_map_bound, seg_map_color])

        elif param["Model"]=="GrabCut":
            # https://docs.opencv.org/master/dd/dfc/tutorial_js_grabcut.html
            
            # get settings of combobox and fields 
            iterCount = self._csbox_grab.get_dict()["iterCount"]

            # get the region of interest
            roi = self.get_obj().get_roi()

            # raise error if the width and height of the roi is not defined
            if not sum(roi[2:4]):
                raise IndexError("There are no images available.")
            
            # allocate mask, background and foreground model
            mask = np.zeros(img.shape[:2],np.uint8)
            bgdModel = np.zeros((1,65),np.float64)
            fgdModel = np.zeros((1,65),np.float64)

            # implement the grabcut algorithm and assign the result of the algorithm to variable img_cut

            # define image list for visualization
            img_list = [img, img_cut, img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2], :]]  

        # open a topwindow with the segmentation results of the currently displayed image      
        tw.TopWindow(self, title="Segmentation", dtype="img", value=img_list)      

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_simple_threshold(self, event=None):
        """Set a threshold via input of windows's slider
        """

        # get settings of combobox and fields 
        param = self._csbox_threshold.get_dict()
        thresh = param["Thresh"]

        # get the currently displayed image
        grayimg = imgtools.gray_image(self._img)

        # implement thresholding and assign the result to the variable dst

        # implement erosion and dilation and assign the result to the variable dst

        # visualize the binary mask in the currently displayed image   
        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_binomial_kernel1d(self, n):
        """Return a 1d binomial filter, which forms a compact rapid approximation of the (discretized) Gaussian.
        """
        return np.expand_dims((np.poly1d([.5,.5])**(n-1)).coeffs, axis=0)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_binomial_kernel2d(self, n):
        """Return a 2d binomial filter, which forms a compact rapid approximation of the (discretized) Gaussian.
        """
        kernel = self.get_binomial_kernel1d(n)
        return np.dot(kernel.T, kernel)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    # kernel = np.convolve(np.poly1d([1,1]), np.poly1d([1,1])) # [1,2,1]
    # kernel = np.convolve(kernel, np.poly1d([1,1])) # [1, 3, 3,1]
    # kernel = np.convolve(kernel, np.poly1d([-1,1])) # [-1, -2, 0, 2, 1]

    # kernel = np.convolve(np.poly1d([1,1]), np.poly1d([-1,1])) # [-1, 0, 1]
    # kernel = np.convolve(kernel, np.poly1d([-1,1])) # [1, -1, -1, 1]
    # kernel = np.convolve(kernel, np.poly1d([-1,1])) # [-1, 2, 0, -2, 1]


