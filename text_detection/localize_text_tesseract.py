# import the necessary packages
from pytesseract import Output
import pytesseract
import argparse
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-c", "--min-conf", type=int, default=0,
	help="mininum confidence value to filter weak text detection")
ap.add_argument("-o", "--output", default="default",
	help="mininum confidence value to filter weak text detection")
args = vars(ap.parse_args())

if args["output"]=="default":
    output_file = "detected_" + args["image"]

# load the input image, convert it from BGR to RGB channel ordering,
# and use Tesseract to localize each area of text in the input image
image = cv2.imread(args["image"])

# todo
# cropping only area of interest, for this is line number from
# Core ML object detection : Line Number
"""
crop_img = image[xmin:xmax, ymin:ymax]
"""

rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
results = pytesseract.image_to_data(rgb, output_type=Output.DICT)

# loop over each of the individual text localizations
for i in range(0, len(results["text"])):
	# extract the bounding box coordinates of the text region from
	# the current result
	x = results["left"][i]
	y = results["top"][i]
	w = results["width"][i]
	h = results["height"][i]
	# extract the OCR text itself along with the confidence of the
	# text localization
	text = results["text"][i]
	conf = int(results["conf"][i])


    # filter out weak confidence text localizations
	if conf > args["min_conf"]:
		# display the confidence and text to our terminal
		print("Confidence: {}".format(conf))
		print("Text: {}".format(text))
		print("")
		# strip out non-ASCII text so we can draw the text on the image
		# using OpenCV, then draw a bounding box around the text along
		# with the text itself
		text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
		cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_DUPLEX,
			0.5, (0, 0, 255), 1)
# save the output image
cv2.imwrite(output_file, image)
cv2.waitKey(0)