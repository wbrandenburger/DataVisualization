# ===========================================================================
#   imgio.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
from rsvis.utils.bbox import BBox
from rsvis.__init__ import _logger
import rsvis.utils.general as gu
import rsvis.utils.imgcontainer
from rsvis.utils import imgtools
import rsvis.utils.bbox
import rsvis.utils.yaml
import rsvis.utils.json
import rsvis.utils.obj

import cv2
import numpy as np
import pathlib
import PIL
import shutil
import tifffile
import xml.etree.ElementTree as ET

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_copy_str(path, logger=None):
    copy_str = "[COPY] {}".format(path)
    show_io_str(copy_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_info_str(info, logger=None):
    info_str = "[INFO] {}".format(info)
    show_io_str(info_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_open_str(path, logger=None):
    open_str = "[OPEN] {}".format(path)
    show_io_str(open_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_read_str(path, logger=None):
    read_str = "[READ] {}".format(path)
    show_io_str(read_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_write_str(path, logger=None):
    write_str = "[WRITE] {}".format(path)
    show_io_str(write_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_io_str(io_str, logger=None):
    _logger.info(io_str)

    if logger is not None:
        logger(io_str)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_xml(path, logger=None):
    show_read_str(path, logger=logger)
    
    return ET.parse(path).getroot()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_object(path, logger=None, label2id=None):
    show_read_str(path, logger=logger)

    objects = list()
    if pathlib.Path(path).suffix==".txt":
        root = read_log(path, logger=logger)
        objects = rsvis.utils.obj.ObjConverter(label2id=label2id).get_obj_from_yolo(root)
        
    if pathlib.Path(path).suffix==".xml":
        root = read_xml(path, logger=logger)
        objects = rsvis.utils.obj.ObjConverter(label2id=label2id).get_obj_from_voc(root)

    if pathlib.Path(path).suffix==".json":
        root = read_json(path, logger=logger)
        objects = rsvis.utils.obj.ObjConverter(label2id=label2id).get_obj_from_coco(root)

    
    for idx in range(len(objects)):
        objects[idx]["bbox"] = [objects[idx]["bbox"][1], objects[idx]["bbox"][3], objects[idx]["bbox"][0], objects[idx]["bbox"][2]]
        objects[idx]["bbox"] = BBox().corner2polyline(objects[idx]["bbox"])
 
    return objects

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------

def write_object(path, objects, logger=None):
    show_write_str(path, logger=logger)

    if pathlib.Path(path).suffix==".txt":
        np.matrix(objects)
        np.savetxt(path, objects, fmt="%i : %1.3f : [%1.3f, %1.3f, %1.3f, %1.3f]")
        # np.savetxt(path, obj, fmt="%i %1.3f %1.3f %1.3f %1.3f %1.3f")
    if pathlib.Path(path).suffix==".xml":
        pass

    if pathlib.Path(path).suffix==".json":
        for obj in objects:
            obj['probability'] = np.float64(obj['probability'])
            obj['bbox'] = list(np.array(obj['bbox'], dtype=np.float64))
        write_json(path, {'annotations': objects}, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_object(path, scale=100, default=list(), logger=None, **kwargs):
    if not pathlib.Path(path).exists():
        return default
    obj = read_object(path, logger=logger)
    if scale != 100 and obj is not None:
        for o in obj:
            o["bbox"] = (np.asarray(o["bbox"])*(float(scale)/100.0)).tolist()
            # o["bbox"] = [int(box*(float(scale)/100.0)) for box in o["bbox"]]
    
    return obj if obj else default

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def set_object(path, obj, scale=100, logger=None, **kwargs):
    if scale != 100:
        for o in obj:
            o["bbox"] = (np.asarray(o["bbox"])*(float(scale)/100.0)).tolist()
            # o["bbox"] = [int(box/(float(scale)/100.0)) for box in o["bbox"]]
    
    write_object(path, obj, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_yaml(path, logger=None):
    show_read_str(path, logger=logger)

    return rsvis.utils.yaml.data_to_yaml(path)
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_yaml(path, data, logger=None):
    show_write_str(path, logger=logger)

    rsvis.utils.yaml.data_to_yaml(path, data)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_json(path, logger=None):
    show_read_str(path, logger=logger)

    return rsvis.utils.json.json_to_data(path)
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_json(path, data, logger=None):
    show_write_str(path, logger=logger)

    rsvis.utils.json.data_to_json(path, data)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_log(path, logger=None):
    show_read_str(path, logger=logger)

    with open(path, "r") as f:
        return f.read().splitlines()
        
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_log(path, log, logger=None):
    show_write_str(path, logger=logger)

    with open(path, "w") as f:
        f.write(log)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_log(path, logger=None, **kwargs):
    if not pathlib.Path(path).exists():
        return
    return read_log(path, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def show_log(path, default="There is no logging information.", logger=None, **kwargs):
    log_str = get_log(path, logger=logger)
    if not log_str:
        show_info_str(default, logger=logger)
    else:
        show_io_str(log_str, logger=logger)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def read_image(path, logger=None,):
    show_read_str(path, logger=logger)
    
    if str(path).endswith(".tif"):
        img = tifffile.imread(path)
    else:
        img = cv2.imread(path, 1)
        if img.ndim == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = np.asarray(PIL.Image.open(path))
    
    return img

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def write_image(path, img, logger=None,):
    show_write_str(path, logger=logger)

    if str(path).endswith(".tif"):
        tifffile.imwrite(path, img)
    else:
        cv2.imwrite(path, cv2.cvtColor(img[:,:, 0:3], cv2.COLOR_BGR2RGB))

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def copy_image(path, dest, logger=None,):
    show_copy_str(dest, logger=logger)
    shutil.copy2(path, dest)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_image(
        path, 
        spec,
        label=list(), 
        color=list(),
        scale=100, 
        show=False, 
        logger=None,
        **kwargs
    ):

    img = read_image(path, logger=logger)

    if show:
        show_info_str(imgtools.get_array_info(img), logger=logger)

    if scale < 100:
        img = imgtools.resize_img(img, scale)

    if label and spec == "label":
        img = imgtools.labels_to_image(img, label)
        # if color:
        #     img = imgtools.image_to_labels(img, color)

    return img
