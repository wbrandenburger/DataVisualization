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
#[label(str), probability(str), xmin, xmax, ymin, ymax(int)]
def getXml(result_list, hbb=True):
    doc = xml.dom.minidom.Document()
    # owner
    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)
    # # source
    # source = doc.createElement('source')
    # annotation.appendChild(source)
    # filename = doc.createElement('filename')
    # source.appendChild(filename)
    # filename_txt = doc.createTextNode(imgname)
    # filename.appendChild(filename_txt)
    # origin = doc.createElement('origin')
    # source.appendChild(origin)
    # origin_txt = doc.createTextNode("GF2/GF3")
    # origin.appendChild(origin_txt)


    # # research
    # research = doc.createElement('research')
    # annotation.appendChild(research)
    # version = doc.createElement('version')
    # research.appendChild(version)
    # version_txt = doc.createTextNode("4.0")
    # version.appendChild(version_txt)
    # provider = doc.createElement('provider')
    # research.appendChild(provider)
    # provider_txt = doc.createTextNode("UniBwM")
    # provider.appendChild(provider_txt)
    # pluginname = doc.createElement('pluginname')
    # research.appendChild(pluginname)
    # pluginname_txt = doc.createTextNode("Airplane Detection and Recognition")
    # pluginname.appendChild(pluginname_txt)
    # pluginclass = doc.createElement('pluginclass')
    # research.appendChild(pluginclass)
    # pluginclass_txt = doc.createTextNode("Detection")
    # pluginclass.appendChild(pluginclass_txt)
    # time = doc.createElement('time')
    # research.appendChild(time)
    # time_txt = doc.createTextNode("2020-07-2020-11")
    # time.appendChild(time_txt)

    # objects
    objects = doc.createElement('objects')
    annotation.appendChild(objects)


    for bbox in result_list:

        object_new = doc.createElement("object")
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

        # [label(str), probability(str), xmin, xmax, ymin, ymax(int)]
        # 顺时针
        # xmin, ymin    0+2,2+2     2,4
        # xmin, ymax    0,3         2,5
        # xmax, ymax    1,3         3,5
        # xmax, ymin    1,2         3,4

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

    new_file, filename = tempfile.mkstemp()
    filename = os.path.splitext(filename)[0]+'.xml'
    with open(filename, 'wb') as f:
        f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
    
    xml_opener = opener.Opener({"xml": "code.cmd"})
    xml_opener("xml", [filename])
    
    # return filename