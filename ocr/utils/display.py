import cv2
import os
import datetime


def show_img(image_array, output_dir=None):
    cv2.imshow('image', image_array)

    key = cv2.waitKey(0)
    key = chr(key & 255)

    # if key == 'q':
    #     cv2.destroyAllWindows()

    # Capture image when press button 'c'
    if key == 'c':
        if output_dir:
            image_name = os.path.join(output_dir,
                                      datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S') + '.png')
            print(image_name)
            cv2.imwrite(image_name, image_array)
        # else:
        #     cv2.destroyAllWindows()

