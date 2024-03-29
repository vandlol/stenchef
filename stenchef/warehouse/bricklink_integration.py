from telnetlib import STATUS
from bricklink_api.auth import oauth
from bricklink_api.catalog_item import (
    get_subsets,
    get_price_guide,
    Type,
    GuideType,
    NewOrUsed,
    VATSetting,
    get_item_image,
    get_known_colors,
)
from bricklink_api.order import (
    get_orders,
    get_order,
    get_order_items,
    Direction,
    Status,
    update_order_status,
)
from bricklink_api.feedback import post_feedback
import bricklink_api.user_inventory as bui
from pprint import pprint as pp
import json
import pymongo
import uuid
import re
from datetime import datetime, timedelta
from dateutil import parser
import redis
import subprocess
from warehouse.format_label import format_label as fl

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

tmap = {
    "P": "PART",
    "B": "BOOK",
    "M": "MINIFIG",
    "G": "GEAR",
    "S": "SET",
    "C": "CATALOG",
    "I": "INSTRUCTION",
    "O": "ORIGINAL_BOX",
    "U": "UNSORTED_LOT",
}


def bl_auth(data):
    consumer_key = data.bl_consumer_key
    consumer_secret = data.bl_consumer_secret
    token_value = data.bl_token_value
    token_secret = data.bl_token_secret
    auth = oauth(consumer_key, consumer_secret, token_value, token_secret)
    return auth


def bl_auth_test():
    with open("../bricklink.json", "r") as file:
        data = json.load(file)
    consumer_key = data["bl_consumer_key"]
    consumer_secret = data["bl_consumer_secret"]
    token_value = data["bl_token_value"]
    token_secret = data["bl_token_secret"]
    auth = oauth(consumer_key, consumer_secret, token_value, token_secret)
    return auth


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def get_color(color_id):
    r = redis.Redis(host="localhost", port=6379, db=4)
    found = r.get(color_id)
    if found:
        return found.decode("ascii")

    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    filter = {"color": str(color_id)}
    sten_found = db.meta_color.find_one(filter)
    r.set(color_id, sten_found["colorname"])
    return sten_found["colorname"]


def query_price(itemtype_id, itemid, color_id, condition, settings, auth=None):
    r = redis.Redis(host="localhost", port=6379, db=3)
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    datelimit = datetime.today() - timedelta(days=30)
    filter = "{}-{}-{}-{}".format(itemtype_id, itemid, color_id, condition)
    do_not_store = True
    found = r.get(filter)
    price_prop = 0
    if found:
        found = json.loads(found.decode("ascii"))
        date_form = datetime.strptime(found["date"], "%d.%m.%y")
        if date_form > datelimit and not found["price_prop"] == 0.0:
            price_prop = found["price_prop"]
    if price_prop == 0:
        price_guide_item = get_price_guide(
            typemap[itemtype_id],
            itemid,
            color_id,
            guide_type="sold",
            new_or_used=condition,
            region="europe",
            country_code="DE",
            currency_code="EUR",
            auth=auth,
        )
        if (
            not price_guide_item
            or (not price_guide_item.get("data"))
            or (price_guide_item["data"].get("avg_price") == "0.0000")
        ):
            price_guide_item = get_price_guide(
                typemap[itemtype_id],
                itemid,
                color_id,
                guide_type="stock",
                new_or_used=condition,
                region="europe",
                country_code="DE",
                currency_code="EUR",
                auth=auth,
            )

        if not price_guide_item or (not price_guide_item.get("data")):
            return float(0.0000)
        else:
            do_not_store = False
        avg = float(price_guide_item["data"]["qty_avg_price"])
        perc = 0
        if condition == "U":
            perc = settings.get("percentage_used")
        elif condition == "N":
            perc = settings.get("percentage_new")
        if str(perc).startswith("-"):
            perc = int(str(perc).replace("-", ""))
            price_prop = avg - ((avg / 100) * perc)
        else:
            price_prop = avg + ((avg / 100) * perc)
        if not price_prop == 0.0:
            p_data = dict()
            p_data["price_prop"] = price_prop
            p_data["date"] = datetime.today().strftime("%d.%m.%y")
            if not do_not_store:
                r.set(filter, json.dumps(p_data))
    return round(price_prop, 4)


def sync_deleted_inventories(owner, auth=None):
    inventory_json = bui.get_inventories(auth=auth)
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    known_inventory_ids = list()
    for inv in inventory_json["data"]:
        known_inventory_ids.append(inv.get("inventory_id"))
    known_inventory_ids.append(None)
    db.warehouse_blinventoryitem.delete_many(
        {"inventory_id": {"$nin": known_inventory_ids}}
    )


