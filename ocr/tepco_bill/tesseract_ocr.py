"""
Tutorials

# 1. Shape detection

* https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
* https://www.pyimagesearch.com/2016/02/08/opencv-shape-detection/
* https://docs.opencv.org/3.4.0/d4/d73/tutorial_py_contours_begin.html
* https://docs.opencv.org/3.4.0/dd/d49/tutorial_py_contour_features.html
* https://docs.opencv.org/3.4.1/d7/d4d/tutorial_py_thresholding.html

# 2. Correct skew image

* https://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/

# 3. Detect ROI

* https://www.pyimagesearch.com/2015/11/30/detecting-machine-readable-zones-in-passport-images/

"""
import cv2
import os
import imutils
import numpy as np
import sys
from .display_util import show_img
from .display_util import save_box
from ..utils import image as img_utils
from . import constants, correction_util, config
from ..utils import constants as shared_constants
from ..utils.tesseract import call_tesseract_command


def find_roi(blur_image, debug=False, debug_output_dir=None):
    # apply the blackhat morphological operator to find dark regions on a light background
    rect_kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (141, 3))
    blackhat = cv2.morphologyEx(blur_image, cv2.MORPH_BLACKHAT, rect_kernel_1)

    if debug:
        show_img(blackhat, output_dir=debug_output_dir)

    # compute the Scharr gradient of the blackhat image and scale the result into the range [0, 255]
    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    # apply a closing operation using the rectangular kernel to close
    # gaps in between letters -- then apply Otsu's thresholding method
    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rect_kernel_1)
    _, thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    if debug:
        show_img(thresh, output_dir=debug_output_dir)

    # perform another closing operation to close gaps between lines, then perform a
    # series of erosions to break apart connected components
    rect_kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 7))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, rect_kernel_2)
    thresh = cv2.erode(thresh, None, iterations=4)

    if debug:
        show_img(thresh, output_dir=debug_output_dir)

    # Get the right ROI
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]

    max_area = 0
    for contour in contours:
        rect = cv2.minAreaRect(contour)
        rect_min_side = min(rect[shared_constants.RECT_SIZE])
        rect_max_side = max(rect[shared_constants.RECT_SIZE])

        if (rect_min_side * rect_max_side > max_area) and (rect_max_side / rect_min_side < 20):
            (x, y, w, h) = cv2.boundingRect(contour)
            pX = int((x + w) * 0.03)
            pY = int((y + h) * 0.15)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))
            xmin, xmax, ymin, ymax = max(x, 0), min(x + w, blur_image.shape[1] - 1), \
                                     max(y, 0), min(y + h, blur_image.shape[0] - 1)
    roi = blur_image[ymin:ymax, xmin:xmax]

    if debug:
        show_img(roi, output_dir=debug_output_dir)

    return roi


def get_binary_image(image_array, box=constants.BOX_CODES['location_code'], debug=False, debug_output_dir=None):
    # Threshold
    thresh_image = cv2.adaptiveThreshold(image_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 201, 2)

    if debug:
        show_img(thresh_image, output_dir=debug_output_dir)

    # Morphological operations
    if box in [constants.BOX_CODES['location_code'], constants.BOX_CODES['customer_code']]:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph_image = cv2.morphologyEx(thresh_image, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=1)
    elif box == constants.BOX_CODES['customer_name']:
        kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morph_image = cv2.morphologyEx(thresh_image, op=cv2.MORPH_CLOSE, kernel=kernel1, anchor=(-1, -1), iterations=1)
    elif box == constants.BOX_CODES['customer_address']:
        kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morph_image = cv2.morphologyEx(thresh_image, op=cv2.MORPH_CLOSE, kernel=kernel1, anchor=(-1, -1), iterations=1)

    if debug:
        show_img(morph_image, output_dir=debug_output_dir)

    # Back to black-on-white image
    bw_roi = 255 - morph_image

    if debug:
        show_img(bw_roi, output_dir=debug_output_dir)

    return bw_roi


