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
        config = misc.read_config()
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
        container = self.edit(action, uuid, count, containerid)
        # TODO logging
        return(container)

    def pick(self, itemid, color, condition, count, containerid=None):
        # TODO maybe have a "item available" check?
        uuid = self.get_uuid(itemid, color, condition)
        action = "pick"
        container = self.edit(action, uuid, count, containerid)
        # TODO logging
        return(container)

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
            containerid = self.find(uuid)[0]
            if not containerid:
                if action == "pick":
                    l.error(
                        "Could not find Container containing the requested item.")
                    sys.exit(60)
                containerid = c.Container().random()
            else:
                containerid = containerid.get("containerid")
                found += 1
        if not misc.verify_id(containerid):
            l.error("Given containerid is not valid.")
            sys.exit(59)
        container = c.Container().find_cursor(containerid)

        if action == "store":
            if found:
                for item in container.containercontent:
                    if item.get("itemuuid") == uuid:
                        item["count"] += count
                        break
                container.save()
                return(container.containerid)
            else:
                container.containercontent.append(
                    {"itemuuid": uuid, "count": count})
                container.save()
                return(container.containerid)

        elif action == "pick":
            pass
        return("how did you even get here?")

    def remove(self, containerid, item):
        pass


# random_containerid = c.Container().random()
# pp(c.Container().find(random_containerid))
# pp(Item().get("3011"))
# pp(Item().find("3011", color="Red"))
# pp(Item().edit("p", "QR7G", "3011", "Red", 4))


pp(Item().edit("store", "644896f6-370f-4028-88fb-5073b6b3ccb5", 5, None))
