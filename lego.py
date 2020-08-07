# Some clever Text
from pprint import pprint as pp
import json
import misc
import importers
import item_classes
import container
import template
# import item


# importers.ImportMap().all()
# importers.ImportCatalog().all()

test_template = {
    'containertype': "box",
    'containerdimx': 12,
    'containerdimy': 13,
    'containerdimz': 4,
    'containeremptyweight': 30,
    'templatename': "box1"
}

test_container2 = {
    "containerparent": None,
    "containername": "con1",
    "containerid": "QR7G",
    "containeryearadded": 2020,
    "containerconstraints": None,
}


# template_id = template.Template().new(test_template)
# container_id = container.Container().from_template(template_id, test_container2)
# print(container_id)

for item in item_classes.Itemidentifier.find():
    print(item.__dict__)
