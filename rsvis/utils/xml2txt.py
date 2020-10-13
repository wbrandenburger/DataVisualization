# ===========================================================================
#   xml2txt.py --------------------------------------------------------------
# ===========================================================================


import xml.dom.minidom
import xml.etree.ElementTree as ET
import tempfile
import os
import subprocess as sp

from rsvis.utils import opener

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_source(parent, filename='', label=dict()):
    doc = xml.dom.minidom.Document()
    
    # source
    xml_source = doc.createElement('source')
    parent.appendChild(xml_source)

    xml_filename = doc.createElement('filename')
    xml_source.appendChild(xml_filename)
    filename_txt = doc.createTextNode(filename)
    xml_filename.appendChild(filename_txt)

    if label:
        xml_label = doc.createElement('label')
        xml_source.appendChild(xml_label)
        for l_k, l_i in label.items(): 
            element = doc.createElement(l_k)
            xml_label.appendChild(element)
            xml_l_i = doc.createTextNode(l_i)
            element.appendChild(xml_l_i)

    # origin = doc.createElement('origin')
    # source.appendChild(origin)
    # origin_txt = doc.createTextNode("GF2/GF3")
    # origin.appendChild(origin_txt)

    return parent

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def add_source(parent, filename):
    doc = xml.dom.minidom.Document()
    

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def getXml(result_list, source=True, filename='', label=dict(), hbb=True):
    
    # [label(str), probability(str), xmin, xmax, ymin, ymax(int)]
    # xmin, ymin    0+2,2+2     2,4
    # xmin, ymax    0,3         2,5
    # xmax, ymax    1,3         3,5
    # xmax, ymin    1,2         3,4

    doc = xml.dom.minidom.Document()

    # owner
    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)

    if source:
        annotation = add_source(annotation, filename=filename, label=label)

    # objects
    objects = doc.createElement('objects')
    annotation.appendChild(objects)

    for bbox in result_list:

        object_new = doc.createElement('object')
        objects.appendChild(object_new)

        coordinate = doc.createElement('coordinate')
        object_new.appendChild(coordinate)
        coordinate_txt = doc.createTextNode("pixel")
        coordinate.appendChild(coordinate_txt)
        type = doc.createElement('type')
        object_new.appendChild(type)
        type_txt = doc.createTextNode("rectangle")
        type.appendChild(type_txt)
        description = doc.createElement('description')
        object_new.appendChild(description)
        description_txt = doc.createTextNode("None")
        description.appendChild(description_txt)

        possibleresult = doc.createElement('possibleresult')
        object_new.appendChild(possibleresult)

        name = doc.createElement('name')
        possibleresult.appendChild(name)
        name_txt = doc.createTextNode(bbox[0])
        name.appendChild(name_txt)
        probability = doc.createElement('probability')
        possibleresult.appendChild(probability)
        probability_txt = doc.createTextNode(bbox[1])
        probability.appendChild(probability_txt)

        points = doc.createElement('points')
        object_new.appendChild(points)

        if hbb:

            point = doc.createElement('point')
            points.appendChild(point)
            point_txt = doc.createTextNode(str(bbox[2])+','+str(bbox[4]))
            point.appendChild(point_txt)

            point = doc.createElement('point')
            points.appendChild(point)
            point_txt = doc.createTextNode(str(bbox[2]) + ',' + str(bbox[5]))
            point.appendChild(point_txt)

            point = doc.createElement('point')
            points.appendChild(point)
            point_txt = doc.createTextNode(str(bbox[3]) + ',' + str(bbox[5]))
            point.appendChild(point_txt)

            point = doc.createElement('point')
            points.appendChild(point)
            point_txt = doc.createTextNode(str(bbox[3]) + ',' + str(bbox[4]))
            point.appendChild(point_txt)

            point = doc.createElement('point')
            points.appendChild(point)
            point_txt = doc.createTextNode(str(bbox[2]) + ',' + str(bbox[4]))
            point.appendChild(point_txt)
            
        else:
            break

    return doc

#   function ----------------------------------------------------------------
# ---------------------------------------------------------------------------
def box2xml(result_list):
    doc = getXml(result_list, source=False, hbb=True)
    _, filename = tempfile.mkstemp()
    filename = os.path.splitext(filename)[0]+'.xml'
    with open(filename, 'wb') as f:
        f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
    
    xml_opener = opener.GeneralOpener()
    xml_opener("xml", [filename])
    
    # return filename