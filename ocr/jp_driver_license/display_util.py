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
    keys = [
        'full_name',
        'date_of_birth',
        'address',
        'issue_date',
        'inquiry_number',
        'expiration_date',
        'menkyono',
        'joukentou',
        'license_number',
        'nishogen_issue_date',
        'other_issue_date',
        'nishu_issue_date',
        'issue_office',
        # 'allowed_types',
    ]

    for key in keys:
        print('{0:20s}: {1}'.format(key, ocr_result[key]))

