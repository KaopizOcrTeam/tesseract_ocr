import cv2
from ocr.jp_driver_license.tesseract_ocr import ocr_driver_license
from ocr.jp_driver_license.display_util import display_ocr_result


if __name__ == '__main__':
    # Able to get main box: 1,2,4,5,6,7,8-1,8-2,8-3,8-4,11,13,15,16,17,18,19,21,25,26,27,28,29
    # Only get the name box:
    # All card as main box: 9,10,12,14,20,22,23
    # NG: 3,21-3,21-4,24
    image_paths = [
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver1.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver2.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver4.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver5.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver6.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver7.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-1.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-2.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-3.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver8-4.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver9.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver10.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver11.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver12.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver13.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver14.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver15.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver16.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver17.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver18.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver19.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver20.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-1.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver21-2.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver22.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver23.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver25.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver26.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver27.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver28.jpg',
        '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/driver29.jpg',
    ]

    debug_output_dir = '/home/bang/projects/python/tesseract_test/storage/images/driver_lisence/out'
    debug = False

    i = -1
    while True:
        i += 1
        if i == len(image_paths):
            break

        image_path = image_paths[i]

        if image_path == 'q':
            exit(0)

        print('#### {}   ####'.format(image_path))

        bgr_img = cv2.imread(image_path)

        extracted_info = ocr_driver_license(bgr_img, debug=debug, debug_output_dir=debug_output_dir)

        display_ocr_result(extracted_info)


