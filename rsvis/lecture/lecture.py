lecture_options = [
        { 
            "label" : "Objects",
            "name" : "Objects On/Off",
            "key" : "c",
            "description": "Show the bounding boxes in the currently displayed image.",
            "command": lambda obj: obj.show_objects()
        },
        { 
            "label" : "Objects",
            "name" : "Save objects",
            "key" : "v",
            "description": "Save displayed objects.",
            "command": lambda obj: obj.save_object()
        },
        { 
            "label" : "Objects",
            "name" : "Remove selected object",
            "key" : "b",
            "description": "Remove the selected object.",
            "command": lambda obj: obj.remove_object()
        }
    ]