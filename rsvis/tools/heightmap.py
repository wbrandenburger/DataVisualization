# ===========================================================================
#   pctools.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.ply
import rsvis.config.settings

import tempfile
import subprocess
import pandas
import pathlib

import cv2
import numpy as np

height_map = dict()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_height_map(img):
    global height_map

    img_width, img_height, _ = img.shape
    dim_new =(img_width*img_height)
    height_factor = float(np.max(img))/(float(np.max([img_width, img_height])) / 10)

    print(height_factor)
    img = img.astype(float)/height_factor

    grid = np.indices((img_width, img_height), dtype="float")
    height_map.update( 
        {
            'x': grid[0,...].reshape(dim_new).T, 
            'y': grid[1,...].reshape(dim_new).T, 
            'z': img[...,0].reshape(dim_new).T
        }
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def colorize_height_map(img):

    global height_map

    img_width, img_height, _ = img.shape
    dim_new =(img_width*img_height)

    height_map.update(
        {
            'red': img[:,:,0].reshape((img.shape[0]*img.shape[1])).T, 
            'green': img[:,:,1].reshape((img.shape[0]*img.shape[1])).T, 
            'blue': img[:,:,2].reshape((img.shape[0]*img.shape[1])).T
        }
    )

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_intensity_to_height_map(img):

    global height_map

    try:
        img_width, img_height, _ = img.shape
        dim_new =(img_width*img_height)

        height_map.update(
            {
                'intensity': img[:,:,1].reshape((img.shape[0]*img.shape[1])).T
            }
        )
    except AttributeError:
        pass

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def open_height_map(img, height, label=None, ccviewer=True, mesh=True):

    global height_map

    get_height_map(height)
    colorize_height_map(img)
    if not ccviewer:
        add_intensity_to_height_map(label)

    data = pandas.DataFrame(height_map, index=range(img.shape[0]*img.shape[1]))
    
    # create a temporary file
    path = tempfile.mkstemp(prefix="rsvis-", suffix=".ply")[1]

    rsvis.utils.ply.write_ply(path, points=data)
     
     
    if mesh:
        args = rsvis.config.settings._SETTINGS["cloud_delaunay_args"]
        process = subprocess.Popen(
            get_args(
                rsvis.config.settings._SETTINGS["cloud_process"], 
                [item.format(**{"obj": { "path": path}}) for item in args]
            )
        )
        process.wait()
    if ccviewer:
        subprocess.Popen(
            get_args( rsvis.config.settings._SETTINGS["cloud_viewer"], path)
        )
    else:          
        subprocess.Popen( 
            get_args(rsvis.config.settings._SETTINGS["cloud_editor"],path)
        )

    height_map = dict()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------   
def get_args(cmd, *args):
    cmd = cmd.copy() if isinstance(cmd, list) else [cmd]
    for a in args:
        cmd.extend(*to_list(a))
    
    return " ".join(cmd)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def to_list(*args):
    return (x if isinstance(x, list) or x is None else [x] for x in args)
