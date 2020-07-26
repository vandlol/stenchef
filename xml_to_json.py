from glob import glob as glob
import json
import xmltodict
from pprint import pprint as pp
import misc

config = misc.read_config()
folder = config["folder"]

files = glob("{}/*.xml".format(folder["download"]))

for file in files:
    filename = file.replace("{}/".format(folder["download"]), "")
    filetype = "catalog"
    output_filename = filename.replace(".xml", ".json").lower()
    if filename.islower():
        filetype = "map"

    with open(file, 'r') as fh:
        file_dict = xmltodict.parse(fh.read())

    file_dict_lower = {"items": list()}
    c_key = "CATALOG"
    if filename == "codes.xml":
        c_key = "CODES"
    for d_in in file_dict[c_key]["ITEM"]:
        d_out = dict()
        for k, v in d_in.items():
            k = k.lower()
            d_out[k] = v
        file_dict_lower["items"].append(d_out)

    with open("{}/{}".format(folder[filetype], output_filename), 'w') as fh_out:
        json.dump(file_dict_lower, fh_out, sort_keys=True, indent=4)