def get_or_create_container(owner, db, search):
    default_containertype_id = "1dba3efc-1590-4768-aa7f-5ea21ca255f6"
    found = db.warehouse_container.find_one({"name": re.compile(search, re.IGNORECASE)})
    if found:
        return found.get("containerid")
    else:
        new_id = uuid.uuid4()
        container_data = {
            "containerid": new_id,
            "name": search.upper(),
            "containertype_id": uuid.UUID(default_containertype_id),
            "slug": search.lower(),
            "date_added": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "owner_id": owner,
            "parent_id": None,
            "description": "This Container has automatically been added with type: default",
        }
        db.warehouse_container.insert_one(container_data)
        return new_id


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
        if found:
            item_dict = found.copy()

        item_dict["inventory_id"] = item["inventory_id"]
        item_dict["count"] = item["quantity"]
        if item.get("completeness"):
            item_dict["completeness_id"] = item["completeness"]
        else:
            item_dict["completeness_id"] = None
        item_dict["unit_price"] = item["unit_price"]
        item_dict["description"] = item["description"]
        if item.get("remarks"):
            if is_valid_uuid(item["remarks"]):
                item_dict["container_id"] = uuid.UUID(item["remarks"])
            else:
                item_dict["container_id"] = get_or_create_container(
                    owner, db, item["remarks"]
                )
        else:
            item_dict["container_id"] = None
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
            add_item = {**filter, **item_dict}
            inventory_list.append(pymongo.InsertOne(add_item))
    db.warehouse_blinventoryitem.bulk_write(inventory_list)
    return inventory_list


def update_all_remarks(owner, auth=bl_auth_test()):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    local_inventories = db.warehouse_blinventoryitem.find({"owner_id": owner})
    for local_inventory in local_inventories:
        found = db.warehouse_container.find_one(
            {"containerid": local_inventory["container_id"]}
        )
        if not found:
            pp(local_inventory)
        temp = dict()
        temp["remarks"] = found.get("name")
        pp(local_inventory.get("inventory_id"))
        pp(temp)
        print("---")
        bui.update_inventory(local_inventory.get("inventory_id"), temp, auth=auth)


def export_inventory_full(owner, auth=bl_auth_test()):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    local_inventories = db.warehouse_blinventoryitem.find({"owner_id": owner})
    create_list = list()
    for local_inventory in local_inventories:
        if local_inventory.get("inventory_id"):
            continue
        found = db.warehouse_container.find_one(
            {"containerid": local_inventory["container_id"]}
        )
        local_inventory["container_id"] = found.get("name")
        temp = _prep_inventory_data(local_inventory)
        bui.create_inventory(temp, auth=auth)
        # pp(temp)
        # create_list.append(temp)
    # bui.create_inventories(create_list, auth=auth)


def export_inventory_single(owner, storedid, auth=bl_auth_test()):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    local_inventory = db.warehouse_blinventoryitem.find_one(
        {"owner_id": owner, "storedid": storedid}
    )
    found = db.warehouse_container.find_one(
        {"containerid": local_inventory["container_id"]}
    )
    local_inventory["container_id"] = found.get("name")
    temp = _prep_inventory_data(local_inventory)
    bui.create_inventory(temp, auth=auth)


def _prep_inventory_data(local_inventory):
    temp = dict()
    temp["item"] = dict()
    temp["item"]["type"], temp["item"]["no"] = local_inventory["item_id_id"].split("_")
    temp["item"]["type"] = tmap[temp["item"]["type"]]
    temp["color_id"] = local_inventory["color_id"]
    temp["new_or_used"] = local_inventory["condition_id"]
    temp["quantity"] = local_inventory["count"]
    if local_inventory.get("completeness_id"):
        temp["completeness"] = local_inventory["completeness_id"]
    temp["unit_price"] = local_inventory["unit_price"]
    temp["description"] = local_inventory["description"]
    temp["remarks"] = str(local_inventory["container_id"])
    temp["bulk"] = local_inventory["bulk"]
    temp["is_retain"] = local_inventory["is_retain"]
    temp["is_stock_room"] = local_inventory["is_stock_room"]
    temp["sale_rate"] = local_inventory["sale_rate"]
    temp["tier_quantity1"] = local_inventory["tier_quantity1"]
    temp["tier_price1"] = local_inventory["tier_price1"]
    temp["tier_quantity2"] = local_inventory["tier_quantity2"]
    temp["tier_price2"] = local_inventory["tier_price2"]
    temp["tier_quantity3"] = local_inventory["tier_quantity3"]
    temp["tier_price3"] = local_inventory["tier_price3"]
    return temp


