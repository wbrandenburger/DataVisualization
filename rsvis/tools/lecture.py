# ===========================================================================
#   lecture.py --------------------------------------------------------------
# ===========================================================================

import rsvis.tools.rsshow
import rsvis.tools.imagestats
import cv2
import numpy as np
import rsvis.tools.welford
import timeit
import tifffile
import matplotlib.pyplot as plt

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def test(files, types, cat=dict(), resize=100):
    img_load = lambda index: [get_image(f, t, cat, resize=resize) for f, t in zip(files[index], types)]
    
    

    # foo = rsvis.tools.imagestats.ImageStats(cat.values(), 8 ) 
    for i in range(2,3):
        img_list = img_load(i)
    #     foo(img_list[types.index("msi")], img_list[types.index("label")]) 
    #     print(foo)

    # path = foo.write()
    # print(path)

    foo = rsvis.tools.imagestats.ImageStats(
            path="A:\\VirtualEnv\\dev-rsvis\\src\\rsvis\\temp\\tmpchlgw4dk.json" 
        )
    # foo.plot_stats(2)
    img = img_list[types.index("msi")]
    a = foo.get_probability(img[50,30,:])
    print(a)
    
def get_image(img_path, img_type, cat, resize=100):
    
    img = tifffile.imread(img_path)

    scale_percent = resize
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height) 
    img = cv2.resize(img, dim,  interpolation=cv2.INTER_NEAREST)

    img = np.expand_dims(img, axis=2) if len(img.shape) != 3 else img 

    if img_type == "label":
        img = rsvis.tools.rsshow.label_to_scalar(img, cat)
    if img_type == "msi":
        img = img.astype(float)
        min_max_img = (np.min(img), np.max(img))
        img = (img - min_max_img[0])/(min_max_img[1] - min_max_img[0]) * 255
        img = img.astype("uint8")

    return img