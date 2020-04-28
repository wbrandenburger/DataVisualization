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

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def rsshow(
        files, 
        param_specs, 
        param_io,
        param_log=dict(),
        param_label=dict(), 
        param_msi=list(), 
        param_dist=dict(), # param?
        param_show=dict()
    ):
        
    _logger.debug("Start training multi task classification and regression model with settings:\nparam_specs:\t{}\nparam_io:\t{}\nparam_log:\t{}\nparam_label:\t{}\nparam_msi:\t{}\nparam_dist:\t{}\nparam_show:\t{}".format(param_specs, param_io, param_log, param_label, param_msi, param_dist, param_show))

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    img_in, img_out, _ , get_path = rsvis.utils.imgio.get_data(files, param_specs, param_io, param_log=param_log, param_label=param_label, param_show=param_show)
    
    keys, keys_description = rsvis.tools.keys.get_keys(param_specs, img_out, param_label=param_label)

    ui = rsvis.tools.rsshowui.RSShowUI(img_in, keys=keys, description=keys_description, logger=_logger, **param_show)
    ui.imshow(wait=True)