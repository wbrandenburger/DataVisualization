# ===========================================================================
#   rsio.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.utils.general as gu
import rsvis.utils.imgcontainer
from rsvis.utils import imgio 
import rsvis.utils.rsio

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSIOImage(rsvis.utils.rsio.RSIO):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
            self,
            images, 
            specs,
            *args,
            label = list(),
            color = list(),
            **kwargs
        ):
        super(RSIOImage, self).__init__(*args, **kwargs)

        self._images = images
        self._specs = specs
        self._label = label
        self._color = color

        self._img_name = "image"

        self._log_io = gu.PathCreator(**gu.get_value(self._param_in, "log", dict()))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_load_img(self):
        return lambda path, spec: imgio.get_image(
            path,
            spec,
            self._label,
            color=self._color,
            logger=self._logger,
            **self._param_show
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_in(self):
        img_in = list()
        for images in self._images:
            img_list_container = rsvis.utils.imgcontainer.ImgListContainer(
                load=self.get_load_img()
            )

            specs = self._specs if len(self._specs) == len(images) else ["{}-{}".format(self._specs[0], idx) for idx in range(len(images))]
            
            for idx, img in enumerate(images):
                img_list_container.append(
                    path=img, 
                    spec=specs[idx], 
                    **self._param_show
                )

            img_in.append(img_list_container)

        return img_in

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_out(self):
        return lambda path, img, logger=self._logger, **kwargs: imgio.write_image(
            self._io(path, **self._param_out[self._img_name], **kwargs), 
            img,
            logger=self._logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log_path(self, path):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log_in(self, path, default="", **kwargs):
        if self._log_io:
            return imgio.get_log(
                self._log_io(path, **kwargs), 
                default="", 
                logger=self._logger
            )
        return default

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log_in(self, path, log, **kwargs):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log_out(self, path, log, **kwargs):
        pass