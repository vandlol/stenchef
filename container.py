from log import logger as l
import misc
import item_classes
import sys

from pprint import pprint as pp


class Container:
    def __init__(self):
        self.config = misc.read_config()
        self.mandatory_properties = ["containertype"]
        self.numerical_properties = [
            "containerimx", "containerdimy", "containerdimz", "containeremptyweight"]
        self.id_properties = ["containerparent",
                              "containerid", "containerconstraints"]
        self.string_properties = ["containertype", "containername"]
        self.year_properties = ["containeryearadded"]
        self.unwanted_properties = ["_id", "templateid"]

    def new(self, container):
        self.container = container
        if not self._verify_container():
            l.error("There was an error within the Container Properties.")
            sys.exit("31")
        if not self.container.get("containerid"):
            self.container["containerid"] = misc.gen_id(
                id_length=self.config["id_length"])
            while item_classes.Templates.find_one({"containerid": self.container["containerid"]}):
                self.container["containerid"] = misc.gen_id(
                    id_length=self.config["id_length"])

        self.container["containercontent"] = dict()
        # TODO saving
        return(self.container["containerid"])

    def from_template(self, templateid, container):
        self.container = Template().load(templateid=templateid)
        if not self.container:
            l.error("Could not load Container Template: {}.".format(templateid))
            sys.exit("32")

        for prop in self.unwanted_properties:
            del self.container[prop]

        for prop, val in container.items():
            self.container[prop] = val

        return(self.new(self.container))

    def _verify_container(self):
        def _log_ok(prop, val):
            l.debug(
                "Verification Container Property {}, Value {}: OK.".format(prop, val))
            return

        err = 0
        for prop in self.mandatory_properties:
            if not self.container.get(prop):
                err += 1
                l.error(
                    "Container Property {} missing or None".format(prop))
                continue
            l.debug("Mandatory Container Property {} has been defined".format(prop))
        if err != 0:
            l.error("{} Mandatory Container Properties are missing.".format(err))
            return(False)
        for prop, val in self.container.items():
            if not val:
                continue
            if prop in self.numerical_properties:
                if misc.verify_int_or_float(val):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error(
                        "Container Property {} is not an integer or float.".format(prop))
            if prop in self.string_properties:
                if misc.verify_string(val):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error("Container Property {} is not a string.".format(prop))
            if prop in self.id_properties:
                if misc.verify_id(val, id_length=self.config["id_length"]):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error("Container Property {} is not a valid ID.".format(prop))
            if prop in self.year_properties:
                if misc.verify_year(val):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error("Container Property {} is not a Year.".format(prop))
        if err != 0:
            l.debug("Container PropertyError Count is {}.".format(err))
            return(False)
        return(True)


class Template:
    def __init__(self):
        self.config = misc.read_config()
        self.mandatory_properties = ["containertype"]
        self.numerical_properties = [
            "containerimx", "containerdimy", "containerdimz", "containeremptyweight"]
        self.string_properties = ["containertype",
                                  "containername", "templatename"]

    def new(self, template):
        self.template = template.copy()
        if not self._verify_template():
            l.error("There was an error within the Container Template Properties.")
            sys.exit("41")
        if not self.template.get("templateid"):
            self.template["templateid"] = misc.gen_id(
                id_length=self.config["id_length"])
            while item_classes.Templates.find_one({"templateid": self.template["templateid"]}):
                self.template["templateid"] = misc.gen_id(
                    id_length=self.config["id_length"])
        check_template = item_classes.Templates.find_one(template)
        if check_template:
            l.info("A template containing the given Properties already exists with templateid: {}".format(
                check_template.__dict__['templateid']))
            return(check_template.__dict__['templateid'])
        if not self.template["templatename"]:
            self.template["templatename"] = self.template["templateid"]
        item_classes.Templates(self.template).save()
        return(self.template["templateid"])

    def load(self, templateid=None):
        if templateid:
            self.templateid = templateid
        if not self.templateid:
            l.error("No templateid given.")
            return(None)
        ret_template = item_classes.Templates.find_one(
            {"templateid": self.templateid})
        if not ret_template:
            return(dict())
        return(ret_template.__dict__)

    def list_type(self, templatetype=None):
        if templatetype:
            self.templatetype = templatetype
        if not self.templatetype:
            # TODO error handling
            print("no templatetype given")
            return(None)
        ret_list = list()
        for item in list(item_classes.Templates.find({"templatetype": self.templatetype})):
            ret_list.append(item.__dict__)
        return(ret_list)

    def list_all(self):
        ret_list = list()
        for item in list(item_classes.Templates.find()):
            ret_list.append(item.__dict__)
        return(ret_list)

    def _verify_template(self):
        def _log_ok(prop, val):
            l.debug(
                "Verification Container Template Property {}, Value {}: OK.".format(prop, val))
            return

        err = 0
        for prop in self.mandatory_properties:
            if not self.template.get(prop):
                err += 1
                l.error(
                    "Container Template Property {} missing or None".format(prop))
                continue
            l.debug(
                "Mandatory Container Template Property {} has been defined".format(prop))
        if err != 0:
            l.error(
                "{} Mandatory Container Template Properties are missing.".format(err))
            return(False)
        for prop, val in self.template.items():
            if not val:
                continue
            if prop in self.numerical_properties:
                if misc.verify_int_or_float(val):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error(
                        "Container Template Property {} is not an integer or float.".format(prop))
            if prop in self.string_properties:
                if misc.verify_string(val):
                    _log_ok(prop, val)
                    continue
                else:
                    err += 1
                    l.error(
                        "Container Template Property {} is not a string.".format(prop))
        if err != 0:
            l.debug("Container Template Property Error Count is {}.".format(err))
            return(False)
        return(True)


test_container = {
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
}

test_container2 = {
    "containerparent": None,
    "containername": "con1",
    "containerid": "QR7G",
    "containeryearadded": 1995,
    "containerconstraints": None,
}

test_template = {
    'containertype': "box",
    'containerimx': 12,
    'containerdimy': 13,
    'containerdimz': 4,
    'containeremptyweight': 30,
    'templatename': "box1"
}

# pp(Template().list_all())
# pp(Container().from_template("LIGA", test_container))
pp(Container().from_template("LIHA", test_container2))
# pp(Template().new(test_template))

# Container().new(test)
