import faker
import random
import os
from datetime import datetime
from decouple import config
import utils.constants as constants
# import constants as constants


def fake_person_names(quantity, output_file=None, locale='ja_JP', seed=None):
    """
    Generate a list of person names
    :param quantity: number of generated names
    :param output_file: path to output file
    :return:
        - if output_file is None: return a list of person names, otherwise write generated names to output_file
    """

    generator = faker.Faker(locale)

    if seed:
        generator.seed(seed)

    if output_file:
        with open(output_file, 'w') as f:
            for i in range(quantity):
                name = generator.name()
                f.write('{}\n'.format(name))
        print('Wrote person names to file {}'.format(output_file))
        return
    else:
        name_list = []
        for i in range(quantity):
            name = generator.name()
            name_list.append(name)
        return name_list


def fake_addresses(quantity, output_file=None, locale='ja_JP', seed=None):
    """
    Generate a list of addresses
    :param output_file: path to output file
    :return:
        - if output_file is None: return a list of addresses, otherwise write generated addresses to output_file
    """

    generator = faker.Faker(locale)

    if seed:
        generator.seed(seed)

    if output_file:
        with open(output_file, 'w') as f:
            for i in range(quantity):
                address = generator.address()
                f.write('{}\n'.format(address))
        print('Wrote addresses to file {}'.format(output_file))
        return
    else:
        address_list = []
        for i in range(quantity):
            address = generator.address()
            address_list.append(address)
        return address_list


def fake_date_strings_jp(quantity, patterns=['{}{}年{}月{}日'], year_names=['平成', '昭和'], output_file=None, seed=None):
    """
    Generate list of date strings
    :param quantity: Number of generated strings for each combination of patterns and year_names
    :param patterns: List of date patterns
    :param output_file: path to output file
    :param seed:
    :return:
        - if output_file is None: return a list of strings, otherwise write generated strings to output_file
    """

    if seed:
        random.seed(seed)

    def _get_random_date_string(pattern, year_name):
        fake_year = random.randint(1, 99)
        fake_month = random.randint(1, 12)
        fake_date = random.randint(1, 31)
        date_string = pattern.format(year_name, fake_year, fake_month, fake_date)

        return date_string

    quantity_each = quantity // (len(patterns) * len(year_names))

    if output_file:
        with open(output_file, 'w') as f:
            for i in range(quantity_each):
                for pattern in patterns:
                    for year_name in year_names:
                        date_string = _get_random_date_string(pattern, year_name)
                        f.write('{}\n'.format(date_string))
        print('Wrote date strings to file {}'.format(output_file))
        return
    else:
        date_list = []
        for i in range(quantity_each):
            for pattern in patterns:
                for year_name in year_names:
                    date_string = _get_random_date_string(pattern, year_name)
                    date_list.append(date_string)
        return date_list


def fake_driver_license_number_jp(quantity, patterns=['{}'], output_file=None, seed=None):
    """
    Generate list of driver license numbers
    :param quantity: Number of generated driver license numbers
    :param patterns: List of patterns
    :param output_file: path to output file
    :param seed:
    :return:
        - if output_file is None: return a list of sequences, otherwise write generated sequences to output_file

    Reference:
        * https://gazoo.com/article/daily/150907.html
    """

    if seed:
        random.seed(seed)

    def _get_random_sequence(pattern):
        # Fake digits 1-2: police committee code
        police_committee_code = random.choice(constants.POLICE_COMMITTEE_CODES)

        # Fake digits 3-4: last two digits of year that the license is acquired
        acquired_year_last_two_digits = '{0:02d}'.format(random.randint(0, 99))

        # Fake digits 5-10: management code
        management_code = '{0:06d}'.format(random.randint(0, 999999))

        # Fake digits 11-12: confirmation code
        confirmation_code = '{0:02d}'.format(random.randint(0, 99))

        sequence = police_committee_code + acquired_year_last_two_digits + management_code + confirmation_code
        sequence_string = pattern.format(sequence)

        return sequence_string

    quantity_each = quantity // len(patterns)

    if output_file:
        with open(output_file, 'w') as f:
            for i in range(quantity_each):
                for pattern in patterns:
                    sequence_string = _get_random_sequence(pattern)
                    f.write('{}\n'.format(sequence_string))
        print('Wrote sequence strings to file {}'.format(output_file))
        return
    else:
        sequence_list = []
        for i in range(quantity_each):
            for pattern in patterns:
                sequence_string = _get_random_sequence(pattern)
                sequence_list.append(sequence_string)
        return sequence_list


