import re


def correct_location_code(location_code_ocr):
    """

    :param location_code_ocr:
    :return:
    """
    location_code = location_code_ocr.replace(' ', '')
    location_code_label_pattern = re.compile(r'地点番号')
    location_code = location_code_label_pattern.sub('', location_code)

    return location_code


def correct_customer_code(customer_code_ocr):
    """
    Get お客さま番号 information
    :param customer_code_ocr:
    :return:
    """
    return customer_code_ocr


def correct_customer_name(customer_name_ocr):
    customer_name = customer_name_ocr.replace(' ', '')

    # Remove redundant symbols at the beginning of the name
    beginning_symbols_pattern = re.compile(r'^[_/\\|.・。\'"*]+')
    customer_name = beginning_symbols_pattern.sub('', customer_name)

    # Remove redundant symbols at the end of the name
    end_symbols_pattern = re.compile(r'[_/\\|.・。\'"*]+$')
    customer_name = end_symbols_pattern.sub('', customer_name)

    return customer_name


def correct_customer_address(customer_address_ocr):
    customer_address = customer_address_ocr.replace(' ', '')
    customer_address = customer_address.replace('\n', ' ')

    # Remove the label 'ご使用場所' at the beginning of the address string
    address_label_pattern = re.compile(r'[_/\\|.・。\'"*]*ご使用場所')
    customer_address = address_label_pattern.sub('', customer_address)

    # Remove redundant symbols at the end of the name
    end_symbols_pattern = re.compile(r'[_/\\|.・。\'"*]+$')
    customer_address = end_symbols_pattern.sub('', customer_address)

    return customer_address
