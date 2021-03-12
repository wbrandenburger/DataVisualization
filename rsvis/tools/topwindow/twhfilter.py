# ===========================================================================
#   twhfilter.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.height import Height
from rsvis.utils import imgtools
import rsvis.utils.imgcontainer

from rsvis.tools.widgets import csbox, buttonbox, scalebox
from rsvis.tools.topwindow import tw, twhist

import cv2
import numpy as np
from tkinter import *
from tkinter import ttk

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class TWHFilter(twhist.TWHist):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            parent,
            **kwargs
        ):

        #   settings --------------------------------------------------------
        super(TWHFilter, self).__init__(parent, **kwargs)
        
        self.reset_dimage()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_canvas(self, img, **kwargs):
        """Set the main image canvas with the image to be displayed and the corresponding histogram
        """        
        super(TWHFilter, self).set_canvas(img, **kwargs)
        
        # set combobox and settingsbox for blurring parameters
        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Gaussian", "Median", "Bilateral Filtering"]], ["Bilateral Filtering"], ["str"]], sbox=[["Kernel Size", "Sigma", "d", "sigmaColor", "sigmaSpace"], [5, 2.3, 7, 100, 500], ["int", "float", "int", "int", "int"]], bbox=[["Blur Image", "Gradient Image"], [self.blur_image, self.gradient_image]])
        self._csbox_blur.grid(row=2, column=0, rowspan=7, sticky=N+W+E+S)

        # set combobox and settingsbox for edge detection parameters
        self._csbox_edges = csbox.CSBox(self, bbox=[["Get Edges"], [self.get_edges]], sbox=[["Threshold I", "Threshold II", "Aperture Size"], [50, 150, 3], ["int", "int", "int"]])
        self._csbox_edges.grid(row=10, column=0, rowspan=4, sticky=N+W+E+S)

        # set combobox and settingsbox for thresholding parameters    
        self._csbox_bthreshold = csbox.CSBox(self, bbox=[["Simple Thresholding"], [self.set_threshold_img]])
        self._csbox_bthreshold.grid(row=2, column=1, rowspan=1, sticky=N+W+S+E)
        self._csbox_threshold = scalebox.ScaleBox(self, scbox=[["Thresh"], [[0, 255, 2, 0]], ["int"]],  orient=HORIZONTAL, func=self.set_threshold_img_mask)
        self._csbox_threshold.grid(row=3, column=1, rowspan=1, sticky=N+W+S+E)

        self._csbox_athreshold = csbox.CSBox(self, cbox=[["adaptiveMethod"], [["Mean", "Gaussian"]], ["Gaussian"], ["str"]], sbox=[["blockSize", "C"], [5, 2], ["int", "int"]], bbox=[["Adaptive Thresholding"], [self.set_adaptive_thresholding]])
        self._csbox_athreshold.grid(row=4, column=1, rowspan=3, sticky=N+W+S+E)

        # set combobox and settingsbox for building difference images
        self._csbox_difference = csbox.CSBox(self, bbox=[["Clear Image List", "Add Image to Image List", "Compute Difference (Image)", "Show Image List"], [self.reset_dimage, self.set_dimage, self.compute_dimage, self.show_dimage]])
        self._csbox_difference.grid(row=7, column=1, rowspan=4, sticky=N+W+S+E)        

        # set combobox and settingsbox for hough transformation
        self._csbox_hough = csbox.CSBox(self, bbox=[["Hough Transform"], [self.get_hough_transform]], sbox=[["Threshold", "Minimum Line Length","Maximum Line Gap"], [40, 40, 40], ["int", "int", "int"]])
        self._csbox_hough.grid(row=14, column=0, rowspan=4, sticky=N+W+S+E)

        # set combobox and settingsbox for hough transformation
        self._csbox_gplot = csbox.CSBox(self, bbox=[["Laplacian Plot", "Gradient Plot"], [self.laplacian_plot, self.gradient_plot]], sbox=[["Threshold"], [0], ["int"]])
        self._csbox_gplot.grid(row=11, column=1, rowspan=3, sticky=N+W+S+E)

        self._button_quit.grid(row=18, column=0, columnspan=3, sticky=W+E)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def laplacian_plot(self, event=None):
        """Reset list of difference images
        """
        # get the currently displayed image
        img = self.get_obj().get_img(show=True)
        param = self._csbox_gplot.get_dict()
        plot = imgtools.plot_laplacian(img, threshold=param["Threshold"])

        # set image in canvas and update histogram
        self.get_obj().set_img(plot, clear_mask=False)
        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def gradient_plot(self, event=None):
        """Reset list of difference images
        """
        # get the currently displayed image
        img = self.get_obj().get_img(show=True)
        param = self._csbox_gplot.get_dict()
        plot = imgtools.plot_gradient(img, threshold=param["Threshold"])

        # set image in canvas and update histogram
        self.get_obj().set_img(plot, clear_mask=False)
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
    def compute_dimage(self, event=None):
        """Compute the difference image of the currently images in 'd_image'
        """
        
        # continue if two images are provided
        if len(self._dimage)<2:
            raise IndexError("There are not enough images available to compute the difference.")

        # compute the difference image of the currently images in 'd_image'
        img = np.absolute(imgtools.gray_image(self._dimage[-2].astype(np.float32))-imgtools.gray_image(self._dimage[-1].astype(np.float32)))

        #check wheter the image is not empty
        if np.sum(img) == 0:
            raise ValueError("Sum of differences is zero.")

        img = imgtools.project_data_to_img(img)

        # set image in canvas and update histogram
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Difference of images", dtype="img", value=[img, self._dimage[-1], self._dimage[-2]])

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
        elif param["Model"] == "Gaussian":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
            img = cv2.GaussianBlur(img, kernel_size, param["Sigma"], borderType=param["BorderType"])
        elif param["Model"] == "Median":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9
            img = cv2.medianBlur(img, kernel_size[0])
        elif param["Model"] == "Bilateral Filtering":
            # https://docs.opencv.org/master/d4/d86/group__imgproc__filter.html#ga9d7064d478c95d60003cf839430737ed
            img = cv2.bilateralFilter(img, param["d"], param["sigmaColor"], param["sigmaSpace"])

        # set image in canvas and update histogram
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

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
    def set_threshold(self, event=None):
        """Set a threshold via input of windows's slider
        """
        # get settings of combobox and fields 
        param = self._csbox_threshold.get_dict()
        thresh = param["Thresh"]
        method = cv2.THRESH_BINARY if param["Thresh"] else cv2.THRESH_BINARY + cv2.THRESH_OTSU

        # get the currently displayed image
        grayimg = imgtools.gray_image(self.get_obj().get_img(show=True))

        # implement thresholding and assign the result to the variable dst
        ret, dst = cv2.threshold(grayimg, thresh, 255, method)

        self._logger("Simple Thresholding with thresh: {}".format(ret))

        return ret, dst

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_threshold_img_mask(self, event=None):
        """Set a threshold via input of windows's slider and display as a mask
        """
        
        # set a threshold via input of windows's slider and display as a mask
        ret, dst = self.set_threshold()  
        
        # visualize the binary mask in the currently displayed image   
        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_threshold_img(self, event=None):
        """Set a threshold via input of windows's slider and display as a mask
        """

        # set a threshold via input of windows's slider and display as a mask
        ret, dst = self.set_threshold()  
        
        # set image in canvas and update histogram
        self.get_obj().set_img(imgtools.project_data_to_img(dst, dtype=np.uint8, factor=255), clear_mask=True)

        self.set_img()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_adaptive_thresholding(self, event=None):
        # get settings of combobox and fields 
        param = self._csbox_athreshold.get_dict()
        
        if  param["adaptiveMethod"] == "Mean":
            param_method = cv2.ADAPTIVE_THRESH_MEAN_C
        elif param["adaptiveMethod"] == "Gaussian":
            param_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        dst	= cv2.adaptiveThreshold(imgtools.gray_image(self._img), 255,  param_method, cv2.THRESH_BINARY, param["blockSize"], param["C"])

        self.set_threshold_mask(dst)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_edges(self):
        
        # get settings of combobox and fields 
        param = self._csbox_edges.get_dict()

        # get the currently displayed image
        img = imgtools.project_data_to_img(imgtools.gray_image(self.get_obj().get_img(show=True)), dtype=np.uint8, factor=255)

        aperture_size = param["Aperture Size"]
        if (aperture_size%2)==0 or aperture_size<3 or aperture_size>7:
            raise ValueError("Aperture size should be odd between 3 and 7.")

        edges = cv2.Canny(img, param["Threshold I"], param["Threshold II"], apertureSize=param["Aperture Size"])

        # set image in canvas and update histogram
        # self.get_obj().set_img(edges, clear_mask=False)
        # self.set_img()

        # open a topwindow with the edges of the currently displayed image computed via canny
        tw.TopWindow(self, title="Edges", dtype="img", value=[img, edges])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_hough_transform(self, event=None):

        # get settings of combobox and fields 
        param_edges = self._csbox_edges.get_dict()
        param_hough = self._csbox_hough.get_dict()

        # get the currently displayed image
        img = self.get_obj().get_img(show=True)
        grayimg = imgtools.gray_image(img)

        aperture_size = param_edges["Aperture Size"]
        if (aperture_size%2)==0 or aperture_size<3 or aperture_size>7:
            raise ValueError("Aperture size should be odd between 3 and 7.")

        edgeimg = cv2.Canny(grayimg, param_edges["Threshold I"], param_edges["Threshold II"], apertureSize=param_edges["Aperture Size"])
        
        img_list = [img, edgeimg]

        lines = cv2.HoughLinesP(edgeimg, 1, np.pi/180, param_hough["Threshold"],minLineLength=param_hough["Minimum Line Length"], maxLineGap=param_hough["Maximum Line Gap"])

        if lines is not None:
            houghimg = img.copy()
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(houghimg, (x1, y1), (x2, y2), (0, 0, 128), 1)

            img_list.append(houghimg)

        # open a topwindow with the edges of the currently displayed image computed via hough transform
        tw.TopWindow(self, title="Hough Transform", dtype="img", value=img_list)
