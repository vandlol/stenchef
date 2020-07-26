import json
import misc
import item_classes
from glob import glob as glob


class ImportMap:
    config = misc.read_config()

    def __init__(self):
        pass

    def categories(self):
        print("Importing Map: categories.json")
        with open("{}/{}".format(self.config["folder"]["map"], "categories.json")) as categories_file:
            map_cat = json.load(categories_file)

        for item in map_cat["items"]:
            item_classes.Categories(item).save()

    def codes(self):
        print("Importing Map: codes.json")
        with open("{}/{}".format(self.config["folder"]["map"], "codes.json")) as codes_file:
            map_cod = json.load(codes_file)

        for item in map_cod["items"]:
            item_classes.Codes(item).save()

    def itemtypes(self):
        print("Importing Map: itemtypes.json")
        with open("{}/{}".format(self.config["folder"]["map"], "itemtypes.json")) as itemtypes_file:
            map_itt = json.load(itemtypes_file)

        for item in map_itt["items"]:
            item_classes.Itemtypes(item).save()

    def colors(self):
        print("Importing Map: colors.json")
        with open("{}/{}".format(self.config["folder"]["map"], "colors.json")) as colors_file:
            map_col = json.load(colors_file)

        for item in map_col["items"]:
            item_classes.Colors(item).save()

    def all(self):
        print("Importing all Map Files.")
        self.categories()
        self.codes()
        self.itemtypes()
        self.colors()


class ImportCatalog:
    config = misc.read_config()

    def __init__(self):
        pass

    def single(self, file):
        if not file:
            return(None)
        print("Importing Catalog: {}".format(file.replace(
            "{}/".format(self.config["folder"]["catalog"]), "")))
        with open(file, 'r') as fh:
            catalog_file_json = json.load(fh)

        for item in catalog_file_json["items"]:
            item_classes.Catalog(item).save()

    def all(self):
        print("Importing all Catalog Files.")
        files = glob("{}/*.json".format(self.config["folder"]["catalog"]))
        for file in files:
            self.single(file)
