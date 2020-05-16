# ===========================================================================
#   heightmap.py ------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils import imgio, imgtools, opener, ply

import numpy as np
import pandas
import tempfile

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class Height():

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, param, dtype=np.float32, show=False, logger=None):

        self._param = param
        
        self._height= dict()
        self._num_points = None

        self._path = tempfile.mkstemp(prefix="shdw-", suffix=".ply")[1]

        self._logger = logger
        
        self._opener = opener.Opener(self._param["opener"], logger=self._logger)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_height(self, heightmap, dtype=np.float32, show=False):
        if not len(heightmap):
            return

        self._num_points = heightmap.shape[0]*heightmap.shape[1]
        heightmap = imgtools.expand_image_dim(heightmap.astype(dtype))

        if show:
            heightmap = heightmap - np.min(heightmap)
            height_factor = float(np.max(heightmap))/(float(np.max([heightmap.shape[0], heightmap.shape[1]])) / 6.0)
            heightmap = heightmap/height_factor

        grid = np.indices((heightmap.shape[0], heightmap.shape[1]), dtype=dtype)

        self._height.update( {
                'x': grid[0,...].reshape(self._num_points).T, 
                'y': grid[1,...].reshape(self._num_points).T, 
                'z': heightmap[...,0].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_color(self, colormap):
        if not len(colormap):
            return
            
        colormap= imgtools.stack_image_dim(colormap)

        self._height.update({
                'red': colormap[:,:,0].reshape(self._num_points).T, 
                'green': colormap[:,:,1].reshape(self._num_points).T, 
                'blue': colormap[:,:,2].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def add_intensity(self, intensitymap):
        if not len(intensitymap):
            return

        intensitymap = imgtools.stack_image_dim(intensitymap)
        
        self._height.update({
                'intensity': intensitymap[ :, :, 1].reshape(self._num_points).T
            }
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def read(self):
        imgio.show_read_str(self._path, logger=self._logger)
        return ply.read_ply(self._path)["points"]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write(self):
        points = pandas.DataFrame(self._height, index=range(self._num_points))
        imgio.show_write_str(self._path, logger=self._logger)
        ply.write_ply(self._path, points=points)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def open(self, maps, opener="viewer"):
        self.add_height(maps[0])
        self.add_color(maps[1])
        self.add_intensity(maps[2])

        self.write()
        self._opener(opener, path=self._path)