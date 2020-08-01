from log import logger as l
import misc
import item_classes
import sys

from pprint import pprint as pp


class Template:
    def __init__(self):
        self.config = misc.read_config()
        self.mandatory_properties = ["containertype"]
        self.numerical_properties = [
            "containerdimx", "containerdimy", "containerdimz", "containeremptyweight"]
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

    def list_items(self, search=None):
        ret_list = list()
        if not search:
            for item in list(item_classes.Templates.find()):
                ret_list.append(item.__dict__)
        else:
            for item in list(item_classes.Templates.find(search)):
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

    def delete(self, templateid):
        if not templateid:
            l.error("No templateid given.")
            sys.exit("36")
        templates = self.list_items(search={"templateid": templateid})
        if templates:
            for template in templates:
                item_classes.Containers(template).delete()
                l.info(
                    "Deleted Container Template with templateid: {}".format(templateid))
            return(True)
        l.error(
            "Could not find Container Template with templateid: {}".format(templateid))
        return(False)
