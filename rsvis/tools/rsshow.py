# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.tools.rsshowui
import rsvis.tools.keys
from rsvis.utils import imgtools
import rsvis.utils.imgio
import rsvis.utils.objindex

import numpy as np

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(
        files, 
        specs, 
        param_io,
        param_log=dict(),
        param_label=dict(), 
        param_msi=list(), 
        param_dist=dict(),
        param_show=dict()
    ):
        
    _logger.debug("Start training multi task classification and regression model with settings:\nparam_io:\t{}\nparam_log:\t{}\nparam_label:\t{}\nparam_msi:\t{}\nparam_dist:\t{}\nparam_show:\t{}".format(param_io, param_log, param_label, param_msi, param_dist, param_show))

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    img_in, img_out, _ , get_path = rsvis.utils.imgio.get_data(files, specs, param_io, param_log=param_log, param_label=param_label, param_show=param_show)
    
    img_cpy = lambda path: rsvis.utils.imgio.copy_image(path, get_path(path))
    label_index = rsvis.utils.objindex.ObjIndex(imgtools.project_dict_to_img(param_label.copy(), dtype=np.uint8, factor=255))

    keys = rsvis.tools.keys.get_keys(label_index, img_out, img_cpy, param_dist, param_msi)

    ui = rsvis.tools.rsshowui.RSShowUI(img_in, keys=keys)
    ui.imshow(wait=True)