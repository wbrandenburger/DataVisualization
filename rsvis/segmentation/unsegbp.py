# ===========================================================================
#   unsegbp.py --------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.utils.time import MTime
from rsvis.segmentation.torchnet import TorchNet1, TorchNet2, TorchNet3, TorchNet
from rsvis.tools.topwindow import tw

import cv2
import math
import numpy as np
from skimage import segmentation, color
from sklearn.preprocessing import normalize
import torch

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def unsegbp(parent, img, img_list, logger, dim1=32, dim2=64, min_label=4, max_label=256, iterCount=64, factor=1, net=1, height=False, segments="xx"):

    #   settings ------------------------------------------------------------
    mtime = MTime(number=iterCount)

    seg_out_color = img.copy()

    img_list_cv = np.hstack(
        (cv2.cvtColor(img_list[0], cv2.COLOR_BGR2RGB),  
        cv2.cvtColor(img_list[2], cv2.COLOR_BGR2RGB))
    )

    #   training initialization ---------------------------------------------
    np.random.seed(1943)

    device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
    img_tensor = img.astype(np.float32) / 255.
    # print(height)
    # if height:
    #     height_tensor = img_list[3] / np.linalg.norm(img_list[3])
    #     tensor = np.concatenate([img_tensor, height_tensor], axis=2)
    #     inp_dim = 3
    #     height_tensor = img_list[3] / np.linalg.norm(img_list[3])
    #     height_tensor = np.stack([height_tensor]*3, axis=2)
    #     tensor = np.concatenate([img_tensor, height_tensor], axis=2)
    #     inp_dim = 4
    # else:
    tensor = img_tensor
    inp_dim = 3

    tensor = tensor.transpose((2, 0, 1)) # (depth, height, width) and values in [0., 1.]
    tensor = tensor[np.newaxis, :, :, :]
    tensor = torch.from_numpy(tensor).to(device)

    if net==1:
        model = TorchNet1(inp_dim=inp_dim, mod_dim1=dim1, mod_dim2=dim2).to(device)
    elif net==2:
        model = TorchNet2(inp_dim=inp_dim, mod_dim1=dim1, mod_dim2=dim2).to(device)
    elif net==3:
        model = TorchNet3(inp_dim=inp_dim, mod_dim1=dim1, mod_dim2=dim2).to(device)

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-1, momentum=0.9) # lr=5e-2
    # optimizer = torch.optim.RMSprop(model.parameters(), lr=1e-1, momentum=0.0)

    #   segmentation results ------------------------------------------------
    # seg_map: binary image with shape (height, width) similar to image and values in [1, K], with K number of clusters 
    seg_map = img_list[1].flatten() # vector with shape (height*width,)
    seg_label = [np.where(seg_map == label)[0] for label in np.unique(seg_map)] # list with vectors of pixel indices of one cluster, sum(seg_label.shape[0]) = height*width

    color_avg = np.random.randint(255, size=(max_label, 3)) # integer values in [0, 255] and size (maximum number of allowed clusters, 3)

    # open a topwindow with the segmentation results of the currently displayed image      
    # img_list_tw = tw.TopWindow(parent, title="Segmentation", dtype="img", value=img_list)
    #   training ------------------------------------------------------------
    model.train()
    for batch_idx, mt in zip(range(iterCount), mtime):
            
        #   forward propagation ---------------------------------------------
        optimizer.zero_grad()
        output = model(tensor)[0]
        output = output.permute(1, 2, 0).view(-1, dim2)
        print(output.shape)  
        target = torch.argmax(output, 1)
        seg_out = target.data.cpu().numpy() # vector with shape (height*width,) values in [0, new number of clusters]

        #   refinement ------------------------------------------------------
        # constraint on spatial continuity
        # additional constraint that favors cluster labels that are the same as those of neighboring pixels
        # force all all of the pixels in each superpixel to have the same label
        seg_out_refined = seg_out.copy()
        for idx_seg in seg_label:
            label, hist = np.unique(seg_out_refined[idx_seg], return_counts=True)
            # idx_seg: pixel indices of one cluster
            # seg_out[idx_seg]: new cluster indices of each pixel in one cluster of inital segmentation results
            # label: unique cluster indices of seg_out[idx_seg]
            # hist: list with number of pixels with a certain value
            seg_out_refined[idx_seg] = label[np.argmax(hist)] # label with maximum number of pixels having the same label

        #   backward propagation --------------------------------------------
        target = torch.from_numpy(seg_out_refined)
        target = target.to(device)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        mt.stop()

        #   visualization ---------------------------------------------------
        clusters, hist = np.unique(seg_out, return_counts=True)
        num_clusters = len(clusters)

        seg_out = seg_out.reshape(img.shape[:2])
        seg_out_refined = seg_out_refined.reshape(img.shape[:2])
        
        # seg_out = cv2.resize(seg_out, (img.shape[1], img.shape[0]), dst=cv2.CV_32SC1, interpolation=cv2.INTER_NEAREST)
        # seg_out_refined = cv2.resize(seg_out_refined, (img.shape[1], img.shape[0]), dst=cv2.CV_32SC1, interpolation=cv2.INTER_NEAREST)
        
        seg_out_color = color.label2rgb(seg_out, img_list[0], kind='avg', bg_label=0)
        seg_out_color_refined = color.label2rgb(seg_out_refined, img_list[0], kind='avg', bg_label=0)
    
        # seg_map_bound = segmentation.mark_boundaries(img, seg_out)
        # seg_out = seg_out.reshape((95,97))
        # img_out = cv2.resize(img, (seg_out.shape[1], seg_out.shape[0]), dst=cv2.CV_8UC3, interpolation=cv2.INTER_LINEAR)
        # seg_out_color = color.label2rgb(seg_out, cv2.cvtColor(img_out, cv2.COLOR_BGR2RGB), kind='avg')

        img_list_out = np.hstack((
            cv2.cvtColor(seg_out_color, cv2.COLOR_BGR2RGB), 
            cv2.cvtColor(seg_out_color_refined, cv2.COLOR_BGR2RGB)
        ))
        cv2.imshow("seg_pt", np.vstack((img_list_cv, img_list_out )))
        cv2.waitKey(1)

        # print('Loss:', batch_idx, loss.item(), mt.overall)
        print("{}, [LOSS]: {}, [NUMBER-CLUSTER]: {}".format(mt.overall(), loss.item(), num_clusters))

        if num_clusters < min_label:
            break

    # '''save'''
    # time0 = time.time() - start_time0
    # time1 = time.time() - start_time1
    # print('PyTorchInit: %.2f\nTimeUsed: %.2f' % (time0, time1))
    # img_list_tw.update(seg_out_color, index=2)
    cv2.destroyAllWindows()
    img_list= [img_list[0], img_list[2], seg_out_color]
    for idx, imgs in enumerate(img_list):
        cv2.imwrite("A:\\Temp\\rsvis\\seg_{}_{}_{}_{}_{}_{}.png".format(factor, iterCount, segments, dim1, dim2, idx), imgs)
    tw.TopWindow(parent, title="Segmentation", dtype="img", value=img_list)

