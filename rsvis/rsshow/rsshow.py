# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
from rsvis.utils import imgtools
from rsvis.utils import imgio
import rsvis.utils.rsioimage
import rsvis.utils.rsioobject
import rsvis.utils.objindex

import rsvis.tools.options
import rsvis.tools.rsshowui

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def run(
        files, 
        param_specs, 
        param_in,
        param_out=dict(),
        param_classes=list(),
        param_cloud=dict(),
        param_show=dict()
    ):
        
    _logger.debug("Start training multi task classification and regression model with settings:\nparam_specs:\t{}\nparam_in:\t{}\nparam_out:\t{}\nparam_classes:\t{}\nparam_cloud:\t{}\nparam_show:\t{}".format(param_specs, param_in, param_out, param_classes, param_cloud, param_show))

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = [c["label"] for c in param_classes]
    param_color = [c["color"] for c in param_classes]
    rsio = rsvis.utils.rsioobject.RSIOObject(files, param_specs, param_in, param_out, param_show, label=param_label, color=param_color
    )

    ui = rsvis.tools.rsshowui.RSShowUI(
        rsio,
        options = rsvis.tools.options.get_options(
            param_specs, param_cloud=param_cloud
        ), 
        classes = param_classes,
        objects = rsio,
        logger=_logger,
        show=param_show
    )

    ui.imshow(wait=True)