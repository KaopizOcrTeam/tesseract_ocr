import cv2
import numpy as np
import os
from . import constants
from .display import show_img


def approximate_contour(c, fraction=0.04):
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, fraction * peri, True)

    return approx


def rotate_image(image_array, center, angle):
    """
    Rotate image around a center
    :param image_array:
    :param center: center to rotate: (center_x, center_y)
    :param angle: angle to rotate
    :return: rotated image array
    """
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image_array, M, (image_array.shape[1], image_array.shape[0]),
                                   flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated_image


def get_rotating_angle(rect):
    """
    Get true rotating angle for the rectangle
    :param rect: A min area rectangle: ((center_x, center_y), (width, height), angle)
    :return:
    """
    angle = rect[constants.RECT_ANGLE]
    if angle < -45:
        rotating_angle = 90 + angle
    else:
        rotating_angle = angle

    return rotating_angle


def get_rectangle_size(rect):
    """

    :param rect: A min area rectangle: ((center_x, center_y), (width, height), angle)
    :return: (rect_width, rect_height), with rect_width > rect_height
    """
    if rect[constants.RECT_SIZE][0] > rect[constants.RECT_SIZE][1]:
        return rect[constants.RECT_SIZE][0], rect[constants.RECT_SIZE][1]
    else:
        return rect[constants.RECT_SIZE][1], rect[constants.RECT_SIZE][0]


def rescale_image(image_array, min_height=150):
    height, width = image_array.shape
    factor = min_height / height
    if height < min_height:
        res = cv2.resize(image_array, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
        return res
    else:
        return image_array


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped


def auto_canny(image_array, sigma=0.33):
    v = np.median(image_array)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))

    edged_img = cv2.Canny(image_array, lower, upper)

    return edged_img


def get_roi_area(image_array, xmin_fraction=0, xmax_fraction=1, ymin_fraction=0, ymax_fraction=1,
                 debug=False, debug_output_dir=None, area_name='roi_area'):
    image_height, image_width = image_array.shape

    area_xmin = int(image_width * xmin_fraction)
    area_xmax = int(image_width * xmax_fraction)
    area_ymin = int(image_height * ymin_fraction)
    area_ymax = int(image_height * ymax_fraction)

    area = image_array[area_ymin:area_ymax, area_xmin:area_xmax]

    if debug and debug_output_dir:
        cv2.imwrite(os.path.join(debug_output_dir, '{}.png'.format(area_name)), area)

    return area

