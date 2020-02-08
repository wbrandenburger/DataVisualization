# ==============================================================================
#   img2histpdf.py: Compute and plot histogram as well as pdf of an image.------
# ==============================================================================
'''
 img2histpdf.py: Compute and plot histogram as well as pdf of an image.
'''

#   import ---------------------------------------------------------------------
# ==============================================================================

import click
from multimethod import multimethod

import os
import re
import subprocess
from struct import Struct
from configobj import ConfigObj

import math

import tifffile as tiff
import numpy as np as np
import cv2

CCVIEWER = r'C:\\Program Files\\ccViewer\\ccViewer.exe'

#   functions ------------------------------------------------------------------
# =============================================================================

@multimethod
def show_label(file_path: str):
    img = cv2.imread(file_path)
    for label in LABELS_COLOR:
        img[np.where((img == LABELS_COLOR[label][0]).all(axis=2))] = LABELS_COLOR[label][1]
    return img

@multimethod
def prepare_labels_color(file_path: str):

    file_object = open(file_path, 'r')
    labels_color_temp = file_object.read().splitlines()
    file_object.close()

    for i in labels_color_temp:
        labels_config = i.split()

        label_color_old = [int(labels_config[1]), int(labels_config[1]), int(labels_config[1])]
        label_color_new = [int(labels_config[2][1:3], 16), int(labels_config[2][3:5], 16), int(labels_config[2][5:7], 16)]
        LABELS_COLOR[labels_config[0]] = [label_color_old, label_color_new]

    return 1 
    
    