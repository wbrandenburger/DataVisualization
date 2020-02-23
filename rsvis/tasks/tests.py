# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.utils.format
import rsvis.tools.rsshow

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    rsvis.__init__._logger.warning("No task chosen from set 'tests'")

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_test_code():
    import rsvis.tools.objcontainer 
    import rsvis.tools.imgcontainer
    import rsvis.tools.index

    import numpy as np

    files = rsvis.config.settings._DATA, 
    types = rsvis.config.settings._SETTINGS["data-tensor-types"]

    a = rsvis.tools.objcontainer.ObjContainer(np.ones((2,3)))
    print(a)

    b = rsvis.tools.objcontainer.ObjContainer(None)
    print(b)

    b.obj = np.ones((2,3))
    print(b)

    c = rsvis.tools.imgcontainer.ImgContainer( path="A:\\Datasets\\Data-Fusion-Contest-2019\\Train-Track1-RGB\\Track1-RGB\\JAX_004_006_RGB.tif")
    print(c.load())
    print(c)

    d= list()
    for f_set in files:
        e = rsvis.tools.imgcontainer.ImgListContainer()
        for f,t  in zip(f_set,types):
            e.append(path = f, spec=t)
        d.append(e)

    f = rsvis.tools.index.Index(7,3)
    print(f)
    f += 1
    f -= 1
    f = f + 2
    print(f)