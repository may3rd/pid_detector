import coremltools as ct
import numpy as np
# Load an image using PIL
from PIL import Image
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import argparse
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="test.png",
                help="path to input image to be OCR'd")
ap.add_argument("-c", "--min-conf", type=int, default=0,
                help="mininum confidence value to filter weak text detection")
ap.add_argument("-m", "--model", default="LineNumber.mlmodel",
                help="Create ML exported file path")
ap.add_argument("-o", "--output", default="default",
                help="output file path")
args = vars(ap.parse_args())

if args["output"] == "default":
    output_file = "detected_" + args["image"]

input_file = args["image"]

model_file = args["model"]

def load_image(path, resize_to=None):
    # resize_to: (Width, Height)
    img = Image.open(path)
    Width, Height = img.size

    if resize_to is not None:
        img = img.resize(resize_to, Image.ANTIALIAS)
    img_np = np.array(img).astype(np.float32)

    return img_np, img, Width, Height

class BoundBox:
	def __init__(self, xmin, ymin, xmax, ymax, objness=None, classes=None):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.objness = objness
		self.classes = classes
		self.label = -1
		self.score = -1

	def get_label(self):
		if self.label == -1:
			self.label = np.argmax(self.classes)

		return self.label

	def get_score(self):
		if self.score == -1:
			self.score = self.classes[self.get_label()]

		return self.score

def draw_boxes(filename, v_boxes, v_labels, v_scores):
	# load the image
	data = pyplot.imread(filename)
	# plot the image
	pyplot.imshow(data)
	# get the context for drawing boxes
	ax = pyplot.gca()

	# read image for cropping
	img = cv2.imread(filename)

	# plot each box
	for i in range(len(v_boxes)):
		box = v_boxes[i]
		# get coordinates
		y1, x1, y2, x2 = box.ymin, box.xmin, box.ymax, box.xmax
		# calculate width and height of the box
		width, height = x2 - x1, y2 - y1
		# create the shape
		rect = Rectangle((x1, y1), width, height, fill=False, color='red')
		# draw the box
		ax.add_patch(rect)
		# draw text and score in top left corner
		label = "%s (%.3f)" % (v_labels[i], v_scores[i])
		pyplot.text(x1, y1, label, color='red')

		# copy image
		img2 = img.copy()

		# Cropping the text block for giving input to OCR
		cropped = img2[y1:y2, x1:x2]

		cv2.imwrite('{}_{}{}'.format(output_file[:-4], i+1, output_file[-4:]), cropped)

	# show the plot
	#pyplot.show()
	pyplot.savefig(output_file)

def detect_image_file(filename):

	_, img, width, height = load_image(filename, resize_to=(416, 416))

	prediction = model.predict({'imagePath': img})

	v_boxes, v_labels, v_scores = list(), list(), list()

	positions = prediction['coordinates']
	scores = prediction['confidence']

	for i in range(len(positions)):
		pos = positions[i]
		x = pos[0]
		y = pos[1]
		w = pos[2]
		h = pos[3]
		xmin = int((x - w / 2) * width)
		ymin = int((y - h / 2) * height)
		xmax = int(xmin + w * width)
		ymax = int(ymin + h * height)
		box = BoundBox(xmin, ymin, xmax, ymax, scores[i], 'Line number')
		v_boxes.append(box)
		v_labels.append('Line number')
		v_scores.append(scores[i])

	draw_boxes(input_file, v_boxes, v_labels, v_scores)


# load Core ML model
model = ct.models.MLModel(model_file)

detect_image_file(input_file)