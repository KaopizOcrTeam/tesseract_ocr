"""
References:
    * https://www.pyimagesearch.com/2015/11/30/detecting-machine-readable-zones-in-passport-images/
"""
import cv2
from ocr.jp_driver_license import correction_util, tesseract_ocr
from ocr.jp_driver_license.tesseract_ocr import get_main_boxes
import traceback


def play_box(gray_img, debug=False):
    blur_image = cv2.medianBlur(gray_img, 3)

    # ocr_text = tesseract_ocr._extract_full_name(blur_image, debug=debug)
    # ocr_text = correction_util.correct_full_name(ocr_text)

    # ocr_text = tesseract_ocr._extract_date_of_birth(blur_image, debug=debug)
    # ocr_text = correction_util.correct_date_of_birth(ocr_text)

    # ocr_text = tesseract_ocr._extract_address(blur_image, debug=debug)
    # ocr_text = correction_util.correct_address(ocr_text)

    # ocr_text = tesseract_ocr._extract_issue_date(blur_image, debug=debug)
    # ocr_text = correction_util.correct_issue_date(ocr_text)

    # ocr_text = tesseract_ocr._extract_inquiry_number(blur_image, debug=debug)
    # ocr_text = correction_util.correct_inquiry_number(ocr_text)

    # ocr_text = tesseract_ocr._extract_expiration_date(blur_image, debug=debug)
    # ocr_text = correction_util.correct_expiration_date(ocr_text)

    # ocr_text = tesseract_ocr._extract_menkyono(blur_image, debug=debug)
    # ocr_text = tesseract_ocr._extract_joukentou(blur_image, debug=debug)

    # ocr_text = tesseract_ocr._extract_nishogen_issue_date(blur_image, debug=debug)
    # ocr_text = correction_util.correct_nishogen_issue_date(ocr_text)

    # ocr_text = tesseract_ocr._extract_other_issue_date(blur_image, debug=debug)
    # ocr_text = correction_util.correct_other_issue_date(ocr_text)

    # ocr_text = tesseract_ocr._extract_nishu_issue_date(blur_image, debug=debug)
    # ocr_text = correction_util.correct_nishu_issue_date(ocr_text)

    # ocr_text = tesseract_ocr._extract_license_number(blur_image, debug=debug)
    # ocr_text = correction_util.correct_license_number(ocr_text)

    ocr_text = tesseract_ocr._extract_issue_office(blur_image, debug=debug)
    ocr_text = correction_util.correct_issue_office(ocr_text)

    # ocr_text = tesseract_ocr._extract_allowed_types(blur_image, debug=debug)

    print(ocr_text)


def play_box_detection(bgr_img, debug=False, debug_output_dir=None):
    gray_name_box, gray_main_box = get_main_boxes(bgr_img, debug=debug, debug_output_dir=debug_output_dir)


if __name__ == '__main__':

    image_paths = [
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_2.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_4.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_7.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_8-1.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_8-2.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_11.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_12.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_15.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_16.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_17.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_18.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_19.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_20.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_21.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_22.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_25.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_26.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_name_box_29.png',

        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_2.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_4.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_7.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_8-1.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_8-2.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_11.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_12.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_15.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_16.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_17.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_18.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_19.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_20.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_21.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_22.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_25.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_26.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out/gray_main_box_29.png',

        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver1.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver2.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver4.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver5.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver7.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver6.jpg', # (main contour not convex)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-1.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-2.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-3.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-4.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver9.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver10.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver11.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver12.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver13.jpg', # (main contour not convex)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver14.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver15.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver16.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver17.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver18.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver19.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver20.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-1.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-2.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver22.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver23.jpg', (too bright)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver25.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver26.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver27.jpg', # (main contour not convex)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver28.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver29.jpg',
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver3.jpg', # NG (bad image)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver24.jpg', # NG Hard (too bright)
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-3.jpg',  # NG
        # '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-4.jpg',   # NG
    ]

    debug = True
    debug_output_dir = '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out'

    i = -1
    while True:
        i += 1
        if i == len(image_paths):
            break

        image_path = image_paths[i]
        print('#### {}   ####'.format(image_path))

        if image_path == 'q':
            exit(0)

        bgr_img = cv2.imread(image_path)

        # gray_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        # play_box(gray_img, debug=debug)

        try:
            play_box_detection(bgr_img, debug=debug, debug_output_dir=debug_output_dir)
        except Exception:
            print(traceback.format_exc())

        input('Press any key to continue: ')


