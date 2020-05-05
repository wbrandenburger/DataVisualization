# ===========================================================================
#   imgcanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

import rsvis.tools.extcanvas
import rsvis.tools.imgconcanvas

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImageCanvas(rsvis.tools.imgconcanvas.ImageContainerCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent, 
        grid=list(), 
        double_button=None, 
        classes=dict(), 
        **kwargs
    ):

        super(ImageCanvas, self).__init__(parent, shift=[4,4], **kwargs)

        self.double_button = double_button if double_button else (lambda x: x)

        self.bind("<Button-1>", self.mouse_button_1_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_1_released)
        self.bind("<ButtonRelease-2>", self.mouse_button_2_released)
        self.bind("<Double-Button-1>", self.mouse_double_1_button)
        self.bind("<B1-Motion>", self.mouse_motion)

        self.mouse_area = list()
        self.mouse_point = list()

        self._area_event = 0

        self._grid_flag = 1
        self._grid = grid if grid else [1, 1]
        
        self._object_flag = 0

        self._selection = dict()
        self._patches_bbox = None
        self._patches_grid = None

        self._boxes = list()                        
        self._color = dict((c["name"], c["color"]) for c in classes)
        self._label = list(self._color.keys())[0] if self._color else None

        self._bbox = [0, 0, 0, 0]

        self._point = [0,0]

        self._mouse_sensitivity = 4

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self, **kwargs):
        super(ImageCanvas, self).clear(**kwargs)
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_bbox(self, boxes, inverted=False):
        scale = [float(s)/i for s, i in zip(self.get_size(), self._img_size)]

        if inverted:
            scale = [1/s for s in scale]

        boxes_resize = list()
        for box in boxes:
            boxes_resize.append([
                int(box[0]*scale[1]), int(box[1]*scale[1]), 
                int(box[2]*scale[0]), int(box[3]*scale[0])])
        return boxes_resize

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_resize = super(ImageCanvas, self).draw_image(**kwargs)
        shape = np.asarray(img_resize).shape

        img = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
        
        self._patches_bbox = rsvis.utils.patches_unordered.UnorderedPatches(np.asarray(img_resize), bbox=self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]))
        
        if self._object_flag:
            img = imgtools.draw_box(img, [], self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]), [self._color[b["label"]] for b in self._boxes if isinstance(b, dict)])            

        self._patches_grid = rsvis.utils.patches_ordered.OrderedPatches(np.asarray(img_resize), num_patches=self._grid, logger=self._logger)

        if self._grid_flag:            
            img = imgtools.get_grid_image(img, [], self._patches_grid.get_bbox())

        if self._selection:
            img = imgtools.draw_box(img, [], self.resize_bbox([self._selection["box"]]), [self._selection["color"]])

        img = Image.fromarray(imgtools.get_transparent_image(img))

        img_label = img_resize.copy()
        img_label.paste(img, (0, 0), img)
        return img_label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def obj(self):
        return self._object_flag

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_img(self, img, objects=list()):
        self._img_size = [img.shape[1], img.shape[0]]
        self._img = Image.fromarray(img)

        self._boxes = objects
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, index=0, **kwargs):
        self._area_event = index
        if self._area_event==1:
            self._object_flag = 0
            self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_grid(self, grid):
        self._grid = grid
        if self._grid_flag: 
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, label):
        self._label = label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_grid(self):
        self._grid_flag = 0 if self._grid_flag else 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_objects(self):
        self._object_flag = 0 if self._object_flag  else 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_objects(self):
        return self._boxes

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_event(self, event):
        ev = [event.y, event.x]

        ev[0] = ev[0] if ev[0] >= 0 else 0 
        ev[0] = ev[0] if ev[0] <= self._img_resize.size[1] else self._img_resize.size[1]
        
        ev[1] = ev[1] if ev[1] >= 0 else 0 
        ev[1] = ev[1] if ev[1] <= self._img_resize.size[0] else self._img_resize.size[0]
        
        return ev

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        self.focus_set()
        self._selection = dict()

        ev = self.resize_event(event)
        self._point = [ev[0], ev[1]]
        if self._area_event==1:
            indices=list()
            self._patches_bbox.get_bbox_from_point(ev, indices=indices)
            
            if len(indices):
                self._selection = {"box": self._boxes[indices[0]]["box"], "color": [150,150,150]}
                
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_motion(self, event):
        self.focus_set()

        ev = self.resize_event(event)
        self._bbox[0] = min([self._point[0], ev[0]])
        self._bbox[1] = max([self._point[0], ev[0]])
        self._bbox[2] = min([self._point[1], ev[1]])
        self._bbox[3] = max([self._point[1], ev[1]])
        self._selection = {"box": self.resize_bbox([self._bbox], inverted=True)[0], "color": [150,150,150]}
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        self.focus_set()
        
        ev = self.resize_event(event)
        self._bbox[0] = min([self._point[0], ev[0]])
        self._bbox[1] = max([self._point[0], ev[0]])
        self._bbox[2] = min([self._point[1], ev[1]])
        self._bbox[3] = max([self._point[1], ev[1]])

        if not (self._bbox[1]-self._bbox[0] > self._mouse_sensitivity and self._bbox[3]-self._bbox[2] > self._mouse_sensitivity):
            return

        if self._area_event==0:
            patch = self._patches_bbox.get_patch(bbox=self._bbox)
            self._selection = {"box": self.resize_bbox([self._bbox], inverted=True)[0], "color": [150,150,150]}
            self.create_image()

            self.double_button(title="Histogram", dtype="img", value=patch, histogram=True)
        elif self._area_event==1:
            self._boxes.append({"box": self.resize_bbox([self._bbox], inverted=True)[0], "label": self._label})
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_2_released(self, event):
        self.focus_set()
        
        ev = self.resize_event(event)

        boxes = None
        if self._area_event==0:
            bbox = self.resize_bbox([self._patches_grid.get_bbox_from_point(ev)], inverted=True)[0]
        elif self._area_event==1:
            boxes = list()
            self._patches_bbox.get_bbox_from_point(ev, boxes=boxes)
    
            if len(boxes):
                bbox = self.resize_bbox(boxes, inverted=True)[0]
            else:
                return

        if bbox:
            img_container = self._img_container.copy()
            img_container.set_bbox(bbox)
            self.double_button(title="Histogram", dtype="img", value=img_container, container=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_1_button(self, event):
        self.focus_set()
        
        ev = self.resize_event(event)

        if self._area_event==0:
            patch = self._patches_grid.get_patch_from_point(ev)
        elif self._area_event==1:
            patches = list()
            self._patches_bbox.get_patch_from_point(ev, patches=patches)
            
            if len(patches):
                patch = patches[0]
            else:
                return

        self.double_button(title="Histogram", dtype="img", value=patch, histogram=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        if self._selection and self._patches_bbox:
            idx = self._patches_bbox.equal(self.resize_bbox([self._selection["box"]])[0])
            if idx is not None: 
                self._boxes.pop(idx)
                self._selection = dict()
            self.create_image()
