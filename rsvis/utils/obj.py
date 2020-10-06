# ===========================================================================
#   obj.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET

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
        label2id=dict(),
        ):

        self.label2id = label2id

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_yolo(self, root):
        obj_list = list()
        for txt_obj in root:
            r = txt_obj.split(":")

            label = r[0]
            probability = r[1]
            category_id = self.label2id[label] if self.label2id else 0
            box = [float(p) for p in eval(r[2])]
            dtype = "minmax"
            obj_list.append(
                {
                    'bbox': box,
                    'label': label,
                    'probability': probability,
                    'category_id': category_id,
                    'ignore': 0,
                    'dtype': 'dtype'
                } 
            )         
        return obj_list

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_coco(self, root):
        root = [root] if not isinstance(root, list) else root
        for r in root:
            
            box = list()
            dtype = 'coco'
            if 'segmentation' in r:
                if isinstance(r['segmentation'][0], str):
                    box = [ int(p) for c in s['segmentation'][0].split(" ")]
                else:
                    box = coco_obj["segmentation"][0]

                dtype = 'polyline'
            
                r['bbox'] = box
                r['dtype'] = dtype
                r['probability'] = 1 if not 'probability' in r else r['probability']
                # r['category_id'] = self.label2id[r['label']] if self.label2id else 0
        
        return root

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_obj_from_voc(self, root):
        obj_list = list()
        for r in root.find("objects").findall("object"):   
            label = r.findtext('name') if r.find('name') else r.find('possibleresult').findtext('name')
            probability = 1  if r.find('name')  else r.find("possibleresult").findtext('probability')
            category_id = self.label2id[label] if self.label2id else 0
            
            bndbox = r.find('bndbox')
            points = r.find('points')

            box = list()
            if bndbox:
                xmin = float(bndbox.findtext('xmin')) - 1
                ymin = float(bndbox.findtext('ymin')) - 1
                xmax = float(bndbox.findtext('xmax'))
                ymax = float(bndbox.findtext('ymax'))
                box =  [xmin, ymin, xmax, ymax], # bbox
                dtype = 'minmax'
            elif points:
                for pts in points:
                    box.append([float(p) for p in pts.text.split(",")][0:8])
                dtype = 'polyline'

            obj_list.append(
                {
                    'bbox': box,
                    'label': label,
                    'probability': probability,
                    'category_id': category_id,
                    'ignore': 0,
                    'dtype': 'dtype'
                }
            )
        return obj_list

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_label2id(self, path: str):
        """id is 1 start"""
        with open(path, 'r') as f:
            labels_str = f.read().split()
        labels_ids = list(range(1, len(labels_str)+1))
        self.labelid = dict(zip(labels_str, labels_ids))