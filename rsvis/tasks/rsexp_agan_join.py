# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.rsioobject
import rsvis.utils.general as gu
from rsvis.utils import opener, imgtools
import rsvis.utils.logger

import rsvis.utils.bbox 
import rsvis.utils.patches_ordered_ext
import rsvis.utils.utils_gan

import cv2
import math
import numpy as np
import pathlib
from tqdm import tqdm
import torch
import os
import shutil


def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0, 0, 0, 0, 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    a = (min(boxAArea, boxBArea) + interArea)/ (2*min(boxAArea, boxBArea))
    # return the intersection over union value
    return iou,  a, interArea, boxAArea ,boxBArea

def dist_med(boxA, boxB):
    xA_m = min(boxA[0], boxA[2]) + abs(boxA[2]-boxA[0])
    yA_m = min(boxA[1], boxA[3]) + abs(boxA[3]-boxA[1])
    
    xB_m = min(boxB[0], boxB[2]) + abs(boxB[2]-boxB[0])
    yB_m = min(boxB[1], boxB[3]) + abs(boxB[3]-boxB[1])


    return (xB_m - xA_m)**2+(yB_m - yA_m)**2

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def run(
        files, 
        label, 
        param_in,
        param_out=dict(),
        param_classes=list(),
        param_exp=list(),
        param_cloud=dict(),
        param_show=dict()
    ):

    rsvis.utils.logger.Logger().get_logformat("Start RSExp with the following parameters:", param_label=label, param_in=param_in, param_out=param_out, param_classes=param_classes, param_cloud=param_cloud, param_show=param_show)

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = [c["label"] for c in param_classes]
    param_label = [c["color"] for c in param_classes]
    param_color = [c["color"] for c in param_classes]
    rsio = rsvis.utils.rsioobject.RSIOObject(files, label, param_in, param_out, param_show, label=param_label, color=param_color
    )


    if os.path.exists(param_out["log"]["path_dir"]):
        shutil.rmtree(param_out["log"]["path_dir"], ignore_errors=True)

    images_in = rsio.get_img_in()
    images_out = rsio.get_img_out(img_name="image")
    images_log_out = rsio.get_log_out(**param_out["log"])

    label_id = dict()
    for c in param_classes:
        label_id[str(c["id"])] = c["name"]
    # print(label_id)

    param = param_exp
    filepaths = [f for f in os.listdir(param["results"]) if f.endswith(".txt")]
    
    img_obj = [list() for i in range(0, len(images_in))]
    for file in tqdm(filepaths):
        filename, file_extension = os.path.splitext(file) 
        img_param = [int(f) for i, f in enumerate(filename.split("-")) if i > 0]
        
        img_obj[img_param[4]-1].append({'box': img_param[0:4], "file": file})

    thresh = 2  # 3
    for img_idx, (img, obj) in tqdm(enumerate(zip(rsio.get_img_in(), img_obj))):

        box_list = list()
        for o in obj:
            root=list()
            name = o["file"].split("-")
            with open(os.path.join(param["results"],o["file"]), "r") as f:
                root = ([k.split(" ") for k in f.read().splitlines()])
            
            for r in root:
                if(r):
                    box = [
                        float(r[1])*255*param["factor"][0], 
                        float(r[2])*255*param["factor"][1], 
                        float(r[3])*255*param["factor"][0], 
                        float(r[4])*255*param["factor"][1]
                    ]
                    
                    if (box[0]-box[2])/2<thresh and not int(name[3])==0:
                        continue
                    
                    if (box[0]+box[2])/2>(param["img_size"][0]-2) and not o["box"][3]==param["img_size"][0]:
                        continue
                    
                    if (box[1]+box[3])/2 <thresh and not int(name[1])==0:
                        continue

                    if (box[1]+box[3])/2>(param["img_size"][1]-2) and not o["box"][1]==param["img_size"][1]:
                        continue

                    box = rsvis.utils.bbox.BBox().get_minmax(box, dtype="cowc")
                    m = [o["box"][2], o["box"][0], o["box"][3], o["box"][1]]
                    box = [box[0]+o["box"][2], box[1]+o["box"][0], box[2]+o["box"][2], box[3]+o["box"][0]]

                    d = dist_med(box, m)
                    box_ap = True
                    for box_idx, box_d in enumerate(box_list): 
                        iou, a, _, b, c = bb_intersection_over_union(box, box_d)
    

                        if iou > 0.35 or  a>0.9:
                            box_ap = False
                            # box_list[box_idx][4][int(r[0])-1] += 1
                            if box_d[5]<float(r[5])*100:
                                box_list[box_idx][4]=r[0]
                                box_list[box_idx][5]=float(r[5])*100
                            if b > c:
                                box_list[box_idx] = [*box, box_list[box_idx][4], float(r[5])*100, d]
                        
                    # # box = [float(r[1])*255*param["factor"][0], float(r[2])*255*param["factor"][1], float(r[3])*255*param["factor"][0], float(r[4])*255*param["factor"][1]]
                    if box_ap:
                        box_list.append([*box, r[0], float(r[5])*100, d])
                        #box_list.append([*box, np.zeros([10]), float(r[5])*100, d])


                        # box_list[-1][4][int(r[0])-1] += 1
                        
        msg = ""
        for b in box_list:    
            msg = "{}{} : {} :  [{}, {}, {}, {}]\n".format(
                msg, label_id[b[4]], b[5], b[0], b[1], b[2], b[3])
                # msg, label_id[str(np.argmax(b[4])+1)], b[5], b[0], b[1], b[2], b[3])
            
        src_path = img.get_img_from_label(param["label"]).path
        images_log_out(src_path, msg)