def ocr_box(image_array, left_top_width_height, box=constants.BOX_CODES['location_code'], psm=4, debug=False,
            debug_output_dir=None):
    box_img = image_array[left_top_width_height[1]:(left_top_width_height[1] + left_top_width_height[3]),
                                            left_top_width_height[0]:(left_top_width_height[0] + left_top_width_height[2])]

    # TODO Consider rescaling if necessary
    if box in [constants.BOX_CODES['customer_address'], constants.BOX_CODES['customer_name']]:
        box_img = img_utils.rescale_image(box_img, min_height=125)

    # Blur image
    processed_image =cv2.medianBlur(box_img, 3)

    if debug:
        show_img(processed_image, output_dir=debug_output_dir)

    if box in [constants.BOX_CODES['customer_address'], constants.BOX_CODES['customer_name']]:
        # Find ROI
        processed_image = find_roi(processed_image, debug=debug)

    # convert ROI to bw image
    bw_roi = get_binary_image(processed_image, box=box, debug=debug)

    result = call_tesseract_command(bw_roi, tessdata_dir=config.tessdata_dir, lang='jpn+eng', psm=psm)

    return result


def get_notice_label_rect(rectangles):
    """
    Get notice label rectangle (電気ご使用のお知らせ). It is the most-left rectangle
    :param rectangles: List of rectangle: ((center_x, center_y), (width, height), angle)
    :return:
    """
    index = 0
    center_x = sys.maxsize
    for i, rect in enumerate(rectangles):
        if rect[0][0] < center_x:
            center_x = rect[0][0]
            index = i

    return rectangles[index]


def get_customer_code_rect(rectangles):
    """
    Get customer code rectangle (お客さま番号). It is the most-bottom rectangle
    :param rectangles: List of rectangle: ((center_x, center_y), (width, height), angle)
    :return:
    """
    index = 0
    center_y = 0
    for i, rect in enumerate(rectangles):
        if center_y > rect[0][1]:
            center_y = rect[0][1]
            index = i

    return rectangles[index]


