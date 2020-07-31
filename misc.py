import json
import random
import string
import re
from pprint import pprint as pp


def read_config(file="config.json"):
    with open(file, 'r') as config_file:
        config = json.load(config_file)
    return(config)


def gen_id(id_length=4):
    id = ''.join(
        [random.choice(string.ascii_letters.upper() + string.digits) for n in range(id_length)])
    return(id)


def verify_id(val, id_length=4):
    if re.match(r"^[A-Z0-9]{{{}}}$".format(id_length), val):
        return(True)
    return(False)


def verify_year(val):
    if re.match(r'^\d{4}$', str(val)):
        return(True)
    return(False)


def verify_string(val):
    if isinstance(val, str):
        return(True)
    return(False)


def verify_int_or_float(val):
    if isinstance(val, int):
        return(True)
    elif isinstance(val, float):
        return(True)
    return(False)
