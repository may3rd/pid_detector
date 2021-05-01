# import the necessary packages
from pytesseract import Output
import pytesseract
import argparse
import cv2
import numpy as np
import os


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
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(
    blur, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

kernel = np.ones((5,5), np.uint8)

rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 10))

# Appplying dilation on the threshold image
dilation = cv2.dilate(thresh, rect_kernel, iterations = 1)

cv2.imwrite('thresh.jpg', thresh)
cv2.imwrite('dilation.jpg', dilation)
"""
# find contours
contours, hierarchy = cv2.findContours(dilation,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

im2 = image.copy()

for cnt in contours:
	x, y, w, h = cv2.boundingRect(cnt)
      
    # Drawing a rectangle on copied image
	rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Cropping the text block for giving input to OCR
	cropped = im2[y:y + h, x:x + w]

	text = pytesseract.image_to_string(cropped)

	# Apply OCR on the cropped image
	#text = pytesseract.image_to_string(cropped)

	results = pytesseract.image_to_data(cropped, output_type=Output.DICT)
	text_sum = ''
	for i in range(0, len(results["text"])):
		# extract the OCR text itself along with the confidence of the
		# text localization
		text = results["text"][i]
		conf = int(results["conf"][i])

		# filter out weak confidence text localizations
		if conf > 50:
			text_sum += text + ' '
			# display the confidence and text to our terminal
			#print("Confidence: {}".format(conf))
			#print("Text: {}".format(text))
			#print("")
	
	print(text_sum)
"""

results = pytesseract.image_to_data(thresh, output_type=Output.DICT)

j = 0
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
	if conf > 50:
		# display the confidence and text to our terminal
		#print("Confidence: {}".format(conf))
		print("Text {}: {}".format(i, text))
		print("")
		j += 1
		# strip out non-ASCII text so we can draw the text on the image
		# using OpenCV, then draw a bounding box around the text along
		# with the text itself
		#text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
		#cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
		#cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_DUPLEX,
		#	0.5, (0, 0, 255), 1)
# save the output image
#cv2.imwrite(output_file, image)