import re


def clean_phone_number(phone):
    digits = re.sub(r'\D', '', phone)  # keep only digits

    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    elif digits.startswith('0') and len(digits) == 11:
        digits = digits[1:]
    return digits