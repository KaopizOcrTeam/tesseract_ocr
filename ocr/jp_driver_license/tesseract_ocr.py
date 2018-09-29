import imutils
import os
import numpy as np
import cv2
from ..utils.display import show_img
from ..utils.image import four_point_transform, approximate_contour, get_roi_area, rescale_image
from ..utils.geometry import get_cross_point, get_line_slope, get_anchor_lines
from ..utils.tesseract import call_tesseract_command
from . import correction_util, config


def get_main_boxes(bgr_image, debug=False, debug_output_dir=None):
    # find contours in the image
    gray_img = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Find the main contour
    thresh_img_inv = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 2)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'thresh_inv.png'), thresh_img_inv)

    contours = cv2.findContours(thresh_img_inv.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    if debug:
        # Draw largest contours
        imgcp = bgr_image.copy()
        for i, contour in enumerate(contours):
            cv2.drawContours(imgcp, [contour], -1, (0, 255, 0), 1)
        cv2.imwrite(os.path.join(debug_output_dir, 'largest_contours.png'), imgcp)
        # for i, contour in enumerate(contours):
        #     imgcp = bgr_image.copy()
        #     cv2.drawContours(imgcp, [contour], -1, (0, 255, 0), 5)
        #     cv2.imwrite(os.path.join(debug_output_dir, 'contour_{}.png'.format(i)), imgcp)

    # Consider the case when the largest contour is the border of the whole card
    min_min_y = 9999999999999999
    min_min_y_index = -1
    for i, cnt in enumerate(contours):
        min_y = min(cnt[:, 0, 1])

        if min_y < min_min_y:
            min_min_y = min_y
            min_min_y_index = i

    if min_min_y_index == 0:
        # Case 1: The largest contour is the border of the whole card
        cnt_area_0 = cv2.contourArea(contours[0])
        cnt_area_1 = cv2.contourArea(contours[1])

        card_approx = approximate_contour(contours[0], fraction=0.002)

        if cnt_area_1 / cnt_area_0 > 0.9 or len(card_approx) > 11:
            card_approx = approximate_contour(contours[1], fraction=0.002)

        if debug:
            imgcp_contours_appox = bgr_image.copy()
            cv2.drawContours(imgcp_contours_appox, [card_approx], 0, (0, 255, 0), 5)
            cv2.imwrite(os.path.join(debug_output_dir, 'card_contours_approx.png'), imgcp_contours_appox)

        # Get anchor lines of the card
        card_anchor_lines, card_anchor_dists = get_anchor_lines(card_approx.reshape(len(card_approx), 2), quantity=4)

        if debug:
            # Draw all anchor lines
            imgcp_anchor_line = bgr_image.copy()
            for line in card_anchor_lines:
                cv2.line(imgcp_anchor_line, line[0], line[1], (0, 255, 0), thickness=10)
            cv2.imwrite(os.path.join(debug_output_dir, 'card_anchor_lines.png'), imgcp_anchor_line)

        # Get cross points of card
        card_cross_points = []
        anchor_line_num = len(card_anchor_lines)
        for i in range(anchor_line_num):
            cross_p = get_cross_point(card_anchor_lines[i], card_anchor_lines[(i + 1) % anchor_line_num])
            card_cross_points.append(cross_p)
        card_cross_points = np.array(card_cross_points)

        # 4 points transforming the card
        gray_card = four_point_transform(gray_img, card_cross_points)

        if debug:
            cv2.imwrite(os.path.join(debug_output_dir, 'gray_card.png'), gray_card)

        # Get main box and name box
        gray_name_box = get_roi_area(gray_card,
                                     xmin_fraction=0.03140773976444195, xmax_fraction=0.96578799775659,
                                     ymin_fraction=0.055, ymax_fraction=0.133883,
                                     debug=debug, debug_output_dir=debug_output_dir, area_name='gray_name_box')
        gray_main_box = get_roi_area(gray_card,
                                     xmin_fraction=0.03140773976444195, xmax_fraction=0.96578799775659,
                                     ymin_fraction=0.203913491246138, ymax_fraction=0.9420111042566317,
                                     debug=debug, debug_output_dir=debug_output_dir, area_name='gray_main_box')

        return gray_name_box, gray_main_box

    # Case 2: The largest contour is the border of the main box
    # Get contour for name box and contour for main box
    main_box_contour = cv2.convexHull(contours[0])

    main_contour_min_y = min(main_box_contour[:, 0, 1])
    name_box_contour = None
    for i in range(1, len(contours)):
        contour_min_y = min(contours[i][:, 0, 1])
        if contour_min_y < main_contour_min_y:
            name_box_approx = approximate_contour(contours[i], fraction=0.002)
            if len(name_box_approx) < 12:
                name_box_contour = contours[i]
                break

    if debug:
        imgcp = bgr_image.copy()
        cv2.drawContours(imgcp, [main_box_contour], -1, (0, 255, 0), 10)
        cv2.drawContours(imgcp, [name_box_contour], -1, (0, 0, 255), 10)
        cv2.imwrite(os.path.join(debug_output_dir, 'main_contours.png'), imgcp)

        imgcp_contours_appox = bgr_image.copy()
        cv2.drawContours(imgcp_contours_appox, [name_box_approx], 0, (0, 0, 255), 10)

    # Get anchor lines of the name box
    name_box_anchor_lines, name_box_anchor_dists = get_anchor_lines(name_box_approx.reshape(len(name_box_approx), 2),
                                                                    quantity=2)

    if debug:
        # Draw all anchor lines
        imgcp_anchor_line = bgr_image.copy()
        for line in name_box_anchor_lines:
            cv2.line(imgcp_anchor_line, line[0], line[1], (0, 0, 255), thickness=10)

    # Approximate the main box contour
    approx = approximate_contour(main_box_contour, fraction=0.002)

    if debug:
        cv2.drawContours(imgcp_contours_appox, [approx], 0, (0, 255, 0), 5)
        cv2.imwrite(os.path.join(debug_output_dir, 'main_contours_approx.png'), imgcp_contours_appox)

    # Get anchor lines of the main box
    main_box_anchor_lines, main_box_anchor_dists = get_anchor_lines(approx.reshape(len(approx), 2), quantity=4)

    if debug:
        # Draw all anchor lines
        for line in main_box_anchor_lines:
            cv2.line(imgcp_anchor_line, line[0], line[1], (0, 255, 0), thickness=10)
        cv2.imwrite(os.path.join(debug_output_dir, 'main_anchor_lines.png'), imgcp_anchor_line)

    # Get cross points of the name box
    name_box_anchor_line_slope = get_line_slope(name_box_anchor_lines[0])
    main_anchor_line_slope_diffs = \
        [abs(get_line_slope(line) - name_box_anchor_line_slope) for line in main_box_anchor_lines]
    main_box_vertical_line_indexes = sorted(
        sorted(range(len(main_box_anchor_lines)), key=lambda k: main_anchor_line_slope_diffs[k], reverse=True)[:2])

    name_box_cross_points = []
    indexes = [(1, 0), (0, 0), (0, 1), (1, 1)]
    for index in indexes:
        name_box_cross_points.append(get_cross_point(name_box_anchor_lines[index[0]],
                                                     main_box_anchor_lines[main_box_vertical_line_indexes[index[1]]]))
    name_box_cross_points = np.array(name_box_cross_points)

    # 4 points transforming the name box
    gray_name_box = four_point_transform(gray_img, name_box_cross_points)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'gray_name_box.png'), gray_name_box)

    # Get cross points of main box
    main_box_cross_points = []
    anchor_line_num = len(main_box_anchor_lines)
    for i in range(anchor_line_num):
        cross_p = get_cross_point(main_box_anchor_lines[i], main_box_anchor_lines[(i + 1) % anchor_line_num])
        main_box_cross_points.append(cross_p)
    main_box_cross_points = np.array(main_box_cross_points)

    # 4 points transforming the main box
    gray_main_box = four_point_transform(gray_img, main_box_cross_points)

    if debug:
        cv2.imwrite(os.path.join(debug_output_dir, 'gray_main_box.png'), gray_main_box)

    return gray_name_box, gray_main_box


