from log import logger as l
import misc
import item_classes
import template as t

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
        item_classes.Containers(self.container).save()
        l.info("Created Container with containerid: {}".format(
            self.container["containerid"]))
        return(self.container["containerid"])

    def from_template(self, templateid, container):
        self.container = t.Template().load(templateid=templateid)
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

    def list_items(self, search=None):
        ret_list = list()
        if not search:
            for item in list(item_classes.Containers.find()):
                ret_list.append(item.__dict__)
        else:
            for item in list(item_classes.Containers.find(search)):
                ret_list.append(item.__dict__)
        return(ret_list)

    def delete(self, containerid):
        if not containerid:
            l.error("No containerid given.")
            sys.exit("36")
        containers = self.list_items(search={"containerid": containerid})
        if containers:
            for container in containers:
                item_classes.Containers(container).delete()
                l.info("Deleted Container with containerid: {}".format(containerid))
            return(True)
        l.error("Could not find Container with containerid: {}".format(containerid))
        return(False)


test_container = {
    "containertype": "container",
    "containerimx": 9,
    "containerdimy": 5,
    "containerdimz": 3,
    "containeremptyweight": 15,
    "containerparent": None,
    "containername": "con1",
    "containeryearadded": 1995,
    "containerconstraints": None,
}

test_container2 = {
    "containerparent": None,
    "containername": "con1",
    "containerid": "QR7G",
    "containeryearadded": 2020,
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

# pp(t.Template().list_items())
# pp(Container().from_template("LIGA", test_container))
# pp(Container().from_template("LIHA", test_container2))
# pp(Container().list_items())
# pp(Container().delete('QR7G'))
# pp(t.Template().new(test_template))

# Container().new(test)
