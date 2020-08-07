import json
import uuid
import random
import string
import re
from pprint import pprint as pp


def read_config(file="config.json"):
    with open(file, 'r') as config_file:
        config = json.load(config_file)
    return(config)


def gen_uuid():
    return("{}".format(uuid.uuid4()))


def gen_id(id_length=4):
    id = ''.join(
        [random.choice(string.ascii_letters.upper() + string.digits) for n in range(id_length)])
    return(id)


def get_condition(condition_in):
    condition_in = condition_in.lower()
    condition = None
    if condition_in == "n" or condition_in == "new":
        condition = "new"
    elif condition_in == "u" or condition_in == "used":
        condition = "used"
    return(condition)


def get_action(action_in):
    action_in = action_in.lower()
    action = None
    if action_in == "p" or action_in == "pick":
        action = "pick"
    elif action_in == "s" or action_in == "store":
        action = "store"
    return(action)


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


def verify_int(val):
    if isinstance(val, int):
        return(True)
    return(False)


def verify_int_or_float(val):
    if isinstance(val, int):
        return(True)
    elif isinstance(val, float):
        return(True)
    return(False)


def verify_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def verify_positive_num(val):
    if val > 0:
        return(True)
    return(False)
