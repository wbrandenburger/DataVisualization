# ===========================================================================
#   tools.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from io import BytesIO
from scipy import ndimage

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def get_histogram(img,alpha=0.7):    
    fig = plt.figure(dpi=64)
    color = ('b','g','r')
    # computation of the histogram for each channel
    for channel, col in enumerate(color):
        histr = cv2.calcHist([img], [channel], None, [256], [0,256])
        plt.plot(histr, color = col)
        plt.xlim([0,256])

    plt.title('Histogram for color scale picture')

    # save the figure as image object and read it as numpy array
    png1 = BytesIO()
    fig.savefig(png1, format='png')
    hist = np.asarray(Image.open(png1))
    png1.close()
    plt.close()
    
    return hist
