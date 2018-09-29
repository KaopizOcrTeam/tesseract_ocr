"""
References:
    * https://www.pyimagesearch.com/2015/11/30/detecting-machine-readable-zones-in-passport-images/
"""
import cv2
from ocr.tepco_bill import constants, config
from ocr.tepco_bill.tesseract_ocr import find_roi, get_binary_image
from ocr.utils.image import rescale_image
from ocr.utils.tesseract import call_tesseract_command


if __name__ == '__main__':

    image_paths = [
        # '/home/bang/projects/python/tesseract_test/storage/images/tepco/out/customer_code_box.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/tepco/out/location_code_box.png',
        '/home/bang/projects/python/tesseract_test/storage/images/tepco/out/name_box.png',
        # '/home/bang/projects/python/tesseract_test/storage/images/tepco/out/address_box.png',
    ]

    i = -1
    while True:
        i += 1
        if i == len(image_paths):
            break

        image_path = image_paths[i]
        print('#### {}   ####'.format(image_path))

        if image_path == 'q':
            exit(0)

        bgr_image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # Rescaling
        gray_image = rescale_image(gray_image, min_height=125)

        # Blur image
        blur_image = cv2.medianBlur(gray_image, 3)

        # Find ROI
        roi = find_roi(blur_image, debug=True)

        # convert ROI to bw image
        bw_roi = get_binary_image(roi, box=constants.BOX_CODES['customer_name'], debug=True)
        # bw_roi = get_binary_image(roi, box=constants.BOX_CODES['customer_address'], debug=True)
        # bw_roi = get_binary_image(blur_image, box=constants.BOX_CODES['customer_code'], debug=True)

        result = call_tesseract_command(bw_roi, tessdata_dir=config.tessdata_dir, lang='jpn+eng', psm=13)

        print(result)