def ocr_eletricity_bill(image, debug=False, debug_output_dir=None):
    """
    Extract information from electricity bill
    :param image: 2D image array (BGR mode)
    :return: Extracted information:
        {
            'location_code': '',
            'customer_name': '',
            'customer_address': '',
            'customer_code': ''
        }
    """
    # find contours in the image
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_scale_image, (5, 5), 0)
    thresh_img_inv = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'thresh_inv.png'), thresh_img_inv)

    contours = cv2.findContours(thresh_img_inv.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]

    if debug:
        # Draw all contours
        imgcp = image.copy()
        for contour in contours:
            cv2.drawContours(imgcp, [contour], -1, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(debug_output_dir, 'all_contours.png'), imgcp)

    # Get anchor rectangles
    rects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        approx = img_utils.approximate_contour(contour)
        if len(approx) == 4 and area > 5000:
            rect = cv2.minAreaRect(contour)
            rects.append(rect)

    if debug:
        # Draw all rectangles
        for rect in rects:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(image, [box], 0, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(debug_output_dir, 'rectangles.png'), image)

    # Get notice label rect (電気ご使用のお知らせ). It is the most-left box
    notice_label_rect = get_notice_label_rect(rects)
    rotating_angle = img_utils.get_rotating_angle(notice_label_rect)
    notice_label_rect_center = notice_label_rect[shared_constants.RECT_CENTER]
    rotated_gray_img = img_utils.rotate_image(gray_scale_image, notice_label_rect_center, rotating_angle)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'rotated_notice_label_box.png'), rotated_gray_img)

    # Get location code (地点番号)
    notice_label_rect_width, notice_label_rect_height = img_utils.get_rectangle_size(notice_label_rect)
    location_code_box = [round(notice_label_rect_center[0] - notice_label_rect_width / 2),
                         round(notice_label_rect_center[1] - 1.5 * notice_label_rect_height),
                         round(2 * notice_label_rect_width),
                         round(notice_label_rect_height)]
    location_code_ocr = ocr_box(rotated_gray_img, location_code_box, box=constants.BOX_CODES['location_code'],
                                psm=4, debug=debug)

    if debug:
        print(location_code_ocr)
        # show_box(rotated_gray_img, location_code_box)
        save_box(rotated_gray_img, location_code_box,
                 os.path.join(debug_output_dir, 'location_code_box.png'))

    # Get customer name box (...様)
    customer_name_box = [round(notice_label_rect_center[0] + 0.5 * notice_label_rect_width),
                         round(notice_label_rect_center[1] - 0.5 * notice_label_rect_height),
                         round(notice_label_rect_width * 2.277),
                         round(notice_label_rect_height)]
    customer_name_ocr = ocr_box(rotated_gray_img, customer_name_box, box=constants.BOX_CODES['customer_name'],
                                psm=13, debug=debug)  # psm in [7,13] is good

    if debug:
        print(customer_name_ocr)
        # show_box(rotated_gray_img, customer_name_box)
        save_box(rotated_gray_img, customer_name_box,
                 os.path.join(debug_output_dir, 'name_box.png'))

    # Get customer address box (ご使用場所)
    customer_address_box = [round(notice_label_rect_center[0] - 0.5 * notice_label_rect_width),
                            round(notice_label_rect_center[1] + 0.5 * notice_label_rect_height),
                            round(notice_label_rect_width * 3.486),
                            round(notice_label_rect_height * 1.322)]

    customer_address_ocr = ocr_box(rotated_gray_img, customer_address_box, box=constants.BOX_CODES['customer_address'],
                                   psm=6, debug=debug)    # psm in [4, 6] is good

    if debug:
        print(customer_address_ocr)
        # show_box(rotated_gray_img, customer_address_box)
        save_box(rotated_gray_img, customer_address_box,
                 os.path.join(debug_output_dir, 'address_box.png'))

    # Get customer code rectangle (お客さま番号)
    customer_code_rect = get_customer_code_rect(rects)
    rotating_angle = img_utils.get_rotating_angle(customer_code_rect)
    customer_code_rect_center = customer_code_rect[shared_constants.RECT_CENTER]
    rotated_gray_img = img_utils.rotate_image(gray_scale_image, customer_code_rect_center, rotating_angle)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'rotated_customer_code_box.png'), rotated_gray_img)

    customer_code_rect_width, customer_code_rect_height = img_utils.get_rectangle_size(customer_code_rect)
    customer_code_box = [round(customer_code_rect_center[0] - customer_code_rect_width / 2),
                         round(customer_code_rect_center[1] - customer_code_rect_height / 2),
                         round(customer_code_rect_width),
                         round(customer_code_rect_height)]
    customer_code_ocr = ocr_box(rotated_gray_img, customer_code_box, box=constants.BOX_CODES['customer_code'],
                                psm=4, debug=debug)

    if debug:
        print(customer_code_ocr)
        # show_box(rotated_gray_img, customer_code_box)
        save_box(rotated_gray_img, customer_code_box,
                 os.path.join(debug_output_dir, 'customer_code_box.png'))

    if debug:
        result = {
            'location_code': location_code_ocr,
            'customer_name': customer_name_ocr,
            'customer_address': customer_address_ocr,
            'customer_code': customer_code_ocr,
        }
    else:
        result = {
            'location_code': correction_util.correct_location_code(location_code_ocr),
            'customer_name': correction_util.correct_customer_name(customer_name_ocr),
            'customer_address': correction_util.correct_customer_address(customer_address_ocr),
            'customer_code': correction_util.correct_customer_code(customer_code_ocr),
        }

    return result

