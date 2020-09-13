from bricklink_api.auth import oauth
from bricklink_api.catalog_item import (
    get_price_guide,
    Type,
    GuideType,
    NewOrUsed,
    VATSetting,
)
import bricklink_api.user_inventory as bui
from pprint import pprint as pp
import json
import pymongo
import uuid


def bl_auth(authfile="bricklink.json"):
    with open(authfile, "r") as blfh:
        bl_data = json.load(blfh)
    consumer_key = bl_data["consumer_key"]
    consumer_secret = bl_data["consumer_secret"]
    token_value = bl_data["token_value"]
    token_secret = bl_data["token_secret"]
    auth = oauth(consumer_key, consumer_secret, token_value, token_secret)
    return auth


def import_inventory(auth=bl_auth()):
    inventory_json = bui.get_inventories(auth=auth)
    inventory_list = list()
    if not inventory_json["meta"]["code"] == 200:
        # TODO add error handling
        return None
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    for item in inventory_json["data"]:
        item_dict = dict()
        item_dict["autoid"] = str(uuid.uuid4())
        item_dict["inventory_id"] = item["inventory_id"]
        item_dict["item_id_id"] = "{}_{}".format(
            item["item"]["type"][0], item["item"]["no"]
        )
        item_dict["color_id"] = item["color_id"]
        item_dict["count"] = item["quantity"]
        item_dict["condition_id"] = item["new_or_used"]
        if item.get("completeness"):
            item_dict["completeness_id"] = item["completeness"]
        else:
            item_dict["completeness_id"] = None
        item_dict["unit_price"] = item["unit_price"]
        item_dict["description"] = item["description"]
        item_dict["remarks"] = item["remarks"]
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
        inventory_list.append(pymongo.InsertOne(item_dict))
    db.warehouse_blinventoryitem.bulk_write(inventory_list)


import_inventory()

