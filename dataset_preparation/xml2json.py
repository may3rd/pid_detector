import os
import xml.etree.ElementTree as ET
import glob
import json
import shutil
import argparse

def parse_xml(filename, update_classname=False):
    # Add function to create annotations for Create ML
    ## Create dictionary for json keys
    image_dict = {"image":'', "annotations":[]}

    try:
        tree = ET.parse(filename)
    except Exception as e:
        print(e)
        print('Ignore this bad annotion: ' + img_dir + ann)
        return ''

    for elem in tree.iter():
        label_dict = {"label":'', "coordinates":{}}
        coord_dict = {"x":int, "y":int, "width":int, "height":int}
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

                    if name not in classnames and update_classname:
                        classnames.append(name)
                        
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
            # check if name is in classnames
            if name in classnames:
                coord_dict['x'] = int((xmin + xmax)/2)
                coord_dict['y'] = int((ymin + ymax)/2)
                coord_dict['width'] = int(xmax - xmin)
                coord_dict['height'] = int(ymax - ymin)

                label_dict['label'] = name
                label_dict['coordinates'] = coord_dict  
            
                image_dict['annotations'].append(label_dict)

    image_dict['image'] = img_file                            

    # only add new image_dict if 'annotations' > 0
    if len(image_dict['annotations']) > 0:
        annotations.append(image_dict)


def load_classes_name(filename):
    namelist = []
    with open(filename) as f:
        lines = [line.rstrip() for line in f]
        for l in lines:
            namelist.append(l)
    return namelist


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


# ==== MAIN ====
parser = argparse.ArgumentParser(description='Convert xml to Annotations.json and save in results/.')
parser.add_argument('-u', '--update', default=False, type=str2bool, const=True, nargs='?',
                    help='update class.names or not. Default is False')

args = parser.parse_args()

# clear results directory
files = glob.glob('results/*')
for f in files:
    os.remove(f)

classnames = sorted(load_classes_name('class.names'))

print('Read class.names')
print(classnames)

annotations = []

update_classname = args.update

for ann in sorted(glob.glob('images/*.xml')):
    parse_xml(ann, update_classname)

# dump image_dict to json and save to file in results
json_file = json.dumps(annotations)
with open('results/Annotations.json', 'w') as f:
    f.write(json_file)

# copy image files in image_dict to results folder
for ann in annotations:
    filename = ann['image']
    shutil.copy(os.path.join('images', filename), './results/')

# update class.names
if update_classname:
    print('Update class.names')
    print(classnames)
    with open('class.names', 'w') as f:
        for n in classnames:
            f.write('{}\n'.format(n))
