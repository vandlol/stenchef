from log import logger as l
import misc
import item_classes
import container

import sys
import random
from bson.son import SON
from pprint import pprint as pp


class Item:
    def __init__(self):
        pass

    def get(self, search):
        search = {"itemid": search}
        if not isinstance(search, dict):
            search = {"itemid": search}
        item = item_classes.Catalog.find_one(search).__dict__
        del item['_id']
        return(item)

    def find(self, itemid, color=None):
        if not color:
            containers = container.Container().list_items(
                search={"containercontent.itemid": itemid})
        else:
            containers = container.Container().list_items(
                search={"containercontent.itemid": itemid, "containercontent.storagecolor": color})

        return(containers)

    def add(self, itemid, color, count, containerid=None):
        # TODO validate inputs
        search = {"itemid": itemid}
        item_data = item_classes.Catalog.find_one(search).__dict__
        del item_data['_id']
        # if not color in item_data['itemcolors']:
        #     print(Invalid Item/Color combination.)
        #     # TODO error handling
        # del item_data['itemcolors']
        item_data['storagecolor'] = color
        item_data['storagecount'] = count

        if not containerid:
            containers = self.find(itemid, color=color)
            if not containers:
                containerid = container.Container().random()
            else:

                containerid = random.choice(containers)['containerid']

        item_container = container.Container().find_cursor(
            {"containerid": containerid})

        # TODO Broken
        item_container.containercontent.append(item_data)
        item_container.save()
        return(containerid)

    def edit(self, containerid, itemid, color, count, action="store"):
        pass

    def remove(self, containerid, item):
        pass


# random_containerid = container.Container().random()
# pp(container.Container().find(random_containerid))
pp(Item().get("3011"))
# pp(Item().find("3011", color="Red"))
# pp(Item().add("3011", "Blue", 10, containerid="5ZAF"))