def update_container(owner, inventory_id, container_id, auth=bl_auth_test()):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    found = db.warehouse_container.find_one({"containerid": uuid.UUID(container_id)})
    temp = dict()
    temp["remarks"] = found.get("name")
    bui.update_inventory(inventory_id, temp, auth=auth)


def add_quantity(
    owner, itemid, color_id, condition, quantity: int, auth=bl_auth_test()
):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    local_inventory = db.warehouse_blinventoryitem.find_one(
        {
            "owner_id": owner,
            "item_id_id": itemid,
            "color_id": color_id,
            "condition_id": condition,
        }
    )

    temp = dict()
    if not local_inventory.get("inventory_id"):
        # TODO Error Handling
        return None

    temp["quantity"] = +quantity

    bui.update_inventory(local_inventory["inventory_id"], temp, auth=auth)


def update_price(owner, itemid, color_id, condition, price, auth=bl_auth_test()):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    local_inventory = db.warehouse_blinventoryitem.find_one(
        {
            "owner_id": owner,
            "item_id_id": itemid,
            "color_id": color_id,
            "condition_id": condition,
        }
    )

    temp = dict()
    if not local_inventory:
        print("could not find {} {} in localdb".format(itemid, color_id))
        return None
    if not local_inventory.get("inventory_id"):
        # TODO Error Handling
        return None

    temp["unit_price"] = price

    ret = bui.update_inventory(local_inventory["inventory_id"], temp, auth=auth)


def update_all_prices(auth=bl_auth_test()):
    inventory_json = bui.get_inventories(auth=auth)
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef

    if not inventory_json.get("meta"):
        return None

    if not inventory_json["meta"]["code"] == 200:
        return None

    owner_id = db.auth_user.find_one({"username": "admin"})["id"]
    settings = db.user_setting.find_one({"owner_id": owner_id})
    for item in inventory_json["data"]:
        itemtype_id = item["item"]["type"][:1]
        itemid = item["item"]["no"]
        color_id = item["color_id"]
        condition = item["new_or_used"]
        price_prop = query_price(
            itemtype_id, itemid, color_id, condition, settings, auth=auth
        )
        if price_prop == item["unit_price"]:
            print("Price Stable: {}".format(item["inventory_id"]))
            continue
        if price_prop != 0.0:
            update_price(
                owner_id,
                "{}_{}".format(itemtype_id, itemid),
                str(color_id),
                condition,
                price_prop,
                auth=auth,
            )
            print("Updated: {}".format(item["inventory_id"]))
            continue
        print("No Price found: {}".format(item["inventory_id"]))


def known_colors(itemtype_id, itemid, auth=None):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.colors
    datelimit = datetime.today() - timedelta(days=10)
    filter = {
        "itemtype_id": itemtype_id,
        "itemid": itemid,
    }
    found = db.colors.find_one(filter)
    colors = list()
    if found:
        date_form = datetime.strptime(found["date"], "%d.%m.%y")
        if date_form > datelimit:
            colors = found["known_colors"]
    if not colors:
        colors_q = get_known_colors(
            typemap[itemtype_id],
            itemid,
            auth=auth,
        )
        if not colors_q or (not colors_q.get("data")):
            return list()
        for color in colors_q["data"]:
            color_name = get_color(color["color_id"])
            colors.append(
                {
                    "color_id": str(color["color_id"]),
                    "colorname": color_name,
                }
            )
        filter["known_colors"] = colors
        filter["date"] = datetime.today().strftime("%d.%m.%y")
        db.colors.insert_one(filter)
    return sorted(colors, key=lambda i: i["colorname"])


