# ===========================================================================
#   canvas_image.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.tools.canvas_resizing
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

import numpy as np
from PIL import Image, ImageTk
from tkinter import Canvas, NW

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class ImageCanvas(rsvis.tools.canvas_resizing.ResizingCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(self, parent, grid=list(), double_button=None, classes=dict(), logger=None, **kwargs):
        super(ImageCanvas, self).__init__(parent, shift=[4,4], **kwargs)

        self.double_button = double_button if double_button else (lambda x: x)

        self.bind("<Button-1>", self.mouse_button_pressed)
        self.bind("<ButtonRelease-1>", self.mouse_button_released)
        self.bind("<Double-Button-1>", self.mouse_double_button)

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
        self._label = self._color[list(self._color.keys())[0]] if self._color else None

        self._bbox = [0]*4

        self._mouse_sensitivity = 4

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def clear(self):
        self._selection = dict()
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def resize_bbox(self, boxes, inverted=False):
        scale = [float(s)/i for s, i in zip(self.get_size(), self.img_size)]

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
    def create_image(self):
        self.img_resize = self.img.resize(self.get_size())
        self.canvas_img = ImageTk.PhotoImage(image= self.draw_image())
        super(rsvis.tools.canvas_resizing.ResizingCanvas, self).create_image(0, 0, image=self.canvas_img, anchor=NW)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self):
        shape = np.asarray(self.img_resize).shape
        img = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
        
        self._patches_bbox = rsvis.utils.patches_unordered.UnorderedPatches(np.asarray(self.img_resize), bbox=self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]))
        
        if self._object_flag:
            img = imgtools.draw_box(img, [], self.resize_bbox([b["box"] for b in self._boxes if isinstance(b, dict)]), [self._color[b["label"]] for b in self._boxes if isinstance(b, dict)])            

        self._patches_grid = rsvis.utils.patches_ordered.OrderedPatches(np.asarray(self.img_resize), num_patches=self._grid, logger=self._logger)

        if self._grid_flag:            
            img = imgtools.get_grid_image(img, [], self._patches_grid.get_bbox())

        if self._selection:
            img = imgtools.draw_box(img, [], [self._selection["box"]], [self._selection["color"]])
        img = Image.fromarray(imgtools.get_transparent_image(img))

        img_label = self.img_resize.copy()
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
        self.img_size = [img.shape[1], img.shape[0]]
        self.img = Image.fromarray(img)

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
        img = self.img_resize
        ev = [
            int(float(event.y)/float(self.size[1])*float(img.size[1])),
            int(float(event.x)/float(self.size[0])*float(img.size[0]))
        ]
        ev[0] = ev[0] if ev[0] <= img.size[1] else img.size[1]
        ev[1] = ev[1] if ev[1] <= img.size[0] else img.size[0]
        
        return ev

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_pressed(self, event):
        self.focus_set()
        self.clear()

        ev = self.resize_event(event)
        self._bbox = [ev[0], ev[0], ev[1], ev[1]]

        if self._area_event==1:
            boxes = list()
            self._patches_bbox.get_bbox_from_point(ev, boxes=boxes)
            
            if len(boxes):
                self._selection = {"box": boxes[0], "color": [150,150,150]}
                
        self.create_image()
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_released(self, event):
        self.focus_set()
        
        ev = self.resize_event(event)
        self._bbox[0] = min([self._bbox[0], ev[0]])
        self._bbox[1] = max([self._bbox[1], ev[0]])
        self._bbox[2] = min([self._bbox[2], ev[1]])
        self._bbox[3] = max([self._bbox[3], ev[1]])

        if not (self._bbox[1]-self._bbox[0] > self._mouse_sensitivity and self._bbox[3]-self._bbox[2] > self._mouse_sensitivity):
            return

        if self._area_event==0:
            patch = self._patches_bbox.get_patch(bbox=self._bbox)
            self._selection = {"box": self._bbox, "color": [150,150,150]}
            self.create_image()

            self.double_button(title="Histogram", dtype="img", value=[patch, imgtools.get_histogram(patch)])
        elif self._area_event==1:
            self._boxes.append({"box": self.resize_bbox([self._bbox], inverted=True)[0],"label": self._label})
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_button(self, event):
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

        self.double_button(title="Histogram", dtype="img", value=[patch,imgtools.get_histogram(patch)])

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        if self._selection and self._patches_bbox:
            idx = self._patches_bbox.equal(self._selection["box"])
            if idx is not None: 
                self._boxes.pop(idx)
                self._selection = dict()
            self.create_image()
