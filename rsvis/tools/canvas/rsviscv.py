# ===========================================================================
#   rsviscv.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.general as gu
import rsvis.utils.imgtools as imgtools
import rsvis.utils.patches_ordered
import rsvis.utils.patches_unordered

from rsvis.tools.canvas import extimgconcv

import numpy as np
import pathlib
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Listbox, Scrollbar, INSERT, END, TOP, N, W, E, S

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class RSVisCanvas(extimgconcv.ExtendedImgConCv):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        parent,
        data,
        popup=None, 
        classes=dict(),
        **kwargs
    ):

        #   settings --------------------------------------------------------
        super(RSVisCanvas, self).__init__(parent, shift=[4,4], **kwargs)
        
        self._set_popup = popup if popup else (lambda *args, **kwargs: None)

        self._data = data
        self._images = data.get_img_in()
        self._show_log = data.show_log()
        self._idx_list = rsvis.utils.index.Index(len(self))

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
        self.bind("<Control-Double-Button-1>", self.ctrl_mouse_button_2_released)
        # self.bind("<Double-Button-1>", self.mouse_double_1_button)

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
    def __iter__(self):
        self._idx_list.__iter__()
        return self

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __len__(self):
        return len(self._images)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __next__(self):
        self._idx_list.__next__()
        self.set_container(index=self._idx_list())
        return self
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def next(self):
        index = self._idx_list.next()
        self.set_container(index=index)
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def last(self):
        index = self._idx_list.last()
        self.set_container(index=index)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def draw_image(self, **kwargs):
        img_assembly = super(RSVisCanvas, self).draw_image(**kwargs)
        
        boxes = self.get_object_boxes()
        self._patches_bbox = rsvis.utils.patches_unordered.UnorderedPatches(np.asarray(self._img_draw), bbox=boxes)
        
        if self._object_flag and boxes:
            img = imgtools.draw_box(self.get_intial_draw_image(), [], boxes, self.get_object_colors(), dtype=np.int16)            
            img_assembly = np.where(img_assembly>=0, img_assembly, img)

        return img_assembly

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_object_boxes(self, box, resize=False, append=True):
        box = self.resize_boxes(box, inversion=True)[0] if resize else box
        if append:
            self._boxes.append({"box": box, "label": self._label})
        else:
            self._boxes = box
        self.show_objects(force=True)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object_boxes(self, resize=True):
        boxes = [b["box"] for b in self._boxes if b]
        return self.resize_boxes(boxes) if resize and boxes else boxes 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object_colors(self):
        return [self._color[b["label"]] for b in self._boxes if b]

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_container(self, index=None):
        index = self._idx_list() if index is None else index   
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
    def get_idx_list(self):
        return self._idx_list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_area_event(self, index=0, **kwargs):
        self._area_event = index
        if self._area_event==1:
            self._object_flag = 0
            self.show_objects()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def show_objects(self, force=False):
        self._object_flag = 0 if self._object_flag else 1
        if force:
            self._object_flag = 1
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_object(self):
        self._boxes = self._data.get_object_in(self._images[self._idx_list()][0].path, default=list())
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def write_object(self):
        self._data.set_object_in(self._images[self._idx_list()][0].path, self._boxes) 
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def remove_object(self):
        selection = self.get_selection("selection", resize=True)
        if selection and self._patches_bbox:
            idx = self._patches_bbox.equal(selection)
            if idx is not None: 
                self._boxes.pop(idx)
                self.clear_selection("selection")
            self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_label(self, label):
        self._label = label
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_log(self):
        filename = pathlib.Path(self.get_img_path())
        log = self._show_log(self.get_img_path(), path_dir=filename.parent, name=filename.stem, ext=".log")
        
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup(self, bbox, histogram=True):
        if bbox:
            img_container = self._img_container.copy()
            img_container.set_bbox(bbox)
            self._set_popup(title="Histogram Canvas" if histogram else "Patch Canvas", dtype="img", value=img_container, histogram=histogram) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def set_popup_images(self, histogram=True):
        self._set_popup(title="Histogram Canvas" if histogram else "Patch Canvas", dtype="img", value=self._data, histogram=histogram) 

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_pressed(self, event):
        super(RSVisCanvas, self).mouse_button_1_pressed(event)
        if self._area_event==1:
            indices=list()
            self._patches_bbox.get_bbox_from_point(self._mouse_event, indices=indices)
            if len(indices):
                self.set_selection(self._boxes[indices[0]]["box"], "selection", resize=False)
        self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_1_released(self, event, histogram=True):
        super(RSVisCanvas, self).mouse_button_1_released(event)
        if self.is_mouse_event(self._mouse_box):
            if self._area_event==0:
                self.set_popup(self._mouse_selection, histogram=histogram)
            elif self._area_event==1:
                self.set_object_boxes(self._mouse_box, resize=True)
                self.create_image()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_double_1_button(self, event):
        self.focus_set()
        self.clear_selection("temporary")
        self.clear_selection("selection")
        self.mouse_button_2_released(event, histogram=False)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def mouse_button_2_released(self, event, histogram=True):
        self.focus_set()
        if self._area_event==0:
            bbox = self.resize_boxes(self.get_grid_bbox(event), inversion=True)[0]
        elif self._area_event==1:
            boxes = list()
            self._patches_bbox.get_bbox_from_point(self.resize_event(event), boxes=boxes)
            bbox = self.resize_boxes(boxes, inversion=True)[0] if len(boxes) else None
        self.set_popup(bbox, histogram=histogram)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def ctrl_mouse_button_2_released(self, event, histogram=True):
        self.focus_set()
        self.set_popup_images(histogram=histogram)

        # idx_list = rsvis.utils.index.Index(len(self._images))

        # a = self._data.get_img_out()
        # b = self._data.show_log()
        # c = self._data.get_log_out()

        # for idx, imgcon in enumerate(self._images):
        #     a(imgcon[0].path, imgcon[0].data, prefix="arsch", ext=".png")
        #     c(imgcon[0].path, "HAHA - {} - HUHU".format(idx))
        #     b(imgcon[0].path)


    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_w(self, event, **kwargs):
        """Show the next image of the given image set."""
        super(RSVisCanvas, self).key_w(event)
        self.set_log()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_s(self, event, **kwargs):
        """Show the previous image of the given image set."""
        super(RSVisCanvas, self).key_s(event)
        self.set_log()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_d(self, event, **kwargs):
        """Show the next image in given image list (see listbox)."""
        self.next()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def key_a(self, event, **kwargs):
        """Show the previous image in given image list (see listbox)."""
        self.last()

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