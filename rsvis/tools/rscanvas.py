# ===========================================================================
#   rscanvas.py ---------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

import rsvis.tools.imgconcanvas

import numpy as np
import pathlib
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Listbox, Scrollbar, INSERT, END, TOP, N, W, E, S

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSCanvas(rsvis.tools.imgconcanvas.ImgConCanvas):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent,
        images,
        data,
        textbox=None,
        popup=None, 
        classes=dict(), 
        **kwargs
    ):

        #   settings --------------------------------------------------------
        super(RSCanvas, self).__init__(parent, shift=[4,4], **kwargs)
        
        self._set_popup = popup if popup else (lambda x: x)

        self._data = data
        self._images = images
        self._index_list = rsvis.utils.index.Index(len(self._images))

        self._textbox = textbox

        self._area_event = 0

        self._object_flag = 0

        self._patches_bbox = None
        self._grid_bboxes = None

        self._boxes = list()                        
        self._color = dict((c["name"], c["color"]) for c in classes)
        self._label = list(self._color.keys())[0] if self._color else None

        self._bbox = [0, 0, 0, 0]

        #   key bindings ----------------------------------------------------
        self.bind("<ButtonRelease-2>", self.mouse_button_2_released)
        self.bind("<Double-Button-1>", self.mouse_double_1_button)

        self.bind("<w>", self.key_w)
        self.bind("<s>", self.key_s)
        self.bind("<a>", self.key_a)
        self.bind("<d>", self.key_d)
        self.bind("<f>", self.key_f)
        self.bind("<g>", self.key_g)

        self._keys.update({
            "d": "Show the next image in given image list (see listbox).",
            "a": "Show the previous image in given image list (see listbox).",
            "f": "Show or hide the objects for a given image set.",           
            "g": "Remove the selected object."
        })

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_assembly = super(RSCanvas, self).draw_image(**kwargs)
        
        boxes = self.get_object_boxes()
        self._patches_bbox = rsvis.utils.patches_unordered.UnorderedPatches(np.asarray(self._img_draw), bbox=boxes)

        if self._object_flag:
            img = imgtools.draw_box(self.get_intial_draw_image(), [], boxes, self.get_object_colors(), dtype=np.int16)            
            img_assembly = np.where(img_assembly>=0, img_assembly, img)

        return img_assembly

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_object_boxes(self, box, resize=True):
        box = self.resize_boxes(box, inversion=True)[0] if resize else box
        self._boxes.append({"box": box, "label": self._label})

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object_boxes(self, resize=True):
        boxes = [b["box"] for b in self._boxes if isinstance(b, dict)]
        return self.resize_boxes(boxes) if resize else boxes 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object_colors(self):
        return [self._color[b["label"]] for b in self._boxes if isinstance(b, dict)]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_container(self, index=None):
        index = self._index_list() if index is None else index   
        self.get_object()
        self.set_img_container(self._images[index])
        self.set_log()        

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    @property
    def obj(self):
        return self._object_flag

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_index_list(self):
        return self._index_list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, index=0, **kwargs):
        self._area_event = index
        if self._area_event==1:
            self._object_flag = 0
            self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_class(self, index=False):
        return list(self._color.keys()).index(self._label) if index else self._label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_class(self, label):
        self._label = label

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_objects(self):
        self._object_flag = 0 if self._object_flag  else 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object(self):
        self._boxes = self._data.get_object_in(self._images[self._index_list()][0].path, default=list())

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write_object(self):
        self._data.set_object_in(self._images[self._index_list()][0].path, self._boxes) 
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        if self._selection and self._patches_bbox:
            idx = self._patches_bbox.equal(self.resize_boxes(self._selection)[0])
            if idx is not None: 
                self._boxes.pop(idx)
                self.clear_selection()
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log(self):
        log = self._data.get_log_in(self.get_img_path(), default="")
        if log:
            self._textbox.insert("1.0", "{}\n".format(log))

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup(self, bbox, histogram=True):
        if bbox:
            img_container = self._img_container.copy()
            img_container.set_bbox(bbox)
            self._set_popup(title="Histogram", dtype="img", value=img_container, histogram=histogram) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        super(RSCanvas, self).mouse_button_1_pressed(event)
        if self._area_event==1:
            indices=list()
            self._patches_bbox.get_bbox_from_point(self._mouse_event, indices=indices)
            if len(indices):
                self.set_selection(self._boxes[indices[0]]["box"], resize=False)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event):
        super(RSCanvas, self).mouse_button_1_released(event)
        if self.is_mouse_event(self._mouse_box):
            if self._area_event==0:
                self.set_popup(self._mouse_selection)
            elif self._area_event==1:
                self.set_object_boxes(self._mouse_box)
                self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_1_button(self, event):
        self.focus_set()
        self.clear_selection()
        self.mouse_button_2_released(event, histogram=False)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_2_released(self, event, histogram=True):
        self.focus_set()
        ev = self.resize_event(event)
        if self._area_event==0:
            bbox = self.resize_boxes(self.get_grid_bbox(event), inversion=True)[0]
        elif self._area_event==1:
            boxes = list()
            self._patches_bbox.get_bbox_from_point(ev, boxes=boxes)
            bbox = self.resize_boxes(boxes, inversion=True)[0] if len(boxes) else None
        self.set_popup(bbox, histogram=histogram)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        super(RSCanvas, self).key_w(event)
        self.set_log()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        super(RSCanvas, self).key_s(event)
        self.set_log()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, event, **kwargs):
        """Show the next image in given image list (see listbox)."""
        index = self._index_list.next()
        self.set_container(index=index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, event, **kwargs):
        """Show the previous image in given image list (see listbox)."""
        index = self._index_list.last()
        self.set_container(index=index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_f(self, event=None):
        """Show or hide the objects for a given image set."""
        self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_g(self, event=None):
        "Remove the selected object."
        self.remove_object()