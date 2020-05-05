# ===========================================================================
#   imgcontainer.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.objcontainer

import pathlib
import tifffile
import numpy as np

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgListContainer(list):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, default_spec="image", load=None, live=False, obj_flag=True, obj_copy=False, bbox=list(), log_dir=None, **kwargs):
        self._default_spec = default_spec
        self._load = load
        self._live = live            
        self._obj_flag = obj_flag, 
        self._obj_copy = obj_copy
        self._bbox = bbox
        self._log_dir = log_dir        

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def append(self, img=np.ndarray(0), path=None, spec=None, load=None,  live=None, obj_flag=None, obj_copy=None, bbox=list(), log_dir=None, **kwargs):

        self._live = self._live if live is None else live
        self._obj_flag = self._obj_flag if obj_flag is None else obj_flag
        self._obj_copy = self._obj_copy if obj_copy is None else obj_copy
        self._bbox = self._bbox if bbox  else bbox
        self._log_dir = self._log_dir if log_dir is None else log_dir
        self._load = self._load if load is None else load
        
        spec = self._default_spec if not spec else spec
        super(ImgListContainer, self).append(
            rsvis.utils.imgcontainer.ImgContainer(
                img=img,
                path=path,
                spec=spec,
                load=self._load,
                live=self._live, 
                obj_flag=self._obj_flag, 
                obj_copy=self._obj_copy,
                bbox = self._bbox,
                log_dir=self._log_dir
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
                spec=item._spec, 
                load=item._load, 
                live=item._live, 
                bbox=item._bbox, 
                obj_flag=item._obj_flag, 
                obj_copy=item._obj_copy, 
                log_dir=str(item._log_dir)
            )
        return obj

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def spec(self, spec):
    #     for item in self:
    #         if item.spec==spec:
    #             return item

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_from_spec(self, spec):
        for item in self:
            if item.spec==spec:
                return item

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_bbox(self, bbox):
        for item in self:
            item.bbox = bbox

    # @todo[new]: method __repr__

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImgContainer(rsvis.utils.objcontainer.ObjContainer):
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self, 
            img=np.ndarray(0), 
            path=None, 
            spec="image", 
            load=None,
            live=False,
            obj_flag=True, 
            obj_copy=False,
            bbox=list(),
            log_dir=None            
        ):
        super(ImgContainer, self).__init__(obj=img, obj_flag=obj_flag, obj_copy=obj_copy)

        self._path = None
        if path:
            self._path = path

        self._spec = spec
        self._live = live
        self._load = load if load else lambda path, spec: tifffile.imread(path)
     
        self._bbox = bbox

        self._log_dir = pathlib.Path(log_dir) if log_dir else None

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def path(self):
        return self._path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def log(self):
        return str(pathlib.Path.joinpath(
            self._log_dir, "{}.log".format(pathlib.Path(self.path).stem)
        )) if self._log_dir else None

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
    def spec(self):
        return self._spec

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @path.setter
    def path(self, path):
        self.validate_path(path)
        self._path = path

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @spec.setter
    def spec(self, spec):
        self._spec = spec
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------  
    @property
    def data(self):
        if self._live:
            data = self.imread()
        else:
            self.obj = self.imread()
            data = super(ImgContainer, self).data

        if self.bbox:
            return data[self._bbox[0]:self._bbox[1], self._bbox[2]:self. _bbox[3], :]
        return data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def imread(self):
        if self.validate_path(self.path):
            return self._load(self.path, self.spec)

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
    def __eq__(self, spec):
        return True if spec == self._spec else False

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __repr__(self):
        return "{}\n\t<obj: {}>".format(super(ImgContainer, self).__repr__(), self.obj.shape)