# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.tools.rsshowui
import rsvis.tools.options
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
        param_msi=list(), 
        param_dist=dict(), # param?
        param_show=dict(),
        param_classes=list(),
        param_cloud=dict(),
        param_obj=dict()
    ):
        
    _logger.debug("Start training multi task classification and regression model with settings:\nparam_specs:\t{}\nparam_io:\t{}\nparam_log:\t{}\nparam_msi:\t{}\nparam_dist:\t{}\nparam_classes:\t{}\nparam_show:\t{}\nparam_cloud:\t{}\nparam_obj:\t{}".format(param_specs, param_io, param_log, param_msi, param_classes, param_dist, param_show, param_cloud, param_obj))

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = dict((str(c["label"][0]), c["label"][1]) for c in param_classes)
    img_in, img_out, _ , get_path = rsvis.utils.imgio.get_data(files, param_specs, param_io, param_log=param_log, param_label=param_label, param_show=param_show)

    

    ui = rsvis.tools.rsshowui.RSShowUI(
        img_in, 
        img_out, 
        options=rsvis.tools.options.get_options(
            param_specs, param_label=param_label, param_cloud=param_cloud
        ), 
        classes=param_classes,
        objects=param_obj,
        logger=_logger,
        **param_show)

    ui.imshow(wait=True)