import cv2
from ocr.tepco_bill.tesseract_ocr import ocr_eletricity_bill
from ocr.tepco_bill.display_util import display_ocr_result


if __name__ == '__main__':
    debug = True
    output_dir = './storage/images/tepco/out'

    image_paths = [
        # './storage/images/tepco/tepco-err.jpg',
        # './storage/images/tepco/tepco0.jpg',
        './storage/images/tepco/tepco1.jpg',
        # './storage/images/tepco/tepco2.jpg',   # Fail to extract boxes
        # './storage/images/tepco/tepco3.jpg',
        # './storage/images/tepco/tepco4.jpg',
        # './storage/images/tepco/tepco5.jpg',   # Fail to extract boxes
        # './storage/images/tepco/tepco6.jpg',
        # './storage/images/tepco/tepco7.jpg',
        # './storage/images/tepco/tepco8.jpg',
        # './storage/images/tepco/tepco9.jpg',    # Bigger seems to be better??
        # './storage/images/tepco/tepco10.jpg',
        # './storage/images/tepco/tepco_scan1.png',
        # './storage/images/tepco/tepco_scan2.png',
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

        image = cv2.imread(image_path)
        ocr_result = ocr_eletricity_bill(image, debug=debug, debug_output_dir=output_dir)

        display_ocr_result(ocr_result)
