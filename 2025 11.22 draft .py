import random

items = [
    {"name": "步枪", "id": "r", "space": 3, "points": 25, "special": None},
    {"name": "手枪", "id": "p", "space": 2, "points": 15, "special": None},
    {"name": "弹药", "id": "a", "space": 2, "points": 15, "special": None},
    {"name": "急救箱", "id": "m", "space": 2, "points": 20, "special": None},
    {"name": "吸入器", "id": "i", "space": 1, "points": 5, "special": "哮喘"},#需要吸入器
    {"name": "刀", "id": "k", "space": 1, "points": 15, "special": None},
    {"name": "斧头", "id": "x", "space": 3, "points": 20, "special": None},
    {"name": "护身符", "id": "t", "space": 1, "points": 25, "special": None},
    {"name": "烧瓶", "id": "f", "space": 1, "points": 15, "special": None},
    {"name": "解药", "id": "d", "space": 1, "points": 10, "special": "被感染"},#需要解药
    {"name": "食物", "id": "s", "space": 2, "points": 20, "special": None},
    {"name": "弓弩", "id": "c", "space": 2, "points": 20, "special": None}
]

specious = ['被感染','哮喘','无事发生']

must = ''
 
condition = random.choice(specious)
def  all_things_id():
    all_items_id = ''
    for item in items:
        all_items_id += item["id"]

    print(all_items_id)
    thing_id = random.choice(all_items_id)
    print(thing_id)
    for i in items:
        if i["id"] == thing_id:
            print(i["name"],i["id"],i["space"],i["points"])
            print(i)


def score():
    print("ok")



