import re


REDUNDANT_SYMBOLS_PATTERN = re.compile(r'[-_/\\|.・。…*、』」<>)(※\':"=ヽ©]+')
NOT_DIGITS_PATTERN=re.compile(r'[^0-9]+')
ADDRESS_REDUNDANT_SYMBOLS_PATTERN = re.compile(r'[_/\\|.。…*、』」<>)(※\':"=ヽ©]+')
WRONG_SHOWA_YEAR_PATTERN = re.compile(r'([照茹暗辿連因蜂限取呆了胃隔防蝶配玉邑曲妥婦]和|昭[衝独科])|骨科|隊知|照閣|曲知')
WRONG_HEISEI_YEAR_PATTERN = re.compile(r'[半キ理ギ玉]成|平[放故用友度破刻]|辛友|ギ故|ギ必|半生|半友|導入|幸故|半度')
YEAR_MONTH_DATE_PATTERN = re.compile(r'\d\d年\d\d月\d\d日')


def _remove_redundant_symbols(text, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN):
    return symbols_pattern.sub('', text)


def _remove_space(text):
    return text.replace(' ', '')


def _correct_jp_date(text, check_ymd_pattern=False):
    text = WRONG_SHOWA_YEAR_PATTERN.sub('昭和', text)
    text = WRONG_HEISEI_YEAR_PATTERN.sub('平成', text)

    if check_ymd_pattern:
        matched_ymd = YEAR_MONTH_DATE_PATTERN.search(text)
        if not matched_ymd:
            wrong_ymd_pattern_1 = re.compile(r'(\d\d).*(\d\d).*(\d\d).*')
            if wrong_ymd_pattern_1.search(text):
                return wrong_ymd_pattern_1.sub(r'\1年\2月\3日', text)

            wrong_ymd_pattern_2 = re.compile(r'([\d]{1,2})[^0-9]*([\d]{1,2})[^0-9]*([\d]{1,2})[^0-9]*')
            if wrong_ymd_pattern_2.search(text):
                return wrong_ymd_pattern_2.sub(r'\1年\2月\3日', text)

    return text


def correct_full_name(ocr_full_name):
    full_name = ocr_full_name

    full_name = _remove_redundant_symbols(full_name, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    full_name = _remove_space(full_name)
    full_name = full_name.strip()

    return full_name


def correct_date_of_birth(ocr_date_of_birth):
    date_of_birth = ocr_date_of_birth

    date_of_birth = _remove_redundant_symbols(date_of_birth, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    date_of_birth = _remove_space(date_of_birth)
    date_of_birth = _correct_jp_date(date_of_birth)
    date_of_birth = date_of_birth.strip()

    # Remove the ending 生 character
    ending_sei_char_pattern = re.compile(r'[生拓]$')
    date_of_birth = ending_sei_char_pattern.sub('', date_of_birth)

    return date_of_birth


def correct_address(ocr_address):
    address = ocr_address

    address = _remove_redundant_symbols(address, symbols_pattern=ADDRESS_REDUNDANT_SYMBOLS_PATTERN)
    address = _remove_space(address)

    # Change 'ー' or '一' between digits to '-'
    pattern = re.compile(r'(\d)[ー一](\d)')
    address = pattern.sub(r'\1-\2', address)

    address = address.strip()

    return address


def correct_issue_date(ocr_issue_date):
    issue_date = ocr_issue_date

    issue_date = _remove_redundant_symbols(issue_date, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    issue_date = _remove_space(issue_date)
    issue_date = _correct_jp_date(issue_date, check_ymd_pattern=True)
    issue_date = issue_date.strip()

    return issue_date


def correct_inquiry_number(ocr_inquiry_number):
    inquiry_number = ocr_inquiry_number

    inquiry_number = _remove_redundant_symbols(inquiry_number, symbols_pattern=NOT_DIGITS_PATTERN)
    inquiry_number = _remove_space(inquiry_number)
    inquiry_number = inquiry_number.strip()

    return inquiry_number


def correct_expiration_date(ocr_expiration_date):
    expiration_date = ocr_expiration_date

    expiration_date = _remove_redundant_symbols(expiration_date, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    expiration_date = _remove_space(expiration_date)
    expiration_date = _correct_jp_date(expiration_date, check_ymd_pattern=True)
    expiration_date = expiration_date.strip()

    return expiration_date


def correct_menkyono(ocr_menkyono):
    menkyono = ocr_menkyono

    return menkyono


def correct_joukentou(ocr_joukentou):
    joukentou = ocr_joukentou

    return joukentou


def correct_license_number(ocr_license_number):
    license_number = ocr_license_number

    license_number = _remove_redundant_symbols(license_number, symbols_pattern=NOT_DIGITS_PATTERN)
    license_number = _remove_space(license_number)
    license_number = license_number.strip()

    return license_number


def correct_nishogen_issue_date(ocr_nishogen_issue_date):
    nishogen_issue_date = ocr_nishogen_issue_date

    nishogen_issue_date = _remove_redundant_symbols(nishogen_issue_date, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    nishogen_issue_date = _remove_space(nishogen_issue_date)
    nishogen_issue_date = _correct_jp_date(nishogen_issue_date, check_ymd_pattern=True)
    nishogen_issue_date = nishogen_issue_date.strip()

    return nishogen_issue_date


def correct_other_issue_date(ocr_other_issue_date):
    other_issue_date = ocr_other_issue_date

    other_issue_date = _remove_redundant_symbols(other_issue_date, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    other_issue_date = _remove_space(other_issue_date)
    other_issue_date = _correct_jp_date(other_issue_date, check_ymd_pattern=True)
    other_issue_date = other_issue_date.strip()

    return other_issue_date


def correct_nishu_issue_date(ocr_nishu_issue_date):
    nishu_issue_date = ocr_nishu_issue_date

    nishu_issue_date = _remove_redundant_symbols(nishu_issue_date, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    nishu_issue_date = _remove_space(nishu_issue_date)
    nishu_issue_date = _correct_jp_date(nishu_issue_date, check_ymd_pattern=True)
    nishu_issue_date = nishu_issue_date.strip()

    return nishu_issue_date


def correct_issue_office(ocr_issue_office):
    issue_office = ocr_issue_office

    issue_office = _remove_redundant_symbols(issue_office, symbols_pattern=REDUNDANT_SYMBOLS_PATTERN)
    issue_office = _remove_space(issue_office)
    issue_office = issue_office.strip()

    issue_office = issue_office.replace('\n', '')

    # Remove some redundant symbols
    symbols_pattern = re.compile(r'[ーょ]+')
    issue_office = symbols_pattern.sub('', issue_office)

    # Correct 公安委員会
    wrong_police_authority_pattern_1 = re.compile(r'公安[^委]員会')
    issue_office = wrong_police_authority_pattern_1.sub('公安委員会', issue_office)

    wrong_police_authority_pattern_2 = re.compile(r'公安三員倒|公安委躍会|公安半只会|公安装具会|公安半具会|公雪供員会|公安和全員会')
    issue_office = wrong_police_authority_pattern_2.sub('公安委員会', issue_office)

    return issue_office


def correct_allowed_types(ocr_allowed_types):
    allowed_types = ocr_allowed_types

    return allowed_types