def part_out_set(
    set, owner, subset="1", multi=1, itemtype="SET", break_minifigs=False, auth=None
):
    if itemtype == "SET":
        type = Type.SET
        setid = "{}-{}".format(set, subset)
    if itemtype == "GEAR":
        type = Type.GEAR
        setid = set
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    settings = db.user_setting.find_one({"owner_id": owner})

    filter = {"setid": setid}
    found = db.partout.find_one(filter)

    partout = get_subsets(
        type,
        setid,
        instruction=True,
        box=False,
        break_minifigs=break_minifigs,
        break_subsets=True,
        auth=auth,
    )
    if not partout.get("meta"):
        return None

    if not partout["meta"]["code"] == 200:
        return None
    partout = partout["data"]

    set_stats = {
        "pieces": 0,
        "new_pieces": 0,
        "stored_pieces": 0,
        "pov": 0,
        "lots": 0,
        "new_lots": 0,
        "stored_lots": 0,
    }
    parts = list()
    for item in partout:
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
            "quantity": int(entry["quantity"]) * int(multi),
            "item_uid": "{}_{}".format(entry["item"]["type"][:1], entry["item"]["no"]),
            "item_name": entry["item"]["name"],
            "itemid": entry["item"]["no"],
            "itemtype": entry["item"]["type"][:1],
            "storedid": None,
            "storedcount": 0,
            "storedcontainer": None,
            "condition": "N",
            "price_prop": query_price(
                entry["item"]["type"][:1],
                entry["item"]["no"],
                entry["color_id"],
                "N",
                settings,
                auth=auth,
            ),
        }
        set_stats["lots"] += 1
        set_stats["pieces"] += int(entry["quantity"]) * int(multi)
        set_stats["pov"] += float(
            int(entry["quantity"]) * int(multi) * float(pai["price_prop"])
        )
        if stored:
            set_stats["stored_lots"] += 1
            set_stats["stored_pieces"] += int(entry["quantity"]) * int(multi)
            pai["storedid"] = stored["storedid"]
            pai["storedcount"] = stored["count"]
            container = db.warehouse_container.find_one(
                {"containerid": stored["container_id"]}
            )
            pai["storedcontainer"] = container
        else:
            set_stats["new_lots"] += 1
            set_stats["new_pieces"] += int(entry["quantity"]) * int(multi)
        parts.append(pai)
    set_stats["pov"] = round(set_stats["pov"], 2)
    return parts, set_stats


def import_orders(orders, auth=None):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef

    for order in orders:
        filter = {"order_id": order["order_id"]}
        found = db.warehouse_order.find_one(filter)
        if found:
            if order["status"] == "COMPLETED":
                continue
            if found["status"] == order["status"]:
                continue
            found["status"] = order["status"]
            if order.get("shipping"):
                if order["shipping"].get("date_shipped"):
                    found["shipping_date"] = parser.parse(
                        order["shipping"].get("date_shipped")
                    )
            if order["payment"].get("date_paid"):
                found["payment_date"] = parser.parse(order["payment"].get("date_paid"))
            db.warehouse_order.find_one_and_replace(filter, found)

        if order["status"] == "CANCELLED":
            continue

        order_details = get_order(order["order_id"], auth=auth)
        order_items = generate_picklist(order["order_id"], auth=auth)
        order_data = _prep_order_data(order_details["data"])
        db.warehouse_order.insert(order_data)
        items = _prep_order_item_data(order_items, order_data["orderuuid"])
        db.warehouse_orderitem.bulk_write(items)
    return


def status_and_praise(orderid, auth=None):
    set_order_status_packed(orderid, auth=auth)
    give_praise(orderid, auth=auth)
    return


def set_order_status_packed(orderid, auth=None):
    update_order_status(orderid, Status.PACKED, auth=auth)
    return


def give_praise(orderid, auth=None):
    rating = 0
    comment = "Thank you for your purchase."
    feedback_dict = {"order_id": orderid, "rating": rating, "comment": comment}
    post_feedback(feedback_dict, auth=auth)
    return


def _prep_order_item_data(order_items, orderid):
    items = list()
    for order_item in order_items[0]:
        data = dict()
        data["orderitemuuid"] = uuid.uuid4()
        data["order_id"] = orderid
        data["item_id"] = "{}_{}".format(
            order_item["item"]["type"][:1], order_item["item"]["no"]
        )
        data["condition_id"] = order_item["new_or_used"]
        data["color_id"] = order_item["color_id"]
        data["count"] = order_item["quantity"]
        data["unit_price"] = order_item["disp_unit_price_final"]
        items.append(pymongo.InsertOne(data))
    return items


