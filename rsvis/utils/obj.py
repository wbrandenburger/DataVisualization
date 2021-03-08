# ===========================================================================
#   obj.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET
import numpy as np
# difference between coco, pascal voc and ylo format
# https://towardsdatascience.com/coco-data-format-for-object-detection-a4c5eaf518c5

# voc: x_min, y_min, x_max, y_max
# coco: x_min, y_min, width, height
# yolo: x_mid, y_mid, width, height

class ObjConverter():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self,
        label2id=None,
        ):

        self.label2id = label2id

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_yolo(self, root):
        obj_list = list()
        for txt_obj in root:

            probability = 1
            category_id = 0
            bbox = list()

            r = txt_obj.split(" ")
            category_id = int(r[0])
            if len(r) > 1:
                probability = 1
                bbox = [float(p) for p in r[1:5]]
            
            obj_list.append(
                {
                    'bbox': bbox,
                    'label': category_id,
                    'probability': probability,
                    'iscrowd': 0,
                    'category_id': category_id,
                    'ignore': 0
                } 
            )         
        return obj_list

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_coco(self, root):
        # root = [root] if not isinstance(root, list) else root
        root = root['annotations']
        for r in root:
            
            bbox = list()
            if 'segmentation' in r:
                if isinstance(r['segmentation'][0], str):
                    bbox = [ float(p) for p in r['segmentation'][0].split(" ")]
                else:
                    bbox = r["segmentation"][0]
            r['bbox'] = bbox if not 'bbox' in r else [float(b) for b in r['bbox']]
            r['label'] = r['label'] if 'label' in r else self.label2id( r['category_id'] ) # @todo: changed
            if 'area' in r:
                r['area'] = float(r['area'])
            r['probability'] = 1 if not 'probability' in r else float(r['probability'])
        return root

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_voc(self, root):
        obj_list = list()
        for r in root.find("objects").findall("object"):   
            label = r.findtext('name') if r.find('name') else r.find('possibleresult').findtext('name')
            probability = 1 if r.find('name')  else r.find("possibleresult").findtext('probability')
            category_id = self.label2id(label) if self.label2id else 0
            
            bndbox = r.find('bndbox')
            points = r.find('points')

            bbox = list()
            if bndbox:
                xmin = float(bndbox.findtext('xmin'))
                ymin = float(bndbox.findtext('ymin'))
                xmax = float(bndbox.findtext('xmax'))
                ymax = float(bndbox.findtext('ymax'))
                bbox =  [xmin, ymin, xmax, ymax], # bbox
            elif points:
                for pts in points:
                    bbox.append ([float(p) for p in pts.text.split(",")][0:8])
                    
                bbox_arr = np.array(bbox)
                bbox_min = np.min(bbox_arr, axis=0)
                bbox_max = np.max(bbox_arr, axis=0)
                bbox = [bbox_min[0], bbox_min[1], bbox_max[0], bbox_max[1]]

            obj_list.append(
                {
                    'area': (bbox[3]-bbox[1])*(bbox[2]-bbox[0]),
                    'bbox': bbox,
                    'label': label,
                    'probability': probability,
                    'category_id': category_id,
                    'iscrowd': 0,
                    'ignore': 0
                }
            )
        return obj_list