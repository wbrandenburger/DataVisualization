# ===========================================================================
#   heightmap.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
from rsvis.utils import imgio, imgtools, opener, ply
import rsvis.utils.logger

import cv2
import numpy as np
import pandas
import tempfile

#   method --------------------------------------------------------------
# -----------------------------------------------------------------------
def get_array_info(height, verbose=False):
    return "[PCL] Shape: {}, Type: {}, Range: {:.3f}, {:.3f}, {:.3f}".format(height.shape, height.dtype, np.min(height), np.max(height), np.mean(height))

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Height():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, param, logger=None):
        self._height= dict()
        self._num_points = None
        self._shape = list()

        io = gu.PathCreator(**gu.get_value(param, "temp", dict()))
        self._path = io(tempfile.mkstemp(prefix="shdw-", suffix=".ply")[1])
        
        self._param = param["process"]
        self.set_param_normal()

        self._logger = rsvis.utils.logger.Logger(logger=logger)
        self._opener = opener.Opener(param["opener"], logger=self._logger)

        self._stock = [0] * 3

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_height(self, heightmap, factor=1.0, show=False, **kwargs):
        if not len(heightmap):
            return

        self._num_points = heightmap.shape[0]*heightmap.shape[1]
        self._shape = heightmap.shape[0:2]
        heightmap = imgtools.expand_image_dim(heightmap.astype(np.float32))

        if show:
            heightmap = imgtools.project_data_to_img(heightmap, dtype=np.float32, factor=1.0)*150/np.float32(factor)

        grid = np.indices((self._shape), dtype=np.float32)

        self._height.update( {
                "x": grid[0,...].reshape(self._num_points).T, 
                "y": grid[1,...].reshape(self._num_points).T, 
                "z": heightmap[...,0].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_height(self):
        self._height.pop("x", None)
        self._height.pop("y", None)
        self._height.pop("z", None)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_color(self, colormap, **kwargs):
        if not len(colormap):
            return
            
        colormap = imgtools.stack_image_dim(colormap)

        self._height.update({
                "red": colormap[:,:,0].reshape(self._num_points).T, 
                "green": colormap[:,:,1].reshape(self._num_points).T, 
                "blue": colormap[:,:,2].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_color(self):
        self._height.pop("red", None)
        self._height.pop("green", None)
        self._height.pop("blue", None)

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
    def remove_intensity(self):
        self._height.pop("intensity", None)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_param_normal(self, radius="AUTO", model="TRI", **kwargs):
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
    def remove_normal(self):
        self._height.pop("nx", None)
        self._height.pop("ny", None)
        self._height.pop("nz", None)

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
        method(maps, show=True, **kwargs)
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
    def get_rough_img(self, rough=3, **kwargs):
        pass
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_normal_img(self, heightmap, bins=None, log=True, ntype="z",**kwargs):
        self.set_normal([heightmap, [], []], **kwargs)

        # print(self.read(level="points"))
        if ntype=="z":
            scalar= "nz"
            limits = [.0, 1.]
        else:
            scalar = "scalar_Dip_direction_(degrees)"
            log = 0
            limits = list()
        

        normalimg = self.read(level="points")[scalar].to_numpy().reshape(self._shape)

        self._logger(get_array_info(normalimg))
        
        normalimg = imgtools.project_data_to_img(normalimg)
        

        if log:
            normalimg = normalimg*(-1.)+1.
            normalimg = -np.log(np.where(normalimg>0., normalimg, np.min(normalimg[normalimg>0.])))
            limits = [.0, 10.]

        normalimg = imgtools.project_data_to_img(normalimg, limits=limits)
        if bins is not None:
            normalimg_binned = np.zeros(normalimg.shape, dtype=np.float32)
            array = list(np.arange(1.0/bins, 1., 1.0/bins))
            limit = 0.        
            for i in array:
                normalimg_binned += np.where(np.logical_and(normalimg>limit, normalimg<=i), limit, 0.)
                limit = i
            normalimg = normalimg_binned + np.where(normalimg>limit, limit, 0.)

        return normalimg

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_normal(self, heightmap, log=False, opener="viewer", **kwargs):
        self.set_normal([heightmap, [], []], **kwargs)
        normals = self.read(level="points")
        
        normals_x = normals["nx"].to_numpy().reshape(self._shape)
        normals_y = normals["ny"].to_numpy().reshape(self._shape)
        normals_z = normals["nz"].to_numpy().reshape(self._shape)
        
        self._logger(get_array_info(normals_x))
        self._logger(get_array_info(normals_y))
        self._logger(get_array_info(normals_z))

        # normals_x = normals_x*(-1.)+1.

        normals_x = imgtools.project_data_to_img(normals_x, limits=[-1., 1.])*(-1.0)+1
        normals_y = imgtools.project_data_to_img(normals_y, limits=[-1., 1.])*(-1.0)+1
        
        normals_z = normals_z*(-1.)+1.
        normals_z = -np.log(np.where(normals_z>0., normals_z, np.min(normals_z[normals_z>0.])))
        self._logger(get_array_info(normals_z))
        print(get_array_info(normals_z))
        normals_z = imgtools.project_data_to_img(normals_z, limits=[np.mean(normals_z)-np.std(normals_z), np.mean(normals_z)+np.std(normals_z)])

       # normals_z = np.zeros(self._shape, dtype=np.float32)+1

        self._logger(get_array_info(normals_x))
        self._logger(get_array_info(normals_y))
        self._logger(get_array_info(normals_z))

        self.add_height(heightmap, show=True)
        self.add_color(np.stack([normals_x, normals_y, normals_z], axis=2))
        self.remove_normal()

        self.write()
        self._opener(opener, self._path)
   