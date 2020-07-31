
import misc
import item_classes

from pprint import pprint as pp


class Container:
    def __init__(self):
        self.config = misc.read_config()
        self.numerical_properties = [
            "containerimx", "containerdimy", "containerdimz", "containeremptyweight"]
        self.id_properties = ["containerparent",
                              "containerid", "containerconstraints"]
        self.string_properties = ["containertype", "containername"]
        self.year_properties = ["containeryearadded"]

    def new(self, container):
        self.container = container
        if not self._verify_container():
            # TODO error handling
            print("there was an error")
        exit()
        if not self.container["containerid"]:
            # TODO make configurable
            self.container["containerid"] = misc.gen_id(
                id_length=self.config["id_length"])
            while item_classes.Templates.find_one({"containerid": self.container["containerid"]}):
                self.container["containerid"] = misc.gen_id(
                    id_length=self.config["id_length"])

        self.container["containercontent"] = dict()

    def _verify_container(self):
        mandatory_properties = ["containertype", "containerid"]
        err = 0
        for prop in mandatory_properties:
            if not self.container.get(prop):
                err += 1
                print("Container Property {} missing or None".format(prop))

        for prop, val in self.container.items():
            if not val:
                continue
            print("---")
            print(prop, val)
            if prop in self.numerical_properties:
                print("num")
                if misc.verify_int_or_float(val):
                    print("ok")
                    continue
                else:
                    err += 1
                    print(
                        "Container Property {} is not an integer or float.".format(prop))
            if prop in self.string_properties:
                print("string")
                if misc.verify_string(val):
                    print("ok")
                    continue
                else:
                    err += 1
                    print("Container Property {} is not a string.".format(prop))
            if prop in self.id_properties:
                print("id")
                if misc.verify_id(val, id_length=self.config["id_length"]):
                    print("ok")
                    continue
                else:
                    err += 1
                    print("Container Property {} is not a valid ID.".format(prop))
            if prop in self.year_properties:
                print("year")
                if misc.verify_year(val):
                    print("ok")
                    continue
                else:
                    err += 1
                    print("Container Property {} is not a Year.".format(prop))

        if err != 0:
            return(False)
        return(True)


class Template:
    def __init__(self, templateid=None, containertype=None, containerimx=None, containerdimy=None, containerdimz=None, containeremptyweight=None, templatename=None, templatetype="container"):
        self.config = misc.read_config()
        self.templateid = templateid
        self.containertype = containertype
        self.containerimx = containerimx
        self.containerdimy = containerdimy
        self.containerdimz = containerdimz
        self.containeremptyweight = containeremptyweight
        self.templatename = templatename
        self.templatetype = templatetype

    def new(self):
        self.templateid = misc.gen_id(id_length=self.config["id_length"])
        while item_classes.Templates.find_one({"templateid": self.templateid}):
            self.templateid = misc.gen_id(id_length=self.config["id_length"])

        self.template = {
            "templatetype": self.templatetype,
            "containertype": self.containertype,
            "containerimx": self.containerimx,
            "containerdimy": self.containerdimy,
            "containerdimz": self.containerdimz,
            "containeremptyweight": self.containeremptyweight,
            "templatename": self.templatename
        }
        if item_classes.Templates.find_one(self.template):
            # TODO error handling
            print("already exists")
            return(None)
        self.template["templateid"] = self.templateid
        if not self.template["templatename"]:
            self.template["templatename"] = self.templateid
        item_classes.Templates(self.template).save()
        print(self.template)

    def load(self, templateid=None):
        if templateid:
            self.templateid = templateid
        if not self.templateid:
            # TODO error handling
            print("no templateid given")
            return(None)
        ret_template = item_classes.Templates.find_one(
            {"templateid": self.templateid})
        print(ret_template)

    def list_type(self, templatetype=None):
        if templatetype:
            self.templatetype = templatetype
        if not self.templatetype:
            # TODO error handling
            print("no templatetype given")
            return(None)
        return(list(item_classes.Templates.find({"templatetype": self.templatetype})))

    def list_all(self):
        return(list(item_classes.Templates.find()))


test = {
    "containertype": "container",
    "containerimx": 9,
    "containerdimy": 5,
    "containerdimz": 3,
    "containeremptyweight": 15,
    "containerparent": None,
    "containername": "con1",
    "containerid": "QR7G",
    "containeryearadded": 1995,
    "containerconstraints": None,
    "containercontent": dict()
}

Container().new(test)
