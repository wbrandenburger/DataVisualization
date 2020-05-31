#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
from scipy.signal import argrelextrema
import scipy.ndimage.filters as ft
import scipy.signal as sg

from matplotlib.widgets import Slider, Button, RadioButtons


from rsvis.shadow.smoothing import *

def isShadow(K):
	K_R = K[2]
	K_G = K[1]
	K_B = K[0]

	# Property 1: tal*K_H^80 < K_H < eta*K_H^20
	if K_R < 1.59 or K_R > 48.44:
		return False

	if K_G < 1.43 or K_G > 41.6:
		return False

	if K_B < 1.27 or K_B > 32.4:
		return False

	# Property 2   K_R > K_G > K_B
	if (K_B>K_R) or (K_B>K_G) or (K_G>K_R):
   		return False

	# Property 3   
	# K_R-K_G>epsilon and K_G-K_B>epsilon  if  K_R>K_R^80
	# K_R-K_G> (epsilon/2) and K_G-K_B>(epsilon/2)  if  K_R<=K_R^80
	# epsilon = 0.33/2 = 0.165

	if K_R>3.18:
		if (K_R-K_G)<0.165 or (K_G-K_B)<0.165:
			return False
	
	elif (K_R-K_G)<0.0825 or (K_G-K_B)<0.0825:
		return False

	return True


def shadowDetection(img, d=7, sigmaColor=700, sigmaSpace=25, logger=None):

	dtype = cv2.CV_32F
	
	grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	grayimg = cv2.bilateralFilter(grayimg, d, sigmaColor, sigmaSpace)

	shdwimg = cv2.filter2D(
		grayimg, 
		dtype, 
		np.array(
			[[-1., -1., -1.], [-1., 32., -1.], [-1., -1., -1.]], 
			dtype=float
		)/8., 
		borderType= cv2.BORDER_CONSTANT)
	normshdwimg = cv2.normalize(shdwimg, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
	
	if logger is not None:
		logger("Shadw value: {}".format(np.mean(grayimg)*1.3))
	no_shadow_mask = np.logical_and(shdwimg>np.mean(grayimg)*1.3, grayimg>255/2)
	medio_nonShdw = np.sum(np.where(np.stack([no_shadow_mask]*3, axis=2), img, [0,0,0]), axis=(0, 1))

	imgOut = np.where(no_shadow_mask, 0, 255).astype(np.uint8)
	count = np.count_nonzero(no_shadow_mask)

	# # Just in case there are shadow-free pixels
	# if count:
	# 	# Checking on shadow-free areas, verifying the K_H property with windows of size 3
	# 	kernel =  np.array([[1., 1., 1.], [1., 1., 1.], [1., 1., 1.]], dtype=float)
	# 	kernel = kernel/np.sum(kernel)

	# 	imgtarget = cv2.filter2D(imgOut, dtype, kernel, borderType= cv2.BORDER_CONSTANT)
	# 	imgsum = cv2.filter2D(img, dtype, kernel, borderType= cv2.BORDER_CONSTANT)

	# 	imgtarget_verified = np.where(np.logical_or(imgtarget==1, imgtarget==0), True, False)
	# 	imgsum_med = np.divide(np.power(medio_nonShdw/count+14, 2.4), np.power(imgsum+14, 2.4))
	# 	imgOut = np.where(np.logical_and(imgtarget_verified, np.apply_along_axis(isShadow, 2, imgsum_med)), 255, imgOut)

	# imgOut = cv2.morphologyEx(imgOut, cv2.MORPH_CLOSE,  cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))

	return (imgOut, shdwimg, normshdwimg)
		

