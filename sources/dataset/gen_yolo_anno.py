"""
output - each image
<object-class-id> <center-x> <center-y> <width> <height>

The first field object-class-id is an integer representing the class of the object.
It ranges from 0 to (number of classes – 1). In our current case, since we have 
only one class of snowman, it is always set to 0.

The second and third entry, center-x and center-y are respectively 
the x and y coordinates of the center of the bounding box, 
normalized (divided) by the image width and height respectively.

The fourth and fifth entry, width and height are respectively 
the width and height of the bounding box, again normalized (divided) 
by the image width and height respectively.

Let’s consider an example with the following notations:

x – x-coordinate(in pixels) of the center of the bounding box
y – y-coordinate(in pixels) of the center of the bounding box
w – width(in pixels) of the bounding box
h – height(in pixels) of the bounding box
W – width(in pixels) of the whole image
H – height(in pixels) of the whole image

Then we compute the annotation values in the label files as follows:

center-x = x / W
center-y = y / H
width = w / W
height = h / H

The above four entries are all floating point values between 0 to 1.
"""
import os
import glob
import re
from PIL import Image 
import pandas as pd
import argparse


image_path = os.path.join(os.getcwd())
cwd_path = image_path

parser = argparse.ArgumentParser(
        description='Create json for images.')
parser.add_argument('--path', required=False,
                    default=image_path,
                    metavar="/path/to/images/",
                    help='Path to images directory (default=./)')

args = parser.parse_args()

image_path = args.path
#print(image_path)

# Save the annotation file in /path/to/images/labels
filename_list = sorted(glob.glob(image_path + '/*.*'))
filename_list = [f for f in filename_list if (f.endswith(".png") or f.endswith(".jpg"))]

with open('custom.txt') as f:
    content = f.readlines()
content = [x.strip() for x in content]

for png_file in filename_list:
    
    filename = os.path.basename(png_file)
    p = re.compile("^\w*")
    classname = p.findall(filename)[0]

    w_filename = os.path.join(cwd_path,'labels/'+os.path.splitext(filename)[0]+'.txt')
    #print(w_filename)
    str_out = '{} {} {} {} {}'.format(content.index(classname),0.5,0.5,1,1)
    #print(str_out)

    with open(w_filename, "w") as f:
        f.write(str_out)
        f.close()