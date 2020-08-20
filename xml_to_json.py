from glob import glob as glob
import json
import xmltodict
import misc

config = misc.read_config()
folder_download = "download/"
folder_setup = "setup/"

xml_files = glob("{}*.xml".format(folder_download))

for file in xml_files:
    filename = file.replace(folder_download, "")
    filetype = "meta"
    c_key = "CATALOG"
    file_list = list()
    filename_clean = filename.replace(
        "s.xml", "").replace(
        ".xml", "").replace("ie", "y").lower()

    if filename_clean.startswith("original"):
        filename_clean = filename_clean.replace(" ", "_").replace("xe", "x")

    output_filename = "fixture_{}.json".format(
        filename_clean)

    pk = filename_clean
    modelclass = filename_clean

    if not filename.islower():
        filetype = "catalog"
        pk = "itemid"
        modelclass = "item"

    model = "{}.{}".format(filetype, modelclass)

    if filename_clean == "code":
        c_key = "CODES"
        pk = "codename"

    if filename_clean == "color":
        pk = "colorname"

    with open(file, 'r') as fh:
        file_dict = xmltodict.parse(fh.read())
    for item in file_dict[c_key]["ITEM"]:
        temp = {"model": model,
                "pk": None,
                "fields": dict()}
        for k, v in item.items():
            k = k.lower()
            if k == pk:
                temp["pk"] = v
                continue
            if k.startswith("itemdim") or k == "itemweight" or k == "itemyear":
                if v == "?":
                    v = None
                if v:
                    v = int(float(v))
            temp['fields'][k] = v
        file_list.append(temp)

    with open("stenchef/{}/setup/{}".format(filetype, output_filename), 'w') as fh_out:
        json.dump(file_list, fh_out, sort_keys=True, indent=4)
