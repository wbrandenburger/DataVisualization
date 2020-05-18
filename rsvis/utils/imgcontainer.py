# ===========================================================================
#   imgcontainer.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgtools

import pathlib
import tifffile
import numpy as np

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgListContainer(list):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, load=None, live=False, bbox=list(), **kwargs):
        self._load = load
        self._live = live            
        self._bbox = bbox  

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def append(self, img=list(), path=None, label=None, load=None,  live=None,  bbox=list(), **kwargs):

        self._live = self._live if live is None else live
        self._bbox = self._bbox if bbox  else bbox
        self._load = self._load if load is None else load
        
        super(ImgListContainer, self).append(
            ImgContainer(
                img=img,
                path=path,
                label=label,
                load=self._load,
                bbox = self._bbox
            )
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def copy(self):
        obj = ImgListContainer()
        for idx, item in enumerate(self):
            obj.append(
                img=item._obj, 
                path=item._path, 
                label=item._label, 
                load=item._load, 
                live=item._live, 
                bbox=item._bbox
            )
        return obj

    # @todo[new]: Implement iteration for clearing image data in non-active imgcontainers

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def label(self, label):
    #     for item in self:
    #         if item.label==label:
    #             return item

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_label(self, label):
        for item in self:
            if item.label==label:
                return item

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_bbox(self, bbox):
        self._bbox = bbox
        for item in self:
            item.bbox = bbox

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgContainer(object):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            img=list(), 
            path=None, 
            label="image", 
            load=None,
            live=False,
            bbox=list(),  
            **kwargs          
        ):
        self._obj = list()
        self._show = list()

        self._path = path

        self._label = label
        self._live = live
        self._load = load if load else lambda path, label: tifffile.imread(path) # @todo[change]: More complex load function from imgio
     
        self._bbox = bbox

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self):
        self._obj = list()
        self._show = list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def obj(self):
        return self._obj

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @obj.setter
    def obj(self, obj):
        self._obj = obj

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def path(self):
        return self._path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def bbox(self):
        return self._bbox

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @bbox.setter
    def bbox(self, bbox):
        self._bbox = bbox

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def label(self):
        return self._label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @path.setter
    def path(self, path):
        self.validate_path(path)
        self._path = path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @label.setter
    def label(self, label):
        self._label = label
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------  
    @property
    def show(self):
        if not len(self.obj) or self._live:
            self.obj = self.imread()
                
        if not len(self._show):
            self._show = imgtools.project_data_to_img(
            imgtools.stack_image_dim(self.obj), dtype=np.uint8, factor=255)
        
        data = self._show    
        return self.get_bbox(data) if self.bbox else data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------  
    @property
    def data(self):
        if not len(self.obj) or self._live:
            self.obj = self.imread()

        data = self.obj
        return self.get_bbox(data) if self.bbox else data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_bbox(self, data):
        if len(data.shape)>2:
            return data[self._bbox[0]:self._bbox[1], self._bbox[2]:self. _bbox[3], :]
        else:
            return data[self._bbox[0]:self._bbox[1], self._bbox[2]:self. _bbox[3]]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imread(self):
        if self.validate_path(self.path):
            return self._load(self.path, self.label)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def load(self):
        self.obj = self.imread()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def validate_path(self, path, raise_error=True):
        if not pathlib.Path(path).is_file():
            raise ValueError("File {} does not exist.".format(path))
        return True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __eq__(self, label):
        return True if label == self._label else False

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __repr__(self):
        return "{}\n\t<obj: {}>".format(super(ImgContainer, self).__repr__(), self.obj.shape)