def fake_number_sequence(quantity, length, patterns=['{}'], output_file=None, seed=None):
    """
    Generate list of number sequence
    :param quantity: Number of generated number sequence
    :param length: Length of each sequence
    :param patterns: List of patterns
    :param output_file: path to output file
    :param seed:
    :return:
        - if output_file is None: return a list of sequences, otherwise write generated sequences to output_file
    """

    if seed:
        random.seed(seed)

    def _get_random_sequence(pattern, length):
        sequence = ''
        for i in range(length):
            sequence += str(random.randint(0, 9))

        sequence_string = pattern.format(sequence)

        return sequence_string

    quantity_each = quantity // len(patterns)

    if output_file:
        with open(output_file, 'w') as f:
            for i in range(quantity_each):
                for pattern in patterns:
                    sequence_string = _get_random_sequence(pattern, length)
                    f.write('{}\n'.format(sequence_string))
        print('Wrote sequence strings to file {}'.format(output_file))
        return
    else:
        sequence_list = []
        for i in range(quantity_each):
            for pattern in patterns:
                sequence_string = _get_random_sequence(pattern, length)
                sequence_list.append(sequence_string)
        return sequence_list


def generate_jp_driver_licence_training_text_file(output_dir, base_quantity=1000, max_line_length=50,
                                                  fixed_words_file_path=None, seed=None):
    """
    Generate training text file for japanese driver license
    1. Training text for Japanese driver license card
        + Components:
            - Fixed words: '氏名', '住所', '交付', '免許の', '眼鏡等', '条件等', '中型車は中型車', 'に限る',
                           '優良', '番号', '二・小・原', '他', '二種', '運転免許証', '公安委員会'
            - Person name: E.g. '中田 上脳', ...
            - Date string: E.g. '昭和29年2月20日生', '平成20年11月17日', '平成32年03月20日まで有効' ...
            - Address string: E.g. '東京都目黒区柿の木坂2ー10一10', ...
            - driver license number: E.g. '第 444260222920 号', ...
            - Sequence of digits: E.g. '23442'
    :param output_dir: directory to save output training text file
    :param base_quantity: base quantity for each generated item
    :param max_line_length: maximum length of each line in ouput training text file
    :param fixed_words_file_path: path to fixed words file
    :param seed:
    :return:
    """

    # Check if output directory exists
    if not os.path.exists(output_dir):
        raise Exception('output directory {} does not exist'.format(output_dir))

    # Check if fixed words file exists
    if fixed_words_file_path:
        if not os.path.exists(fixed_words_file_path):
            raise Exception('fixed words file {} does not exist'.format(fixed_words_file_path))

    # Create temporary directory and save generated files there
    tmp_dir = '/tmp/' + 'fake_' + datetime.now().strftime('%Y%m%d%H%M%S')
    os.makedirs(tmp_dir)
    print('Created directory for input file: {}\n'.format(tmp_dir))

    person_name_quantity = config('PERSON_NAME_QUANTITY_FACTOR', default=1, cast=int) * base_quantity
    address_quantity = config('ADDRESS_QUANTITY_FACTOR', default=1, cast=int) * base_quantity
    date_string_quantity = config('DATE_STRING_QUANTITY_FACTOR', default=1, cast=int) * base_quantity
    driver_license_number_quantity = config('DRIVER_LICENSE_NUMBER_QUANTITY_FACTOR', default=1, cast=int) * base_quantity
    number_sequence_quantity = config('NUMBER_SEQUENCE_QUANTITY_FACTOR', default=1, cast=int) * base_quantity

    print('Number of person names: {}'.format(person_name_quantity))
    print('Number of addresses: {}'.format(address_quantity))
    print('Number of date strings: {}'.format(date_string_quantity))
    print('Number of driver license numbers: {}'.format(driver_license_number_quantity))
    print('Number of number sequences: {}\n'.format(number_sequence_quantity))

    # Generate person names file
    person_names_file_path = os.path.join(tmp_dir, 'person_names.txt')
    fake_person_names(person_name_quantity, output_file=person_names_file_path, locale='ja_JP', seed=seed)

    # Generate addresses file
    addresses_file_path = os.path.join(tmp_dir, 'addresses.txt')
    fake_addresses(address_quantity, output_file=addresses_file_path, locale='ja_JP', seed=seed)

    # Generate date strings file
    date_strings_file_path = os.path.join(tmp_dir, 'date_strings.txt')
    fake_date_strings_jp(date_string_quantity, patterns=['{}{}年{}月{}日',
                                                         '{}{}年 {}月 {}日',
                                                         '{}{}年{}月{}日生',
                                                         '{}{}年{}月{}日まで有効',
                                                         ],
                         year_names=['平成', '昭和'], output_file=date_strings_file_path, seed=seed)

    # Generate driver license numbers file
    driver_license_numbers_file_path = os.path.join(tmp_dir, 'driver_license_numbers.txt')
    fake_driver_license_number_jp(driver_license_number_quantity, patterns=['第 {} 号',
                                                                            '{}'],
                                  output_file=driver_license_numbers_file_path, seed=seed)

    # Generate 5-digit number sequences file
    number_sequences_file_path = os.path.join(tmp_dir, 'number_sequences.txt')
    fake_number_sequence(number_sequence_quantity, 5, patterns=['{}'],
                         output_file=number_sequences_file_path, seed=seed)

    # Mix fixed words and generated strings to training text file
    # Open input files
    try:
        person_names_file = open(person_names_file_path, 'r')
        addresses_file = open(addresses_file_path, 'r')
        date_strings_file = open(date_strings_file_path, 'r')
        driver_license_numbers_file = open(driver_license_numbers_file_path, 'r')
        number_sequences_file = open(number_sequences_file_path, 'r')
        fixed_words_file = None
        if fixed_words_file_path:
            fixed_words_file = open(fixed_words_file_path)
    except Exception as error:
        raise error

    # Open training text file to write
    training_text_file_path = os.path.join(output_dir, 'driver_license_' +
                                           datetime.now().strftime('%Y%m%d%H%M%S') + '.training_text')

    print('Start writing to file {}'.format(training_text_file_path))
    with open(training_text_file_path, 'w') as training_text_file:
        if seed:
            random.seed(seed)

        PERSON_NAME_CHOICE = 1
        ADDRESS_CHOICE = 2
        DATE_STRING_CHOICE = 3
        DRIVER_LISENCE_NUMBER_CHOICE = 4
        NUMBER_SEQUENCE_CHOICE = 5
        FIXED_WORD_CHOICE = 6

        choice_list = [PERSON_NAME_CHOICE, ADDRESS_CHOICE, DATE_STRING_CHOICE,
                       DRIVER_LISENCE_NUMBER_CHOICE, NUMBER_SEQUENCE_CHOICE]
        if fixed_words_file:
            choice_list.append(FIXED_WORD_CHOICE)
        choice_list_length = len(choice_list)

        text_line = ''
        while choice_list_length > 0:
            # Only fixed words file has remaining texts
            if choice_list_length == 1:
                break

            choice = random.choice(choice_list)

            if choice == PERSON_NAME_CHOICE:
                input_file = person_names_file
            elif choice == ADDRESS_CHOICE:
                input_file = addresses_file
            elif choice == DATE_STRING_CHOICE:
                input_file = date_strings_file
            elif choice == DRIVER_LISENCE_NUMBER_CHOICE:
                input_file = driver_license_numbers_file
            elif choice == NUMBER_SEQUENCE_CHOICE:
                input_file = number_sequences_file
            else:
                input_file = fixed_words_file

            text = input_file.readline().strip()

            # End of file
            if not text:
                if choice == FIXED_WORD_CHOICE:
                    print('Reset fixed words file')
                    fixed_words_file.seek(0, 0)
                    continue

                choice_list.remove(choice)
                choice_list_length -= 1
                continue

            text_line += text + ' '

            if len(text_line) >= max_line_length:
                training_text_file.write('{}\n'.format(text_line))
                text_line = ''

    # Close input files
    person_names_file.close()
    addresses_file.close()
    date_strings_file.close()
    driver_license_numbers_file.close()
    number_sequences_file.close()
    if fixed_words_file:
        fixed_words_file.close()

    print('Finished!')


if __name__ == '__main__':
    generate_jp_driver_licence_training_text_file('/home/bang/projects/python/tesseract_test/tesseract-ocr/langdata/jpn',
                                                  base_quantity=300, max_line_length=30,
                                                  fixed_words_file_path=None, seed=123)
