# ===========================================================================
#   rsshow.py ---------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.rsioobject
import rsvis.utils.logger

import rsvis.tools.options
import rsvis.tools.rsshowui

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def run(
        files, 
        label, 
        param_in,
        param_out=dict(),
        param_classes=list(),
        param_cloud=dict(),
        param_vis=dict(),
        param_obj=dict(),
        param_show=dict()
    ):

    rsvis.utils.logger.Logger().get_logformat("Start RSVis with the following parameters:", param_label=label, param_in=param_in, param_out=param_out, param_classes=param_classes, param_cloud=param_cloud, param_vis=param_vis, param_obj=param_obj, param_show=param_show)

    #   settings ------------------------------------------------------------
    # -----------------------------------------------------------------------
    param_label = [c["label"] for c in param_classes if "label" in c]
    param_color = [c["color"] for c in param_classes if "label" in c]
    rsio = rsvis.utils.rsioobject.RSIOObject(files, label, param_in, param_out, param_show, label=param_label, color=param_color
    )

    ui = rsvis.tools.rsshowui.RSShowUI(
        rsio,
        options = rsvis.tools.options.get_options(
            param_label, param_cloud=param_cloud
        ), 
        classes = param_classes,
        objects = rsio,
        param={"cloud": param_cloud, "vis": param_vis},
        obj=param_obj,
        show=param_show
    )

    ui.imshow(wait=True)
