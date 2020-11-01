import requests
import json
from pprint import pprint as pp
import datetime
import dateutil.parser
from datetime import datetime, timedelta
import re

with open("../lexoffice_data.json", "r") as file:
    lex_data = json.load(file)

base_url = "https://api.lexoffice.io/v1"
headers = {
    "Authorization": "Bearer {}".format(lex_data["api_key"]),
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def unquote(name):
    name = name.replace("&#40;", "(")
    name = name.replace("&#41;", ")")
    return name


def fill_data(invoice_data, ordered_items, shipping_target=5):
    order_date = dateutil.parser.parse(invoice_data["date_ordered"])
    shipping_target_date = order_date + timedelta(days=shipping_target)
    paypal_label = "Betrag bereits per PayPal bezahlt."
    if not invoice_data["shipping"]["address"]["country_code"] == "DE":
        paypal_label = "Order already paid using PayPal."

    ordered_items_c = list()
    for items_l in ordered_items:
        ordered_items_c = ordered_items_c + items_l

    items = list()
    for item in ordered_items_c:
        if item["color_name"] == "(Not Applicable)":
            item_name = item["item"]["name"]
        else:
            item_name = "{}{}".format(item["color_name"], item["item"]["name"])

        item_name = unquote(item_name)
        item_dict = {
            "type": "custom",
            "name": item_name,
            "quantity": item["quantity"],
            "unitName": "pcs",
            "unitPrice": {
                "currency": "EUR",
                "netAmount": float(item["disp_unit_price"]),
                "taxRatePercentage": 0,
            },
        }
        items.append(item_dict)
    items.append(
        {
            "type": "custom",
            "name": "Verpackung und Versand",
            "quantity": 1,
            "unitName": "pcs",
            "unitPrice": {
                "currency": "EUR",
                "netAmount": float(invoice_data["disp_cost"]["shipping"]),
                "taxRatePercentage": 0,
            },
        }
    )
    items.append(
        {
            "type": "custom",
            "name": "Handling Gebühr",
            "quantity": 1,
            "unitName": "pcs",
            "unitPrice": {
                "currency": "EUR",
                "netAmount": float(invoice_data["disp_cost"]["etc1"]),
                "taxRatePercentage": 0,
            },
        }
    )
    data = {
        "archived": False,
        "voucherDate": re.sub(" .*", "T00:00:00.000+01:00", "{}".format(order_date)),
        "address": {
            "name": invoice_data["shipping"]["address"]["name"]["full"],
            "street": invoice_data["shipping"]["address"]["address1"],
            "city": invoice_data["shipping"]["address"]["city"],
            "zip": invoice_data["shipping"]["address"]["postal_code"],
            "countryCode": invoice_data["shipping"]["address"]["country_code"],
            "supplement": invoice_data["buyer_email"],
        },
        "lineItems": items,
        "totalPrice": {
            "currency": "EUR",
            "totalNetAmount": invoice_data["disp_cost"]["grand_total"],
        },
        "taxConditions": {"taxType": "vatfree"},
        "paymentConditions": {
            "paymentTermLabel": paypal_label,
            "paymentTermDuration": shipping_target,
            "paymentDiscountConditions": {"discountPercentage": 0, "discountRange": 0},
        },
        "shippingConditions": {
            "shippingDate": re.sub(
                " .*", "T00:00:00.000+01:00", "{}".format(shipping_target_date)
            ),
            "shippingType": "delivery",
        },
        "title": "Rechnung",
        "introduction": "Deine bestellten Steinchen aus Bricklink Order #{} stellen wir dir hiermit in Rechnung.".format(
            invoice_data["order_id"]
        ),
        "remark": "Vielen Dank für deinen Einkauf.\nBitte bewerte uns auf store.bricklink.com/StolperStein",
    }

    return data


def create_invoice(invoice_data, ordered_items):
    data = fill_data(invoice_data, ordered_items)
    # r = requests.post('{}/invoices?finalize=true'.format(base_url), data=json.dumps(data), headers=headers)
    r = requests.post(
        "{}/invoices".format(base_url), data=json.dumps(data), headers=headers
    )
    if r.json():
        return "https://app.lexoffice.de/vouchers#!/VoucherView/Invoice/{}".format(
            r.json()["id"]
        )
    else:
        return None
