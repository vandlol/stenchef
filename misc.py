import json
import random
import string


def read_config(file="config.json"):
    with open(file, 'r') as config_file:
        config = json.load(config_file)
    return(config)


def gen_id():
    id = ''.join(
        [random.choice(string.ascii_letters.upper() + string.digits) for n in range(4)])
    return(id)
