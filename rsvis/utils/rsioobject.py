# ===========================================================================
#   rsio.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.utils.imgcontainer
import rsvis.utils.imgio 
import rsvis.utils.general as gu
import rsvis.utils.rsioimage

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSIOObject(rsvis.utils.rsioimage.RSIOImage):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self,
            *args,
            **kwargs
        ):
        super(RSIOObject, self).__init__(*args, **kwargs)

        self._param_obj_in = gu.get_value(self._param_in, "object", dict())
        self._param_obj_out = gu.get_value(self._param_out, "object", dict())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object_in(self, path, default=list(), **kwargs):
        if self._param_obj_in:
            return rsvis.utils.imgio.get_object(
                self._io(path, **self._param_obj_in, **kwargs), 
                default=default, 
                logger=self._logger, 
                **self._param_show
            )
        return default

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_object_in(self, path, obj, **kwargs):
        if self._param_obj_in:
            rsvis.utils.imgio.set_object(
                self._io(path, **self._param_obj_in, **kwargs), 
                obj,
                logger=self._logger,
                **self._param_show
            )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_files_out(self, path, obj, **kwargs):
        if self._param_obj_out:
            rsvis.utils.imgio.write_object(
                self._io(path, **self._param_obj_out, **kwargs), 
                obj,
                logger=self._logger
            )