def _prep_order_data(order_details):
    data = dict()
    data["orderuuid"] = uuid.uuid4()
    data["order_id"] = order_details["order_id"]
    data["buyer_name"] = order_details["buyer_name"]
    data["buyer_email"] = order_details["buyer_email"]
    data["date_ordered"] = parser.parse(order_details["date_ordered"])
    data["total_price"] = order_details["disp_cost"]["grand_total"]
    data["subtotal_price"] = order_details["disp_cost"]["subtotal"]
    data["shipping_price"] = order_details["disp_cost"]["shipping"]
    data["handling_fee"] = order_details["disp_cost"]["etc1"]
    data["payment_metod"] = order_details["payment"]["method"]
    if order_details["payment"].get("date_paid"):
        data["payment_date"] = parser.parse(order_details["payment"].get("date_paid"))
    data["shipping_state"] = order_details["shipping"]["address"]["state"]
    data["shipping_country"] = order_details["shipping"]["address"]["country_code"]
    if order_details["shipping"].get("date_shipped"):
        data["shipping_date"] = parser.parse(
            order_details["shipping"].get("date_shipped")
        )
    data["shipping_method"] = order_details["shipping"]["method"]
    data["status"] = order_details["status"]
    data["item_count"] = order_details["total_count"]
    data["lot_count"] = order_details["unique_count"]
    data["weight"] = order_details["total_weight"]
    return data


def orders_query(auth=None):
    orders = get_orders(
        auth=auth,
        filed=False,
        direction=Direction.IN,
        status="-cancelled,-shipped,-completed,-received,-npb,-purged",
    )
    if not orders.get("meta"):
        return None

    if not orders["meta"]["code"] == 200:
        return None
    import_orders(orders["data"], auth=auth)
    orders_comp = list()
    for order in orders["data"]:
        order_details = get_order(order["order_id"], auth=auth)
        orders_comp.append(order_details["data"])
    return orders_comp


def order_query(order_id, auth=None):
    order_details = get_order(order_id, auth=auth)
    if not order_details.get("meta"):
        return None

    if not order_details["meta"]["code"] == 200:
        return None
    return order_details["data"]


def generate_picklist(order_id, auth=None):
    items = get_order_items(order_id, auth=auth)
    if not items.get("meta"):
        return None

    if not items["meta"]["code"] == 200:
        return None

    return items["data"]


def query_inventory_prices(owner, auth=None):
    client = pymongo.MongoClient("localhost", 27017)
    db = client.stenchef
    owner_id = db.auth_user.find_one({"username": owner})["id"]
    settings = db.user_setting.find_one({"owner_id": owner_id})
    items = db.warehouse_blinventoryitem.find({"owner_id": owner_id})
    for item in items:
        if not item.get("inventory_id"):
            continue
        itemtype_id, itemid = item["item_id_id"].split("_")
        new_price = query_price(
            itemtype_id,
            itemid,
            item["color_id"],
            item["condition_id"],
            settings,
            auth=auth,
        )
        if new_price == 0.0:
            continue
        update_price(
            owner_id,
            item["item_id_id"],
            item["color_id"],
            item["condition_id"],
            new_price,
            auth=auth,
        )


def print_label(order_details):
    name = order_details["shipping"]["address"]["name"]["full"].replace("\r", "")
    address = order_details["shipping"]["address"]["address1"]
    if order_details["shipping"]["address"]["address2"]:
        address = address = "{}\n{}".format(
            order_details["shipping"]["address"]["address1"],
            order_details["shipping"]["address"]["address2"],
        )
    if re.match(r"^\d+$", order_details["shipping"]["address"]["address2"]):
        address = "{} {}".format(
            order_details["shipping"]["address"]["address1"],
            order_details["shipping"]["address"]["address2"],
        )
    postal_city = "{} {}".format(
        order_details["shipping"]["address"]["postal_code"],
        order_details["shipping"]["address"]["city"],
    )

    fl("{}\n{}\n{}".format(name, address, postal_city))
    bash_cmd1 = ["lpr -P LabelWriter-450-Turbo -o PageSize=h90.7w161.5 sender.pdf"]
    bash_cmd2 = ["lpr -P LabelWriter-450-Turbo -o PageSize=h90.7w161.5 label.pdf"]
    subprocess.Popen(bash_cmd1, stdout=subprocess.PIPE, shell=True)
    subprocess.Popen(bash_cmd2, stdout=subprocess.PIPE, shell=True)


def custom_label(name, address, postal_code, city):
    fl("{}\n{}\n{} {}".format(name, address, postal_code, city))
    bash_cmd1 = ["lpr -P LabelWriter-450-Turbo -o PageSize=h90.7w161.5 sender.pdf"]
    bash_cmd2 = ["lpr -P LabelWriter-450-Turbo -o PageSize=h90.7w161.5 label.pdf"]
    subprocess.Popen(bash_cmd1, stdout=subprocess.PIPE, shell=True)
    subprocess.Popen(bash_cmd2, stdout=subprocess.PIPE, shell=True)