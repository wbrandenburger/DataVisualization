# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.__init__ import _logger
import rsvis.config.settings
import rsvis.utils.format
import rsvis.tools.rsshow

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    """Default task of set 'test'"""
    _logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow(setting="training"):
    task_rsshow("test")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_test_code():
    import rsvis.utils.objcontainer 
    import rsvis.utils.imgcontainer
    import rsvis.utils.index

    import numpy as np

    files = rsvis.config.settings._DATA, 
    types = rsvis.config.settings._SETTINGS["param_specs"]

    a = rsvis.utils.objcontainer.ObjContainer(np.ones((2,3)))
    print(a)

    b = rsvis.utils.objcontainer.ObjContainer(None)
    print(b)

    b.obj = np.ones((2,3))
    print(b)

    c = rsvis.utils.imgcontainer.ImgContainer( path="A:\\Datasets\\Data-Fusion-Contest-2019\\Train-Track1-RGB\\Track1-RGB\\JAX_004_006_RGB.tif")
    print(c.load())
    print(c)

    d= list()
    for f_set in files:
        e = rsvis.utils.imgcontainer.ImgListContainer()
        for f,t  in zip(f_set,types):
            e.append(path = f, spec=t)
        d.append(e)

    f = rsvis.utils.index.Index(7,3)
    print(f)
    f += 1
    f -= 1
    f = f + 2
    print(f)