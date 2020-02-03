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
    
def get_img_overview(files, dir_rgb):

    number_row = math.floor(math.sqrt(len(files)))
    number_col = math.ceil(math.sqrt(len(files)))

    number_row = number_col

    img = cv2.imread(dir_rgb + files[0])
    img_shape = img.shape
    img_shape = (int(img_shape[0] * 1.0), int(img_shape[0] * 1.0), 3)

    img_out = np.zeros(shape=[img_shape[0]*number_row, img_shape[1]*number_col, img_shape[2]], dtype=np.uint8 )
    idx = 0
    for col in range(0, img_out.shape[1], img_shape[1]):
        for row in range(0, img_out.shape[0], img_shape[0]):
            if idx < len(files):
                img_tmp = cv2.imread(dir_rgb + files[idx])
                img_tmp = cv2.resize(img_tmp, (img_shape[0], img_shape[1]),interpolation=cv2.INTER_LINEAR)
                img_out[row : row + img_shape[0], col : col + img_shape[1], :] = img_tmp
                idx = idx + 1

    return img_out, number_col

    def show_cloud(image,height):
    img = image.astype(float)/256.0
    #height = height * img.shape[0] / 8
    f = tempfile.mkstemp(suffix = '.ply')
    write_cloud(img, height, f[1])

    subprocess.Popen(['C:\\Program Files\\ccViewer\\ccViewer.exe', f[1]])

def write_cloud(img, height, file_path: str):
    
    point_number = img.shape[0]*img.shape[1]

    file_object = open(file_path, 'w')
    file_object.write('ply\n')
    file_object.write('format binary_little_endian 1.0\n')
    string_object = 'element vertex %i\n' % point_number
    file_object.write(string_object)
    file_object.write('property float x\n')
    file_object.write('property float y\n')
    file_object.write('property float z\n')
    file_object.write('property float blue\n')
    file_object.write('property float green\n')
    file_object.write('property float red\n')
    file_object.write('end_header\n')
    file_object.close()

    idx = 0
    indices = np.zeros((point_number, 2))
    for row in range(0, img.shape[0]):
        for col in range(0, img.shape[1]):
            indices[idx, 0] = row
            indices[idx, 1] = col
            idx = idx + 1

    point_objects = np.concatenate((indices, np.reshape(height, (point_number, 1), order='F'), np.reshape(img, (point_number, 3), order='F')), axis=1)

    point_objects_struct = Struct('6f')
    with open(file_path, 'ab') as file_object:
        for point_object in point_objects.tolist():
            file_object.write(point_objects_struct.pack(*point_object))

    return 1

