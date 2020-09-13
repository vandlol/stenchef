from glob import glob as glob
import xmltodict
import pymongo
import json
from pprint import pprint as pp

folder_download = "bricklink_data/"
translate_map = {
    "item": {"category": "category_id", "itemtype": "itemtype_id"},
    "code": {
        "color": "color_id",
        "codename": "code",
        "itemid": "itemid_id",
        "itemtype": "itemtype_id",
    },
}


def clean_filename(file):
    filename = file.replace(folder_download, "")
    filename_clean = (
        filename.replace("s.xml", "").replace(".xml", "").replace("ie", "y").lower()
    )
    if filename_clean.startswith("original"):
        filename_clean = filename_clean.replace(" ", "_").replace("xe", "x")

    return (filename, filename_clean)


def translate_k(identifier, k):
    if not translate_map.get(identifier):
        return k
    if not translate_map[identifier].get(k):
        return k
    return translate_map[identifier][k]


def convert(file, cmap=None, filetype="meta", c_key="CATALOG", raw=False):
    filename, filename_clean = clean_filename(file)
    print("Importing: {}".format(file))
    modelclass = filename_clean
    file_list = list()

    if not filename.islower():
        filetype = "catalog"
        modelclass = "item"

    collection_name = "{}_{}".format(filetype, modelclass)

    if filename_clean == "code":
        c_key = "CODES"

    with open(file, "r") as fh:
        file_dict = xmltodict.parse(fh.read())
    for item in file_dict[c_key]["ITEM"]:
        temp = dict()
        if modelclass == "item":
            temp["itemuid"] = "{}_{}".format(item["ITEMTYPE"], item["ITEMID"])
        for k, v in item.items():
            k = k.lower()
            k = translate_k(modelclass, k)
            if k.startswith("itemdim") or k == "itemweight" or k == "itemyear":
                if v == "?":
                    v = None
                if v:
                    v = int(float(v))
            if k == "color_id":
                v = cmap[v]
            temp[k] = v
        if not raw:
            file_list.append(pymongo.InsertOne(temp))
        else:
            file_list.append(temp)
    return collection_name, file_list


def main():
    xml_files = sorted(glob("{}*.xml".format(folder_download)), reverse=True)
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    cn, colors = convert("{}colors.xml".format(folder_download), raw=True)
    cmap = dict()
    for color in colors:
        cmap[color["colorname"]] = color["color"]

    xml_files.remove("{}codes.xml".format(folder_download))
    xml_files.append("{}codes.xml".format(folder_download))
    for file in xml_files:
        collection_name, file_data = convert(file, cmap=cmap)
        db[collection_name].bulk_write(file_data)


if __name__ == "__main__":
    main()
