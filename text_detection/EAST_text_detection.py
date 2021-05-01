from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import glob
import os
import pytesseract


def EAST_text_detector(original, image, confidence=0.25):
    # Set the new width and height and determine the changed ratio
    (h, W) = image.shape[:2]
    (newW, newH) = (640, 640)
    rW = W / float(newW)
    rH = h / float(newH)

    # Resize the image and grab the new image dimensions
    image = cv2.resize(image, (newW, newH))
    (h, W) = image.shape[:2]

    # Define the two output layer names for the EAST detector model that
    # we are interested -- the first is the output probabilities and the
    # second can be used to derive the bounding box coordinates of text
    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    net = cv2.dnn.readNet('frozen_east_text_detection.pb')

    # Construct a blob from the image and then perform a forward pass of
    # the model to obtain the two output layer sets
    blob = cv2.dnn.blobFromImage(image, 1.0, (W, h), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    # Grab the number of rows and columns from the scores volume, then
    # initialize our set of bounding box rectangles and corresponding
    # confidence scores
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # Loop over the number of rows
    for y in range(0, numRows):
        # Extract the scores (probabilities), followed by the geometrical
        # data used to derive potential bounding box coordinates that
        # surround text
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # Loop over the number of columns
        for x in range(0, numCols):
            # If our score does not have sufficient probability, ignore it
            if scoresData[x] < confidence:
                continue

            # Compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # Extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # Use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # Compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # Add the bounding box coordinates and probability score to
            # our respective lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    # Apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    boxes = non_max_suppression(np.array(rects), probs=confidences)

    # Loop over the bounding boxes
    for (startX, startY, endX, endY) in boxes:
        # Scale the bounding box coordinates based on the respective
        # ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        # Draw the bounding box on the image
        cv2.rectangle(original, (startX, startY), (endX, endY), (36, 255, 12), 2)
    return original

def prepare_image(filename):
    """
    thresh, clean, dilation = prepare_image(filename)
    """
    # Convert to grayscale and Otsu's threshold
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    clean = thresh.copy()

    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,1))
    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(clean, [c], -1, 0, 3)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,30))
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(clean, [c], -1, 0, 3)

    # Appplying dilation on the threshold image
    kernel = np.ones((5,5), np.uint8)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    dilation = cv2.dilate(clean, rect_kernel, iterations = 1)

    return image, thresh, clean, dilation

def prepare_image_remove_nontext(clean):
    # Remove non-text contours (curves, diagonals, circlar shapes)
    cnts = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 1500:
            cv2.drawContours(clean, [c], -1, 0, -1)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        x,y,w,h = cv2.boundingRect(c)
        if len(approx) == 4:
            cv2.rectangle(clean, (x, y), (x + w, y + h), 0, -1)

    # Bitwise-and with original image to remove contours
    filtered = cv2.bitwise_and(image, image, mask=clean)
    filtered[clean==0] = (255,255,255)
    return filtered


def set_crop_with_offset(x, y, w, h, xoffset, yoffset, width, height):
    x1 = x - xoffset
    x2 = x + w + 2*xoffset
    y1 = y - yoffset
    y2 = y + h + 2*yoffset

    if x1 < 0:
        x1 = 0
    if x2 > width:
        x2 = width
    if y1 < 0:
        y1 = 0
    if y2 > height:
        y2 = height
    
    return x1, y1, x2, y2

for filename in sorted(glob.glob('images/*.*')):
    print('Processing file: {}'.format(filename))
    image, _, clean, dilation = prepare_image(filename)
    img = image.copy()

    filtered = prepare_image_remove_nontext(clean)

    #cv2.imwrite('processing/' + os.path.basename(filename)[:-4] + '_cln.jpg', clean)
    #cv2.imwrite('processing/' + os.path.basename(filename)[:-4] + '_dlt.jpg', dilation)

    # find contours
    contours, hierarchy = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    xoffset = 5
    yoffset = 5
    height, width, _ = image.shape

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w/h > 5:
            # Drawing a rectangle on copied image
            x1, y1, x2, y2 = set_crop_with_offset(x, y, w, h, xoffset, yoffset, width, height)
            #rect = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Cropping the text block for giving input to OCR
            cropped = clean[y1:y2, x1:x2]

            custom_oem_psm_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(cropped, config=custom_oem_psm_config)

            # strip out non-ASCII text
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_DUPLEX,
                        0.5, (0, 0, 255), 1)
            #print(text)
    
    cv2.imwrite('processing/' + os.path.basename(filename)[:-4] + '_ctr.jpg', image)

    #result = EAST_text_detector(img, filtered)
    #cv2.imwrite('processing/' + os.path.basename(filename)[:-4] + '_flt.jpg', filtered)

exit()

image, thresh, clean, dilation = prepare_image('images/test.png')
filtered = prepare_image_remove_nontext(clean)

# Perform EAST text detection
result = EAST_text_detector(image, filtered)

#cv2.imshow('filtered', filtered)
#cv2.imshow('result', result)
#cv2.waitKey()

cv2.imwrite('filtered.jpg', filtered)
cv2.imwrite('result.jpg', result)

exit()

# find contours
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

i = 1
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
      
    # Drawing a rectangle on copied image
    #rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Cropping the text block for giving input to OCR
    cropped = im2[y:y + h, x:x + w]
    
    # Save cropping
    filename = "cropped/{}.jpg".format(i)
    cv2.imwrite(filename, cropped)

    # Apply OCR on the cropped image
	#text = pytesseract.image_to_string(cropped)
    i = i + 1

    custom_oem_psm_config = r'--oem 3 --psm 6'
    #pytesseract.image_to_string(image, config=custom_oem_psm_config)
