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
            labels,
            *args,
            label = list(),
            color = list(),
            **kwargs
        ):
        super(RSIOImage, self).__init__(*args, **kwargs)

        self._images = images
        self._labels = labels
        self._label = label
        self._color = color

        self._img_name = "image"
        self._log_name = "log"

        self._param_log = gu.get_value(self._param_in, self._log_name, dict())
        self._log_io = gu.PathCreator(**self._param_log)

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

            labels = self._labels if len(self._labels) == len(images) else ["{}-{}".format(self._labels[0], idx) for idx in range(len(images))]
            
            for idx, img in enumerate(images):
                img_list_container.append(
                    path=img, 
                    label=labels[idx], 
                    **self._param_show
                )

            img_in.append(img_list_container)

        return img_in

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_img_out(self, param_out=None, img_name=None):
        if img_name is None:
            img_name = self._img_name
        if param_out is None:
            param = self._param_out[img_name]
        else:
            param = param_out[img_name]
        return lambda path, img, logger=self._logger, **kwargs: imgio.write_image(
            self._io(path, **gu.update_dict(param, kwargs)), 
            img,
            logger=logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log_path(self, path):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log_in(self, **kwargs):
        return lambda path, logger=self._logger, **kwargs: imgio.get_log(
            self._log_io(path, **gu.update_dict(self._param_in[self._log_name], **kwargs)),
            logger=logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_log(self, **kwargs):
        return lambda path, logger=self._logger, **kwargs: imgio.show_log(
            self._log_io(path, **gu.update_dict(self._param_log, kwargs)),
            logger=logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_log_out(self, **kwargs):
        return lambda path, log, logger=self._logger, **kwargs: imgio.write_log(
            self._log_io(path, **gu.update_dict(self._param_log, kwargs)), 
            log,
            logger=logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_param_out(self, **kwargs):
        a = gu.update_dict(self._param_log, kwargs)
        print(a)
        return lambda path, log, logger=self._logger, **kwargs: imgio.write_yaml(
            self._log_io(path, **gu.update_dict(self._param_log, kwargs)), 
            log,
            logger=logger
        )

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log_in(self, path, log, **kwargs):
        pass

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log_out(self, path, log, **kwargs):
        pass