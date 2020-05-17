# ===========================================================================
#   heightmap.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
from rsvis.utils import imgio, imgtools, opener, ply
import rsvis.utils.logger

import numpy as np
import pandas
import tempfile

#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def get_array_info(height, verbose=False):
    return "[PCL] Shape: {}, Type: {}, Range: {:.3f}, {:.3f}".format(height.shape, height.dtype, np.min(height), np.max(height))

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Height():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, param, logger=None):
        self._height= dict()
        self._num_points = None
        self._shape = list()

        io = gu.PathCreator(**gu.get_value(param["temp"], "temp", dict()))
        self._path = io(tempfile.mkstemp(prefix="shdw-", suffix=".ply")[1])
        
        self._param = param["process"]
        self.set_param_normal()

        self._logger = rsvis.utils.logger.Logger(logger=logger)
        self._opener = opener.Opener(param["opener"], logger=self._logger)

        self._stock = [0] * 3

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_height(self, heightmap, factor=1.0):
        if not len(heightmap):
            return

        self._num_points = heightmap.shape[0]*heightmap.shape[1]
        self._shape = heightmap.shape[0:2]
        heightmap = imgtools.expand_image_dim(heightmap.astype(np.float32))

        heightmap = (heightmap - np.min(heightmap))/np.float32(factor)

        grid = np.indices((self._shape), dtype=np.float32)

        self._height.update( {
                'x': grid[0,...].reshape(self._num_points).T, 
                'y': grid[1,...].reshape(self._num_points).T, 
                'z': heightmap[...,0].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_color(self, colormap, **kwargs):
        if not len(colormap):
            return
            
        colormap = imgtools.stack_image_dim(colormap)

        self._height.update({
                'red': colormap[:,:,0].reshape(self._num_points).T, 
                'green': colormap[:,:,1].reshape(self._num_points).T, 
                'blue': colormap[:,:,2].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_intensity(self, intensitymap, **kwargs):
        if not len(intensitymap):
            return

        intensitymap = imgtools.stack_image_dim(intensitymap)
        
        self._height.update({
                'intensity': intensitymap[ :, :, 1].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_param_normal(self, radius="AUTO", model="TRI"):
        self._param_normal_radius = radius
        self._param_normal_model = model

        self.set_param_format()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_param_format(self):
        self._param_format = {
            "obj": { "path": self._path}, 
            "normal": { 
                "radius": self._param_normal_radius, 
                "model": self._param_normal_model
                }
            }
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_level(self, level = 0):
        for idx in range(level, len(self._stock)):
            self._stock[idx] = 0

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_level(self, level):
        level=0
        if level=="normal":
            level = 1
        elif level=="mesh":
            level = 2
        return level

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_pointcloud(self, maps, **kwargs):
        self.add_height(maps[0], **kwargs)
        self.add_color(maps[1], **kwargs)
        self.add_intensity(maps[2], **kwargs)

        self.write()
        self._stock[0] = True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_normal(self, maps, **kwargs):
        if not self._stock[0]: self.set_pointcloud(maps, **kwargs)
        self._opener("editor", *self.get_normal_cmd(), wait=True)
        self._stock[1] = True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_mesh(self, maps, **kwargs):
        if not self._stock[1]: self.set_pointcloud(maps, **kwargs)
        self._opener("editor", *self.get_mesh_cmd(), wait=True)
        self._stock[2] = True

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def read(self, level=None):
        imgio.show_read_str(self._path, logger=self._logger)
        data = ply.read_ply(self._path)
        return data[level] if level else data

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write(self):
        points = pandas.DataFrame(self._height, index=range(self._num_points))
        imgio.show_write_str(self._path, logger=self._logger)
        ply.write_ply(self._path, points=points)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open(self, level, maps, opener="viewer", **kwargs):
        method = getattr(self, "set_{}".format(level), lambda: "Invalid method")
        method(maps, **kwargs)
        self._opener(opener, self._path)

    #   method --------------------------------------------------------------
    # ----------------------------------------------------------------------- 
    def get_normal_cmd(self):
        return (self.format_cmd(self._param["general"]), self.format_cmd(self._param["normal"]), self.format_cmd(self._param["save-pcl"])) 

    #   method --------------------------------------------------------------
    # ----------------------------------------------------------------------- 
    def get_mesh_cmd(self):
        return (self.format_cmd(self._param["general"]), self.format_cmd(self._param["mesh"]), self.format_cmd(self._param["save-mesh"])) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def format_cmd(self, args):
        return [arg.format(**self._param_format) for arg in args]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_normal_img(self, heightmap, log=False, **kwargs):
        self.set_normal([heightmap, [], []], **kwargs)
        normals = self.read(level="points")["nz"].to_numpy().reshape(self._shape)

        self._logger(get_array_info(normals))

        if log:
            normals = normals*(-1.)+1.
            normals = -np.log(np.where(normals>0., normals, np.min(normals[normals>0.])))

        normals = imgtools.project_data_to_img(normals, dtype=np.uint8, factor=255)
        return normals