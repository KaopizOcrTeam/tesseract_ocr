from PIL import Image, ImageFont, ImageDraw, ImageFilter, TiffImagePlugin, ImageEnhance
import ipdb
import numpy as np
import random
import argparse
import os
import glob
import shutil


def draw_text_play():
    text = 'おはようございます。\n' \
           'こんにちは。\n' \
           'ご誕生日おめでとうございます。'
    font = 'TextRecognitionDataGenerator/fonts/jp/TakaoGothic.ttf'
    text_color = (255, 0, 0)

    image_font = ImageFont.truetype(font=font, size=64, index=0)
    text_width, text_height = image_font.getsize(text)

    txt_img = Image.new('RGB', (text_width, text_height * 3), (0, 255, 0))

    txt_draw = ImageDraw.Draw(txt_img)

    txt_draw.text((0, 0), text, fill=text_color, font=image_font)

    txt_img.show()


def make_tif_play():
    text = 'おはようございます。\n' \
           'こんにちは。\n' \
           'ご誕生日おめでとうございます。'
    font = 'TextRecognitionDataGenerator/fonts/jp/TakaoGothic.ttf'
    text_color = (255, 0, 0)

    image_font = ImageFont.truetype(font=font, size=12, index=0)
    text_width, text_height = image_font.getsize(text)

    txt_img = Image.new('RGB', (text_width, text_height * 3), (0, 255, 0))

    txt_draw = ImageDraw.Draw(txt_img)

    txt_draw.text((0, 0), text, fill=text_color, font=image_font)

    with TiffImagePlugin.AppendingTiffWriter('./test.tif', True) as tf:
        txt_img = txt_img.convert('1')
        txt_img.save(tf)
        tf.newFrame()

    ipdb.set_trace()
    imgcp = Image.open('./test.tif')


def add_pepper_noise(image, row_freq=1, points_each_row_fraction=0.1):
    image_height = image.height
    image_width = image.width
    rec_draw = ImageDraw.Draw(image)
    for i in range(0, image_height, row_freq):
        x_candidates = random.sample(range(0, image_width), round(points_each_row_fraction * image_width))
        point_candidates = [(xc, i) for xc in x_candidates]
        rec_draw.point(point_candidates, fill=False)


def open_tiff_play(image_path, box_path, output_path, draw_boxes=False):
    img = Image.open(image_path, mode='r')

    # Initialize filter
    with TiffImagePlugin.AppendingTiffWriter(output_path, True) as tf:
        with open(box_path, 'r') as bf:
            findex = 0
            box_text = None
            new_page = False
            while True:
                try:
                    img.seek(findex)
                except Exception:
                    break
                frame = img
                # ipdb.set_trace()

                # TODO Add noise here
                add_pepper_noise(frame, row_freq=1, points_each_row_fraction=0.1)

                # Draw bounding boxes
                if draw_boxes:
                    rec_draw = ImageDraw.Draw(frame)
                    while True:
                        if not (box_text and new_page):
                            box_text = bf.readline().split('\n')[0]
                            if not box_text:
                                break

                        if new_page:
                            new_page = False

                        box_info = box_text.split(' ')
                        page = int(box_info[-1])

                        if page > findex:
                            new_page = True
                            break

                        if len(box_info) == 6 and box_info[0] != '\t':
                            xmin = int(box_info[1])
                            ymin = frame.height - int(box_info[2])
                            xmax = int(box_info[3])
                            ymax = frame.height - int(box_info[4])
                        elif len(box_info) == 7:
                            xmin = int(box_info[2])
                            ymin = frame.height - int(box_info[3])
                            xmax = int(box_info[4])
                            ymax = frame.height - int(box_info[5])

                        rec_draw.rectangle([xmin, ymin, xmax, ymax])

                frame.save(tf)
                tf.newFrame()

                findex += 1


parser = argparse.ArgumentParser()
parser.add_argument('--training_dir', required=True, default='', type=str,
                    help='Path to training directory that contains .tif and .box files')


if __name__ == '__main__':
    # image_path = '/home/bang/projects/python/tesseract_test/training/tepco_201808221323/data/jpn.GenEi_Koburi_Mincho.exp0.tif'
    # box_path = '/home/bang/projects/python/tesseract_test/training/tepco_201808221323/data/jpn.GenEi_Koburi_Mincho.exp0.box'
    # output_path = '/home/bang/projects/python/tesseract_test/storage/out/out.tif'
    #
    # open_tiff_play(image_path, box_path, output_path, draw_boxes=False)

    # Parse arguments
    args = parser.parse_args()
    training_dir = args.training_dir.strip()

    if training_dir == '':
        raise Exception('Please enter a valid value for --training_dir')

    if not os.path.exists(training_dir):
        raise Exception('{} do not exist'.format(training_dir))

    # Params for adding pepper noise    (row_freq, points_per_row_fraction)
    pepper_noise_settings = [
        (1, 0.1),
        (1, 0.05),
        (5, 0.1),
        (5, 0.05),
    ]

    # Get all .tif files in the training directory
    tif_files = glob.glob(os.path.join(training_dir, '*.tif'))
    for tif_file in tif_files:
        # file_name_without_extension = os.path.basename(tif_file).replace('.tif', '')
        file_path_without_extension = tif_file.replace('.tif', '')
        box_file = file_path_without_extension + '.box'

        tif_img = Image.open(tif_file, mode='r')
        for pepper_noise_setting in pepper_noise_settings:
            # Copy box file
            out_box_file = file_path_without_extension + '_pepper-{}-{}.box'.format(pepper_noise_setting[0],
                                                                                    pepper_noise_setting[1])
            shutil.copyfile(box_file, out_box_file)

            # Make new .tif file with noise
            out_tif_file = file_path_without_extension + '_pepper-{}-{}.tif'.format(pepper_noise_setting[0],
                                                                                    pepper_noise_setting[1])
            with TiffImagePlugin.AppendingTiffWriter(out_tif_file, True) as tf:
                findex = 0
                while True:
                    try:
                        tif_img.seek(findex)
                    except Exception:
                        break
                    frame = tif_img.copy()

                    # Add noise
                    add_pepper_noise(frame, row_freq=pepper_noise_setting[0],
                                     points_each_row_fraction=pepper_noise_setting[1])

                    frame.save(tf)
                    tf.newFrame()

                    findex += 1
