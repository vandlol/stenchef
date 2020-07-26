
import misc
import item_classes

from pprint import pprint as pp


class Container:
    def __init__(self):
        pass

    def new(self, container):
        self.container = container
        if not self._verify_container():
            # TODO error handling
            print("there was an error")
        if not self.container["containerlabel"]:
            # TODO make configurable
            self.container["containerlabel"] = misc.gen_id()
            while item_classes.Templates.find_one({"containerlabel": self.container["containerlabel"]}):
                self.container["containerlabel"] = misc.gen_id()

        self.container["containercontent"] = dict()

    def _verify_container(self):
        mandatory_properties = ["containertype", "containerlabel"]
        err = 0
        for prop in mandatory_properties:
            if not self.container.get(prop):
                err += 1
                print("Property {} missing or None".format(prop))
        if err != 0:
            return(False)
        numerical_properties = ["containerimx",
                                "containerdimy", "containerdimz", "containeremptyweight"]

        id_properties = ["containerparent",
                         "containerlabel", "containerconstraints"]
        string_properties = ["containertype", "containername"]
        year_properties = ["containeryearadded"]

    return(True)


class Template:
    def __init__(self, templateid=None, containertype=None, containerimx=None, containerdimy=None, containerdimz=None, containeremptyweight=None, templatename=None, templatetype="container"):
        self.templateid = templateid
        self.containertype = containertype
        self.containerimx = containerimx
        self.containerdimy = containerdimy
        self.containerdimz = containerdimz
        self.containeremptyweight = containeremptyweight
        self.templatename = templatename
        self.templatetype = templatetype

    def new(self):
        self.templateid = misc.gen_id()
        while item_classes.Templates.find_one({"templateid": self.templateid}):
            self.templateid = misc.gen_id()

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
    "containertype": None,
    "containerimx": None,
    "containerdimy": None,
    "containerdimz": None,
    "containeremptyweight": None,
    "containerparent": None,
    "containername": None,
    "containerlabel": None,
    "containeryearadded": None,
    "containerconstraints": None,
    "containercontent": dict()


}

Container().new(test)
