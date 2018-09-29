import cv2
from ..utils.display import show_img


def show_box(image_array, left_top_width_height, output_dir=None):
    box_img = image_array[left_top_width_height[1]:(left_top_width_height[1] + left_top_width_height[3]),
                          left_top_width_height[0]:(left_top_width_height[0] + left_top_width_height[2])]
    show_img(box_img, output_dir=output_dir)


def save_box(image_array, left_top_width_height, output_path):
    """

    :param image_array:
    :param left_top_width_height:
    :param output_path:
    :return:
    """
    box_img = image_array[left_top_width_height[1]:(left_top_width_height[1] + left_top_width_height[3]),
                          left_top_width_height[0]:(left_top_width_height[0] + left_top_width_height[2])]
    cv2.imwrite(output_path, box_img)


def display_ocr_result(ocr_result):
    """

    :param ocr_result:
        {
            'location_code': '',
            'customer_name': '',
            'customer_address': '',
            'customer_code': ''
        }
    :return:
    """
    keys = ['location_code', 'customer_code', 'customer_name', 'customer_address']
    for key in keys:
        print('## {} ##:\n'.format(key))
        print('{}\n'.format(ocr_result[key]))