def _extract_full_name(blur_image, debug=False, debug_output_dir=None):
    # Get full_name area
    full_name_area = get_roi_area(blur_image,
                                  xmin_fraction=0.0853548966756514, xmax_fraction=0.6159029649595688,
                                  ymin_fraction=0.12307692307692308, ymax_fraction=1,
                                  debug=debug, debug_output_dir=debug_output_dir, area_name='area_full_name')

    full_name_area = rescale_image(full_name_area, min_height=150)

    if debug:
        show_img(full_name_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(full_name_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_full_name = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_full_name


def _extract_date_of_birth(blur_image, debug=False, debug_output_dir=None):
    # Get date_of_birth area
    date_of_birth_area = get_roi_area(blur_image,
                                      xmin_fraction=0.6458604247941049, xmax_fraction=0.9926311226701344,
                                      ymin_fraction=0.12307692307692308, ymax_fraction=1,
                                      debug=debug, debug_output_dir=debug_output_dir, area_name='area_date_of_birth')

    date_of_birth_area = rescale_image(date_of_birth_area, min_height=150)

    if debug:
        show_img(date_of_birth_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(date_of_birth_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_date_of_birth = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_date_of_birth


def ocr_name_box(name_box, debug=False, debug_output_dir=None):
    blur_image = cv2.medianBlur(name_box, 3)

    # Extract full name
    ocr_full_name = _extract_full_name(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract date of birth
    ocr_date_of_birth = _extract_date_of_birth(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    if debug:
        ocr_results = {
            'full_name': ocr_full_name,
            'date_of_birth': ocr_date_of_birth,
        }
    else:
        ocr_results = {
            'full_name': correction_util.correct_full_name(ocr_full_name),
            'date_of_birth': correction_util.correct_date_of_birth(ocr_date_of_birth),
        }

    return ocr_results


def _extract_address(blur_image, debug=False, debug_output_dir=None):
    # Get address area
    address_area = get_roi_area(blur_image,
                                xmin_fraction=0.09084556254367575, xmax_fraction=0.9636617749825297,
                                ymin_fraction=0.008347245409015025, ymax_fraction=0.09682804674457429,
                                debug=debug, debug_output_dir=debug_output_dir, area_name='area_address')

    address_area = rescale_image(address_area, min_height=150)

    if debug:
        show_img(address_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(address_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           111, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_address = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_address


def _extract_issue_date(blur_image, debug=False, debug_output_dir=None):
    # Get issue date
    issue_date_area = get_roi_area(blur_image,
                                   xmin_fraction=0.0873515, xmax_fraction=0.46518305814788224,
                                   ymin_fraction=0.10684474, ymax_fraction=0.1903172,
                                   debug=debug, debug_output_dir=debug_output_dir, area_name='area_issue_date')

    issue_date_area = rescale_image(issue_date_area, min_height=200)

    if debug:
        show_img(issue_date_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(issue_date_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_issue_date = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_issue_date


def _extract_inquiry_number(blur_image, debug=False, debug_output_dir=None):
    inquiry_number_area = get_roi_area(blur_image,
                                       xmin_fraction=0.46518305814788224, xmax_fraction=0.6740847092605886,
                                       ymin_fraction=0.10271460014673514, ymax_fraction=0.19075568598679385,
                                       debug=debug, debug_output_dir=debug_output_dir, area_name='area_inquiry_number')

    inquiry_number_area = rescale_image(inquiry_number_area, min_height=150)

    if debug:
        show_img(inquiry_number_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(inquiry_number_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=3)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_inquiry_number = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_inquiry_number


def _extract_expiration_date(blur_image, debug=False, debug_output_dir=None):
    expiration_date_area = get_roi_area(blur_image,
                                        xmin_fraction=0.0041928721174004195, xmax_fraction=0.6317260656883298,
                                        ymin_fraction=0.19699499165275458, ymax_fraction=0.31552587646076796,
                                        debug=debug, debug_output_dir=debug_output_dir, area_name='area_expiration_date')

    expiration_date_area = rescale_image(expiration_date_area, min_height=150)

    if debug:
        show_img(expiration_date_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(expiration_date_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_expiration_date = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_expiration_date


def _extract_menkyono(blur_image, debug=False, debug_output_dir=None):
    menkyono_area = get_roi_area(blur_image,
                                       xmin_fraction=0.07966457023060797, xmax_fraction=0.63382250174703,
                                       ymin_fraction=0.32387312186978295, ymax_fraction=0.4056761268781302,
                                       debug=debug, debug_output_dir=debug_output_dir, area_name='area_menkyono')

    menkyono_area = rescale_image(menkyono_area, min_height=150)

    if debug:
        show_img(menkyono_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(menkyono_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=1)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_menkyono = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_menkyono


def _extract_joukentou(blur_image, debug=False, debug_output_dir=None):
    joukentou_area = get_roi_area(blur_image,
                                  xmin_fraction=0.08245981830887492, xmax_fraction=0.6317260656883298,
                                  ymin_fraction=0.4023372287145242, ymax_fraction=0.48747913188647746,
                                  debug=debug, debug_output_dir=debug_output_dir, area_name='area_joukentou')

    joukentou_area = rescale_image(joukentou_area, min_height=150)

    if debug:
        show_img(joukentou_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(joukentou_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           51, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_joukentou = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_joukentou


def _extract_nishogen_issue_date(blur_image, debug=False, debug_output_dir=None):
    nishogen_issue_date_area = get_roi_area(blur_image,
                                            xmin_fraction=0.06281407035175879, xmax_fraction=0.3535534816941852,
                                            ymin_fraction=0.7571533382245048, ymax_fraction=0.8481291269258987,
                                            debug=debug, debug_output_dir=debug_output_dir,
                                            area_name='area_nishogen_issue_date')

    nishogen_issue_date_area = rescale_image(nishogen_issue_date_area, min_height=200)

    if debug:
        show_img(nishogen_issue_date_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(nishogen_issue_date_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_nishogen_issue_date = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_nishogen_issue_date


def _extract_other_issue_date(blur_image, debug=False, debug_output_dir=None):
    other_issue_date_area = get_roi_area(blur_image,
                                         xmin_fraction=0.06353194544149318, xmax_fraction=0.3546302943287868,
                                         ymin_fraction=0.8437270726338958, ymax_fraction=0.921496698459281,
                                         debug=debug, debug_output_dir=debug_output_dir,
                                         area_name='area_other_issue_date')

    other_issue_date_area = rescale_image(other_issue_date_area, min_height=200)

    if debug:
        show_img(other_issue_date_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(other_issue_date_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_other_issue_date = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_other_issue_date


def _extract_nishu_issue_date(blur_image, debug=False, debug_output_dir=None):
    nishu_issue_date_area = get_roi_area(blur_image,
                                         xmin_fraction=0.06353194544149318, xmax_fraction=0.3546302943287868,
                                         ymin_fraction=0.921496698459281, ymax_fraction=1,
                                         debug=debug, debug_output_dir=debug_output_dir,
                                         area_name='area_nishu_issue_date')

    nishu_issue_date_area = rescale_image(nishu_issue_date_area, min_height=200)

    if debug:
        show_img(nishu_issue_date_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(nishu_issue_date_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_nishu_issue_date = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=13)

    return ocr_nishu_issue_date


def _extract_issue_office(blur_image, debug=False, debug_output_dir=None):
    issue_office_area = get_roi_area(blur_image,
                                     xmin_fraction=0.6876310272536688, xmax_fraction=0.9091544374563243,
                                     ymin_fraction=0.8631051752921536, ymax_fraction=0.994991652754591,
                                     debug=debug, debug_output_dir=debug_output_dir,
                                     area_name='area_issue_office')

    issue_office_area = rescale_image(issue_office_area, min_height=120)

    if debug:
        show_img(issue_office_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(issue_office_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           51, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=1)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_issue_office = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=6)

    return ocr_issue_office


def _extract_license_number(blur_image, debug=False, debug_output_dir=None):
    license_number_area = get_roi_area(blur_image,
                                       xmin_fraction=0.12928022361984626, xmax_fraction=0.5443745632424878,
                                       ymin_fraction=0.6293823038397329, ymax_fraction=0.7462437395659433,
                                       debug=debug, debug_output_dir=debug_output_dir,
                                       area_name='area_license_number')

    license_number_area = rescale_image(license_number_area, min_height=150)

    if debug:
        show_img(license_number_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(license_number_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=3)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_license_number = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='eng', psm=13)

    return ocr_license_number


def _extract_allowed_types(blur_image, debug=False, debug_output_dir=None):
    allowed_types_area = get_roi_area(blur_image,
                                      xmin_fraction=0.3948312993539124, xmax_fraction=0.6378320172290022,
                                      ymin_fraction=0.7696258253851798, ymax_fraction=0.9882611885546588,
                                      debug=debug, debug_output_dir=debug_output_dir,
                                      area_name='area_allowed_types')

    allowed_types_area = rescale_image(allowed_types_area, min_height=300)

    if debug:
        show_img(allowed_types_area, output_dir=debug_output_dir)

    processed_area = cv2.adaptiveThreshold(allowed_types_area, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                           31, 2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    processed_area = cv2.morphologyEx(processed_area, op=cv2.MORPH_OPEN, kernel=kernel, anchor=(-1, -1), iterations=2)

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    processed_area = 255 - processed_area

    if debug:
        show_img(processed_area, output_dir=debug_output_dir)

    ocr_allowed_types = call_tesseract_command(processed_area, tessdata_dir=config.tessdata_dir, lang='jpn', psm=11)

    return ocr_allowed_types


def ocr_main_box(main_box, debug=False, debug_output_dir=None):
    blur_image = cv2.medianBlur(main_box, 3)

    if debug:
        show_img(blur_image, output_dir=debug_output_dir)

    # Extract address
    ocr_address = _extract_address(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract issue date
    ocr_issue_date = _extract_issue_date(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract inquiry number (照会番号)
    # https://gazoo.com/article/daily/150907.html
    ocr_inquiry_number = _extract_inquiry_number(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract expiration date
    ocr_expiration_date = _extract_expiration_date(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract menkyono
    ocr_menkyono = _extract_menkyono(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract joukentou
    ocr_joukentou = _extract_joukentou(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract 二・小・原取得日付, 他取得日付, 二種取得日付
    ocr_nishogen_issue_date = _extract_nishogen_issue_date(blur_image, debug=debug, debug_output_dir=debug_output_dir)
    ocr_other_issue_date = _extract_other_issue_date(blur_image, debug=debug, debug_output_dir=debug_output_dir)
    ocr_nishu_issue_date = _extract_nishu_issue_date(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract issue office
    ocr_issue_office = _extract_issue_office(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract license number
    ocr_license_number = _extract_license_number(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    # Extract allowed types
    ocr_allowed_types = _extract_allowed_types(blur_image, debug=debug, debug_output_dir=debug_output_dir)

    if debug:
        ocr_results = {
            'address': ocr_address,
            'issue_date': ocr_issue_date,
            'inquiry_number': ocr_inquiry_number,
            'expiration_date': ocr_expiration_date,
            'menkyono': ocr_menkyono,
            'joukentou': ocr_joukentou,
            'license_number': ocr_license_number,
            'nishogen_issue_date': ocr_nishogen_issue_date,
            'other_issue_date': ocr_other_issue_date,
            'nishu_issue_date': ocr_nishu_issue_date,
            'issue_office': ocr_issue_office,
            'allowed_types': ocr_allowed_types,
        }
    else:
        ocr_results = {
            'address': correction_util.correct_address(ocr_address),
            'issue_date': correction_util.correct_issue_date(ocr_issue_date),
            'inquiry_number': correction_util.correct_inquiry_number(ocr_inquiry_number),
            'expiration_date': correction_util.correct_expiration_date(ocr_expiration_date),
            'menkyono': correction_util.correct_menkyono(ocr_menkyono),
            'joukentou': correction_util.correct_joukentou(ocr_joukentou),
            'license_number': correction_util.correct_license_number(ocr_license_number),
            'nishogen_issue_date': correction_util.correct_nishogen_issue_date(ocr_nishogen_issue_date),
            'other_issue_date': correction_util.correct_other_issue_date(ocr_other_issue_date),
            'nishu_issue_date': correction_util.correct_nishu_issue_date(ocr_nishu_issue_date),
            'issue_office': correction_util.correct_issue_office(ocr_issue_office),
            'allowed_types': correction_util.correct_allowed_types(ocr_allowed_types),
        }

    return ocr_results


def ocr_driver_license(bgr_image, debug=False, debug_output_dir=None):
    # Get main boxes
    gray_name_box, gray_main_box = get_main_boxes(bgr_image, debug=debug, debug_output_dir=debug_output_dir)

    # Do OCR for name box
    name_box_text = ocr_name_box(gray_name_box, debug=debug, debug_output_dir=debug_output_dir)

    # Do OCR for main box
    main_box_text = ocr_main_box(gray_main_box, debug=debug, debug_output_dir=debug_output_dir)

    main_box_text.update(name_box_text)

    return main_box_text

