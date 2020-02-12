# ===========================================================================
#   pctools.py --------------------------------------------------------------
# ===========================================================================


import rsvis.utils.ply
import tempfile
import subprocess
import pandas


def get_pointcloud(image, height):
    print("Arschloch")
#     img = cv2.resize(image, (256, 256), interpolation = cv2.INTER_LINEAR).astype("uint8")
#     height = cv2.resize(height, (256, 256), interpolation = cv2.INTER_LINEAR).astype(float)/8
#     grid = np.indices((256, 256))
#     img_dict = np.concatenate((
#         grid[0,:,:].reshape((256*256,1)), 
#         grid[1,:,:].reshape((256*256,1)), 
#         height.reshape((256*256,1)), 
#         img[:,:,0].reshape((256*256,1)), 
#         img[:,:,1].reshape((256*256,1)), 
#         img[:,:,2].reshape((256*256,1))
#         ), axis=1)
#     # img_dict = {
#     #     'x':     [grid[0,:,:].reshape((256*256,1)).astype(float)],
#     #     'y':     [grid[1,:,:].reshape((256*256,1)).astype(float)],
#     #     'z':     [height.reshape((256*256,1)).astype(float)], 
#     #     'red':   [img[:,:,0].reshape((256*256,1))], 
#     #     'green': [img[:,:,1].reshape((256*256,1))], 
#     #     'blue':  [img[:,:,2].reshape((256*256,1))]
#     # }
#     data = pandas.DataFrame(img_dict)
#     tmp = tempfile.mkstemp(suffix=".ply")
#     # data  = pandas.DataFrame(img_list, columns=['x', 'y', 'z', 'red', 'green', 'blue'])

#     rsvis.__init__._logger.debug("Write {0}".format(tmp[1]))
#     rsvis.utils.ply.write_ply(tmp[1], points=data, mesh=None, as_text=True)
#     subprocess.Popen(['C:\\Program Files\\ccViewer\\ccViewer.exe', tmp[1]])
#     return image
