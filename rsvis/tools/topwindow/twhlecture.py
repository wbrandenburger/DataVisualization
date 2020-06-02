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
        self._csbox_blur = csbox.CSBox(self, cbox=[["Model"], [["Average", "Median", "Binomial"]], ["Average"], ["str"]], sbox=[["Kernel Size", "Sigma"], [5, 2.3], ["int", "float"]], bbox=[["Blur Image", "Gradient Image"], [self.blur_image, self.gradient_image]])
        self._csbox_blur.grid(row=2, column=0, rowspan=5, sticky=N+W+E)

        # set combobox and settingsbox for building difference images
        self._csbox_difference = csbox.CSBox(self, bbox=[["Clear Image List", "Add Image to Image List", "Compute Difference (Image)", "Show Image List"], [self.reset_dimage, self.set_dimage, self.compute_dimage, self.show_dimage]])
        self._csbox_difference.grid(row=2, column=1, rowspan=4, sticky=N+W+S+E)        
        
        self._button_quit.grid(row=7, column=0, columnspan=3, sticky=W+E)

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
            # implementation of the binomial filter
            pass

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
        tw.TopWindow(self, title="Difference of images", dtype="img", value=self._dimage, q_cmd=self._q_cmd)

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
        img = np.zeros((0,0)) # implementation of the differences of images img_a and img_b

        # set image in canvas and update histogram
        self.get_obj().set_img(img, clear_mask=False)
        self.set_img()

        # open a topwindow with images used for building the difference
        tw.TopWindow(self, title="Difference of images", dtype="img", value=[img_a, img_b], q_cmd=self._q_cmd)

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
        img = imgtools.project_data_to_img(imgtools.get_gray_image(self.get_obj().get_img(show=True)))

        # calculate gradient
        gradient_x = gradient_y = magnitude = np.zeros((0,0)) # implementation of the gradient images and gradient magnitudes

        # open a topwindow with gradient images
        tw.TopWindow(self, title="Gradient Image", dtype="img", value=[img, magnitude, gradient_x, gradient_y], q_cmd=self._q_cmd)
