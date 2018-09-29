import pytesseract
import re


def call_tesseract_command(image_array, tessdata_dir=None, lang='eng', psm=4):
    """

    :param image_array:
    :param lang:
    :param psm:
    :return:
    """
    pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

    if not tessdata_dir:
        tessdata_dir = '/usr/local/share/tessdata'

    tessdata_dir_option = '--tessdata-dir {}'.format(tessdata_dir)

    configuration = '{} --oem 1 --psm {} -c chop_enable=t -c use_new_state_cost=f -c segment_segcost_rating=f ' \
                    '-c enable_new_segsearch=0 -c language_model_ngram_on=0 -c textord_force_make_prop_words=F ' \
                    '-c edges_max_children_per_outline=40'.format(tessdata_dir_option, psm)

    text = pytesseract.image_to_string(image_array, lang=lang, config=configuration)

    consecutive_new_lines_pattern = re.compile(r'\n\n+')
    text = consecutive_new_lines_pattern.sub('\n', text)

    return text

