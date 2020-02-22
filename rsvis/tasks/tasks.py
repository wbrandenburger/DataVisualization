# ===========================================================================
#   test.py -----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.__init__
import rsvis.config.settings
import rsvis.utils.format
import rsvis.tools.rsshow
import rsvis.tools.lecture

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_default():
    task_print_user_settings()

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
get_value = lambda obj, key, default: obj[key] if key in obj.keys() else default

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_rsshow():
    rsvis.tools.rsshow.rsshow(
        rsvis.config.settings._DATA, 
        rsvis.config.settings._SETTINGS["data-tensor-types"],
        **rsvis.config.settings._SETTINGS["output"],
        labels=get_value(rsvis.config.settings._SETTINGS,"label", dict()),
        msi=get_value(rsvis.config.settings._SETTINGS,"msi", list()),
        resize=get_value(rsvis.config.settings._SETTINGS,"resize", 100)
    )

# #   function ----------------------------------------------------------------
# # ---------------------------------------------------------------------------
# def task_test_code():
#     rsvis.tools.rsshow.test_code( rsvis.config.settings._DATA, 
#         rsvis.config.settings._SETTINGS["data-tensor-types"])

#     print("Test to_list():")
#     a, b, c = to_list("hallo", None, ["hallo", "du"])
#     print(a, b, c)

#     import rsvis.tools.objcontainer    
#     a = rsvis.tools.objcontainer.ObjContainer(np.ones((2,3)))
#     print(a)

#     b = rsvis.tools.objcontainer.ObjContainer(None)
#     print(b)

#     b.obj = np.ones((2,3))
#     print(b)

#     import rsvis.tools.imgcontainer
#     c = rsvis.tools.imgcontainer.ImgContainer( path="A:\\Datasets\\Data-Fusion-Contest-2019\\Train-Track1-RGB\\Track1-RGB\\JAX_004_006_RGB.tif")
#     print(c.load())
#     print(c)

#     import rsvis.tools.imgcontainer
#     d= list()
#     for f_set in files:
#         e = rsvis.tools.imgcontainer.ImgListContainer()
#         for f,t  in zip(f_set,types):
#             e.append(path = f, spec=t)
#         d.append(e)

#     import rsvis.tools.index
#     f = rsvis.tools.index.Index(7,3)
#     print(f)
#     f += 1
#     f -= 1
#     f = f + 2
#     print(f)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_test_lecture():
    rsvis.tools.lecture.test(
        rsvis.config.settings._DATA, 
        rsvis.config.settings._SETTINGS["data-tensor-types"], 
        cat=rsvis.config.settings._SETTINGS["label"],
        resize=get_value(rsvis.config.settings._SETTINGS,"resize", 100)
    )
    
#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_settings():
    """Print the user settings"""
    
    # print user's defined settings
    rsvis.__init__._logger.info("Print user's defined settings")
    rsvis.utils.format.print_data(rsvis.config.settings._SETTINGS)

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def task_print_user_data():
    """Print the user data"""
    
    # print user's defined data
    rsvis.__init__._logger.info("Print user's defined data")
    rsvis.utils.format.print_data(rsvis.config.settings._DATA)