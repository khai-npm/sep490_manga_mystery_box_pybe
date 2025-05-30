import re 


def contains_special_character(input_string):
    return bool(re.search(r'[^A-Za-z0-9]', input_string))