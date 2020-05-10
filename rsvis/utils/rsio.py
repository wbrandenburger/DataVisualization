# ===========================================================================
#   rsio.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.utils.general as gu

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSIO(object):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self,
            param_in,
            param_out,
            param_show,
            logger = None,
            **kwargs
        ):

        self._param_in = param_in
        self._param_out = param_out
        self._param_show = param_show
        
        self._io = gu.PathCreator(**self._param_in["image"])

        self._logger = logger

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def logger(self, log_str, stream="info"):
        if self._logger is None:
            return

        if stream == "info":
            self._logger.info(log_str)
        elif stream == "debug":
            self._logger.debug(log_str)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_files_in(self, spec):
    #     return lambda path, io=self._io, param_in=self._param_in, **kwargs : io(path, **param_in[spec], **kwargs)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_files_out(self, spec):
    #     return lambda path, io=self._io, param_out=self._param_out, **kwargs : io(path, **param_out[spec], **kwargs)

    # save the image in another location (param_io as well as only path wit PathCreator)
    
    # copy the image in another location (param_io as well as only path wit PathCreator)

    # log file which ist derived from an single image name (image or height or ...)
    # object file which is derived from a singel instance (image and height and)

    # each object need a own specification (original image name, pixel bounding box ...)

    # each input (object because of scale, log and so on) need a own imgio function, for example scaling

    # each of all need path creator which looks for the xreation of folders and regex
    
    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def funcname(self, parameter_list):
    #     raise NotImplementedError