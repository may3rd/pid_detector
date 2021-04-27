# import the necessary packages
#from pytesseract import Output
#import pytesseract
import argparse
import cv2
import numpy

# load the input image, convert it from BGR to RGB channel ordering,
# and use Tesseract to localize each area of text in the input image
image = cv2.imread('test.png')

# todo
# cropping only area of interest, for this is line number from
# Core ML object detection : Line Number
"""
crop_img = image[xmin:xmax, ymin:ymax]
"""

#rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#blur = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(
    blur, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

cv2.imwrite('thresh.jpg', thresh)

kernel = np.ones((5,5), np.uint8)

img_erosion = cv2.erode(grey, kernel, iterations=1)
img_dilation = cv2.dilate(grey, kernel, iterations=1)

cv2.imwrite('erosion.jpg', img_erosion)
cv2.imwrite('dilation.jpg', img_dilation)

"""
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
"""