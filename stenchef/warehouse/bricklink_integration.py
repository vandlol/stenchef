from bricklink_api.auth import oauth
from bricklink_api.catalog_item import (
    get_subsets,
    get_price_guide,
    Type,
    GuideType,
    NewOrUsed,
    VATSetting,
    get_item_image,
)
import bricklink_api.user_inventory as bui
from pprint import pprint as pp
import json
import pymongo
import uuid

typemap = {
    "P": Type.PART,
    "B": Type.BOOK,
    "M": Type.MINIFIG,
    "G": Type.GEAR,
    "S": Type.SET,
    "C": Type.CATALOG,
    "I": Type.INSTRUCTION,
    "O": Type.ORIGINAL_BOX,
    "U": Type.UNSORTED_LOT,
}


def bl_auth(data):
    consumer_key = data.bl_consumer_key
    consumer_secret = data.bl_consumer_secret
    token_value = data.bl_token_value
    token_secret = data.bl_token_secret
    auth = oauth(consumer_key, consumer_secret, token_value, token_secret)
    return auth


def import_inventory(owner, auth=None):
    inventory_json = bui.get_inventories(auth=auth)
    inventory_list = list()
    if not inventory_json["meta"]["code"] == 200:
        # TODO add error handling
        return None
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    for item in inventory_json["data"]:
        item_dict = dict()
        filter = dict()
        filter["item_id_id"] = "{}_{}".format(
            item["item"]["type"][0], item["item"]["no"]
        )
        filter["color_id"] = str(item["color_id"])
        filter["condition_id"] = item["new_or_used"]
        filter["owner_id"] = owner

        found = db.warehouse_blinventoryitem.find_one(filter)

        item_dict["inventory_id"] = item["inventory_id"]
        item_dict["count"] = item["quantity"]
        if item.get("completeness"):
            item_dict["completeness_id"] = item["completeness"]
        else:
            item_dict["completeness_id"] = None
        item_dict["unit_price"] = item["unit_price"]
        item_dict["description"] = item["description"]
        item_dict["container"] = item["remarks"]
        item_dict["bulk"] = item["bulk"]
        item_dict["is_retain"] = item["is_retain"]
        item_dict["is_stock_room"] = item["is_stock_room"]
        item_dict["sale_rate"] = item["sale_rate"]
        item_dict["tier_quantity1"] = item["tier_quantity1"]
        item_dict["tier_price1"] = item["tier_price1"]
        item_dict["tier_quantity2"] = item["tier_quantity2"]
        item_dict["tier_price2"] = item["tier_price2"]
        item_dict["tier_quantity3"] = item["tier_quantity3"]
        item_dict["tier_price3"] = item["tier_price3"]

        if found:
            inventory_list.append(pymongo.ReplaceOne(filter, item_dict, upsert=True))
        else:
            item_dict["storedid"] = uuid.uuid4()
            item_dict["autoid"] = uuid.uuid4()
            add_item = {**filter, **item_dict}
            inventory_list.append(pymongo.InsertOne(add_item))
    db.warehouse_blinventoryitem.bulk_write(inventory_list)
    return inventory_list


def part_out_set(set, owner, subset="1", auth=None):
    type = Type.SET
    partout = get_subsets(
        type,
        "{}-{}".format(set, subset),
        instruction=True,
        box=False,
        break_minifigs=False,
        break_subsets=True,
        auth=auth,
    )
    if not partout.get("meta"):
        return None

    if not partout["meta"]["code"] == 200:
        return None

    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    parts = list()
    for item in partout["data"]:
        entry = None
        if not item["match_no"] == 0:
            for e in item["entries"]:
                if e["is_alternate"]:
                    entry = e
                break
        entry = item["entries"][0]
        filter = {
            "owner_id": owner,
            "item_id_id": "{}_{}".format(
                entry["item"]["type"][:1], entry["item"]["no"]
            ),
            "color_id": "{}".format(entry["color_id"]),
            "condition_id": "N",
        }
        stored = db.warehouse_blinventoryitem.find_one(filter)
        pai = {
            "color_id": entry["color_id"],
            "quantity": entry["quantity"] + entry["extra_quantity"],
            "item_uid": "{}_{}".format(entry["item"]["type"][:1], entry["item"]["no"]),
            "itemid": entry["item"]["no"],
            "itemtype": entry["item"]["type"][:1],
            "storedid": None,
            "storedcount": 0,
            "storedcontainer": None,
        }
        if stored:
            pai["storedid"] = stored["storedid"]
            pai["storedcount"] = stored["count"]
            container = db.warehouse_container.find_one(
                {"containerid": stored["container_id"]}
            )
            pai["storedcontainer"] = container
        parts.append(pai)
    return parts
