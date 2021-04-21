import os
import glob
import re
from PIL import Image 
import pandas as pd
import argparse


image_path = os.path.join(os.getcwd())


parser = argparse.ArgumentParser(
        description='Create csv for images.')
parser.add_argument('--path', required=False,
                    default=image_path,
                    metavar="/path/to/images/",
                    help='Path to images directory (default=./)')
parser.add_argument('--dataset', required=False,
                    default="csv",
                    metavar="csv|coco",
                    help='Enter dataset class (default=csv)')

args = parser.parse_args()

assert args.dataset in ["csv", "coco"], "Database support is csv or coco"

image_path = args.path
db_type = args.dataset
#print(db_type)

def create_csv_list(image_path, db_type="csv"):
    df_array = []

    for png_file in glob.glob(image_path + '/*.*g'):
        
        filename = os.path.basename(png_file)
        p = re.compile("^\w*")
        classname = p.findall(filename)

        image = Image.open(png_file)
        width, height = image.size

        #print(classname[0], width, height)

        if db_type == "csv":
            value = [filename, width, height, classname[0], 1, 1, width, height]
        elif db_type == "coco":
            value = []
            value.append(filename)
            
            file_size = os.path.getsize(png_file)  #get file size in KB
            value.append(file_size)

            # File Attributes
            value.append("{}")

            # Region count = 1
            value.append(1)

            # Region id = 0
            value.append(0)

            # Region shape attributes
            all_points_x = '[{},{},{},{},{}]'.format(1,width,width,1,1)
            all_points_y = '[{},{},{},{},{}]'.format(1,1,height,height,1)
            value.append('{{"name":"polygon","all_points_x":{},"all_points_y":{}}}'.format(all_points_x, all_points_y))

            # Region attributes
            r_attributes = '{{"custom":"{}"}}'.format(classname[0])
            value.append(r_attributes)

        print(value)
        df_array.append(value)

    if db_type == "csv":
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    elif db_type == "coco":
        column_name = ['filename','file_size','file_attributes','region_count','region_id','region_shape_attributes','region_attributes']


    return df_array, column_name

df_array, column_name = create_csv_list(image_path, db_type)

csv_df = pd.DataFrame(df_array, columns=column_name)
csv_df.to_csv(os.path.join(image_path, 'all_file.csv'), index=None)