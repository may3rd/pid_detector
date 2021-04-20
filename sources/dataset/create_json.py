import os
import glob
import re
from PIL import Image 
import pandas as pd
import argparse


image_path = os.path.join(os.getcwd())


parser = argparse.ArgumentParser(
        description='Create json for images.')
parser.add_argument('--path', required=False,
                    default=image_path,
                    metavar="/path/to/images/",
                    help='Path to images directory (default=./)')

args = parser.parse_args()

image_path = args.path
#print(db_type)

def create_json_list(image_path):
    df_array = []

    for png_file in sorted(glob.glob(image_path + '/*.*g')):
        
        filename = os.path.basename(png_file)
        p = re.compile("^\w*")
        classname = p.findall(filename)

        image = Image.open(png_file)
        width, height = image.size

        filesize = os.path.getsize(png_file)

        #value = [filename, file_size, width, height, classname[0]]
        value = {}
        value['filename'] = filename
        value['filesize'] = filesize
        value['width'] = width
        value['height'] = height
        value['classname'] = classname[0]
        df_array.append(value)

        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']

    return df_array, column_name

df_array, column_name = create_json_list(image_path)

# initialize string
str_out = '{'

for n in df_array:
    # generate each element
    str_out = str_out + '"{}{}":'.format(n['filename'], n['filesize'])
    str_out = str_out + '{'
    str_out = str_out + '"fileref":"",'
    str_out = str_out + '"filename":"{}",'.format(n['filename'])
    str_out = str_out + '"size":{},'.format(n['filesize'])
    str_out = str_out + '"base64_img_data":"","file_attributes":{},'
    str_out = str_out + '"regions":{"0":{'
    str_out = str_out + '"shape_attributes":{"name":"polygon",'
    width = n['width']
    height = n['height']
    str_out = str_out + '"all_points_x":[{},{},{},{},{}],'.format(1, width, width, 1, 1)
    str_out = str_out + '"all_points_y":[{},{},{},{},{}]'.format(1, 1, height, height, 1)
    str_out = str_out + '},'
    str_out = str_out + '"region_attributes":{"custom":"' + n['classname'] + '"}'
    str_out = str_out + '}}}'
    if n == df_array[-1]:
        #print(str_out)
        str_out = str_out
    else:
        str_out = str_out + ','
        #print('{},'.format(n))

# close string
str_out = str_out + '}'

print(str_out)