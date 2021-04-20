import os
import glob
import re
from PIL import Image 
import pandas as pd

image_path = os.path.join(os.getcwd())

for org_file in glob.glob(image_path + '/*.png'):
    file_index = 0

    filename = os.path.basename(org_file)
    p = re.compile("^\w*")
    classname = p.findall(filename)

    im = Image.open(org_file)
    image = Image.new("RGB", im.size, (255,255,255))
    image.paste(im,im)

    #image.save("results/{}-{}.jpg".format(classname[0], str(file_index).zfill(4)), quality=100, subsampling=0)
    #file_index = file_index + 1

    # rotate image
    for i in range(0, 4):
        new_image = image.rotate(90*i, expand=True)
        new_image.save("results/{}-{}.jpg".format(classname[0], str(file_index).zfill(4)), quality=100, subsampling=0)
        file_index = file_index + 1

        # Flip rotate image
        image_flip = new_image.transpose(Image.FLIP_LEFT_RIGHT)
        image_flip.save("results/{}-{}.jpg".format(classname[0], str(file_index).zfill(4)), quality=100, subsampling=0)
        file_index = file_index + 1

        image_flip = new_image.transpose(Image.FLIP_TOP_BOTTOM)
        image_flip.save("results/{}-{}.jpg".format(classname[0], str(file_index).zfill(4)), quality=100, subsampling=0)
        file_index = file_index + 1

