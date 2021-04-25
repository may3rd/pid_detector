import numpy as np
import os
import xml.etree.ElementTree as ET
import glob
import json

def parse_xml(filename, classname=[]):
    """
    return:
        classname xmin ymin xmax ymax
    """
    str_out = ''

    # Add function to create annotations for Create ML
    ## Create dictionary for json keys
    image_dict = {"image":'', "annotations":[]}
    label_dict = {"label":'', "coordinates":{}}
    coord_dict = {"x":int, "y":int, "width":int, "height":int}

    try:
        tree = ET.parse(filename)
    except Exception as e:
        print(e)
        print('Ignore this bad annotion: ' + img_dir + ann)
        return ''

    for elem in tree.iter():
        if 'filename' in elem.tag:
            img_file = elem.text
        if 'width' in elem.tag:
            width = int(elem.text)
        if 'height' in elem.tag:
            height = int(elem.text)
        if 'object' in elem.tag or 'part' in elem.tag:
            name = ''
            xmin = ymin = xmax = ymax = 0

            for attr in list(elem):
                if 'name' in attr.tag:
                    name = attr.text
                        
                if 'bndbox' in attr.tag:
                    for dim in list(attr):
                        if 'xmin' in dim.tag:
                            xmin = int(round(float(dim.text)))
                        if 'ymin' in dim.tag:
                            ymin = int(round(float(dim.text)))
                        if 'xmax' in dim.tag:
                            xmax = int(round(float(dim.text)))
                        if 'ymax' in dim.tag:
                            ymax = int(round(float(dim.text)))
            i = classnames.index(name)
            x = (xmin + xmax) / (2 * width)
            y = (ymin + ymax) / (2 * height)
            w = (xmax - xmin) / width
            h = (ymax - ymin) / height
            str_out += '{} {} {} {} {}\n'.format(i, x, y, w, h)

            coord_dict['x'] = int((xmin + xmax)/2)
            coord_dict['y'] = int((ymin + ymax)/2)
            coord_dict['width'] = int(xmax - xmin)
            coord_dict['height'] = int(ymax - ymin)

            label_dict['label'] = name
            label_dict['coordinates'] = coord_dict

            image_dict['image'] = img_file
            image_dict['annotations'].append(label_dict)                               

            annotations.append(image_dict)
    return str_out

def load_classes_name(filename):
    namelist = []
    with open(filename) as f:
        lines = [line.rstrip() for line in f]
        for l in lines:
            namelist.append(l)
    return namelist

def xml2txt(filename, classnames):
    txtname = os.path.splitext(filename)[0] + '.txt'
    str_out = parse_xml(ann, classnames)
    f = open(txtname, 'w')
    f.write(str_out)
    f.close
    print(txtname)
    print(str_out)

classnames = load_classes_name('animal.names')

annotations = []

for ann in sorted(glob.glob('images/*.xml')):
    xml2txt(ann, classnames)

json_file = json.dumps(annotations)
with open('Annotations.json', 'w') as f:
    f.write(json_file)