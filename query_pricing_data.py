from bricklink_api.auth import oauth
from bricklink_api.catalog_item import get_price_guide, Type, GuideType, NewOrUsed, VATSetting
from pprint import pprint as pp
import json
import os.path
from influxdb import InfluxDBClient
import pymongo


with open('bricklink.json', 'r') as blfh:
    bl_data = json.load(blfh)
consumer_key = bl_data["consumer_key"]
consumer_secret = bl_data["consumer_secret"]
token_value = bl_data["token_value"]
token_secret = bl_data["token_secret"]
auth = oauth(consumer_key, consumer_secret, token_value, token_secret)
client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('prices')
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["stenchef"]
m_color = mydb["meta_color"]
m_code = mydb["meta_code"]
m_catalog = mydb["catalog_item"]
with open('imported_list.txt', 'r') as text_file:
    imported = text_file.read().split('\n')
    text_file.close()

parts = m_catalog.find({"itemtype_id": "P"})
for part in parts:
    part_id = part['itemid']
    if part_id in imported:
        print("skipped {}".format(part_id))
        continue
    colors = m_code.find({"itemid_id": part_id})
    colorcount = 0
    for color in colors:
        ts_list = list()
        color_id = m_color.find_one(
            {'colorname': color['color_id']})['color']
        colorcount += 1
        for c in ['u', 'n']:
            if c == 'u':
                json_obj = get_price_guide(Type.PART, part_id, color_id, GuideType.SOLD,
                                           NewOrUsed.USED, vat=VATSetting.DEFAULT, auth=auth)
            else:
                json_obj = get_price_guide(Type.PART, part_id, color_id, GuideType.SOLD,
                                           NewOrUsed.NEW, vat=VATSetting.DEFAULT, auth=auth)
            condition = json_obj['data']['new_or_used']
            itemid = json_obj['data']['item']['no']
            itemtype = json_obj['data']['item']['type'].lower()
            currency = json_obj['data']['currency_code']

            for obj in json_obj['data']['price_detail']:
                ts_obj = {
                    "measurement": "price",
                    "tags": {
                        "type": itemtype,
                        "itemid": itemid,
                        "condition": condition,
                        "currency": currency,
                        "color": color,
                        "seller_country_code": obj['seller_country_code'],
                        "buyer_country_code": obj['buyer_country_code']
                    },
                    "time": obj['date_ordered'],
                    "fields": {
                        "unit_price": float(obj['unit_price']),
                        "quantity": int(obj['quantity'])
                    }
                }
                ts_list.append(ts_obj)
        if ts_list:
            client.write_points(ts_list)
    with open('imported_list.txt', 'a') as text_file:
        text_file.write('{}\n'.format(part_id))
        text_file.close()
    print("imported {} in {} colors".format(part_id, colorcount))
pp