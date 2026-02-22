import random


bag = 8

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


def gen_table():
    pick_items = []
    without_items = []
    A = []
    for bianhao in items:
        a=items["i"]
        A.append(a)
        print(bianhao,A)

    print(pick_items)
    print(without_items)

def score():             #选择特殊情况,计算最大分数
    must_item = [] 

    all_items_id = ''           #通过id 寻找物品信息
    for item in items:
        all_items_id += item["id"]

    condition = random.choice(specious)

    if condition == '被感染' :
        print("被感染！")
        print("需要解毒剂")
        bag = 7
        for i in items:
            if i["id"] == "d" :
                #print(i["name"],i["id"],i["space"],i["points"])       
                must_item.append(i)
        #print(must_item)
        gen_table()

    elif condition == '哮喘' :
        print("哮喘！")
        print("需要吸入器")
        bag = 7
        for i in items:
            if i["id"] == "i" :
                #print(i["name"],i["id"],i["space"],i["points"])       
                must_item.append(i)
        #print(must_item)
        gen_table()

    elif condition == '无事发生' :
        print("无事发生...")
        bag = 8
        gen_table()
score()







