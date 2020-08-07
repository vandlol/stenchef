from log import logger as l
import misc
import item_classes
import container as c

import sys
import random
from bson.son import SON
from pprint import pprint as pp


class Item:
    def __init__(self):
        self.config = misc.read_config()
        pass

    def get_uuid(self, itemid, color, condition):
        condition = misc.get_condition(condition)
        if not condition:
            l.error("Given condition is not valid.")
            sys.exit(51)
        if not misc.verify_string(itemid):
            l.error("Given itemid is not a valid string.")
            sys.exit(52)
        if not item_classes.Colors.find_one({"colorname": color}).__dict__.get("color"):
            l.error("Given color is not a valid lego color. (Case Sensitive)")
            sys.exit(53)
        search = {"itemid": itemid,
                  "itemcolor": color,
                  "itemcondition": condition}

        item = item_classes.Itemidentifier.find_one(search)
        if not item:
            l.error(
                "Could not find item with the given Combination of Itemid and Color, please check both.")
            sys.exit(54)
        item = item.__dict__.get('itemuuid')
        return(item)

    def match_uuid(self, itemuuid):
        if not misc.verify_uuid(itemuuid):
            l.error("Given itemuuid is not a valid uuid.")
            sys.exit(55)
        search = {"itemuuid": itemuuid}
        item = item_classes.Itemidentifier.find_one(search).__dict__
        del item['_id']
        return(item)

    def find(self, itemuuid):
        if not misc.verify_uuid(itemuuid):
            l.error("Given itemuuid is not a valid uuid.")
            sys.exit(56)
        containers = c.Container().list_items(
            search={"containercontent.itemuuid": itemuuid})
        return(containers)

    def store(self, itemid, color, condition, count, containerid=None):
        uuid = self.get_uuid(itemid, color, condition)
        action = "store"
        containerid, ret_count = self.edit(action, uuid, count, containerid)
        l.info("{} Items of Catalog Item {} in Color {} with condition {} have been stored into Container {}".format(
            count, itemid, color, condition,  containerid))
        return(uuid)

    def pick(self, itemid, color, condition, count, containerid=None):
        uuid = self.get_uuid(itemid, color, condition)
        action = "pick"
        containerid, ret_count = self.edit(action, uuid, count, containerid)
        l.info("{} Items of Catalog Item {} in Color {} with condition {} have been picked from Container {}".format(
            count, itemid, color, condition,  containerid))
        if ret_count == 0:
            if self.config["storage"]["remove_empty_entries"]:
                self.remove(containerid, uuid, 0)
        return(uuid)

    def edit(self, action, uuid, count, containerid):
        if not action == "pick" and not action == "store":
            l.error("Invalid action (not pick/store) given.")
            sys.exit(57)

        if not misc.verify_int(count) or not misc.verify_positive_num(count):
            l.error("Given item count it not a positive integer.")
            sys.exit(58)

        if not containerid:
            # TODO add handling for more than one container
            found = 0
            containerid = self.find(uuid)
            if not containerid:
                if action == "pick":
                    l.error(
                        "Could not find Container containing the requested item.")
                    sys.exit(60)
                containerid = c.Container().random()
            else:
                containerid = containerid[0].get("containerid")
                found += 1
        if not misc.verify_id(containerid):
            l.error("Given containerid is not valid.")
            sys.exit(59)
        container = c.Container().find_cursor(containerid)
        ret_count = 0
        if action == "store":
            if found:
                for item in container.containercontent:
                    if item.get("itemuuid") == uuid:
                        item["count"] += count
                        ret_count = item["count"]
                        break
                container.save()
            else:
                container.containercontent.append(
                    {"itemuuid": uuid, "count": count})
                ret_count = count
                container.save()

        elif action == "pick":
            for item in container.containercontent:
                if item.get("itemuuid") == uuid:
                    if item["count"] < count:
                        l.error(
                            "Container does not contain enough items to satisfy request.")
                        sys.exit(61)
                    item["count"] -= count
                    ret_count = item["count"]
                    break
            container.save()

        return(containerid, ret_count)

    def remove(self, containerid, uuid, count):
        container = c.Container().find_cursor(containerid)
        container.containercontent.remove(
            {'itemuuid': uuid, 'count': count})
        l.info("Item {} was removed from container {}.".format(uuid, containerid))
        container.save()
        return(container.containerid)


# random_containerid = c.Container().random()
# pp(c.Container().find(random_containerid))
# pp(Item().get("3011"))
# pp(Item().find("3011", color="Red"))
# pp(Item().store("3011", "Light Bluish Gray", "used", 15))

pp(Item().pick("3011", "Light Bluish Gray", "used", 15))
# pp(Item().edit("store", "644896f6-370f-4028-88fb-5073b6b3ccb5", 5, None))
