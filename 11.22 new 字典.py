import random
import poplib




items = {
   'a': {"name": "步枪", "id": "r", "space": 3, "points": 25, "special": None},
   'b': {"name": "手枪", "id": "p", "space": 2, "points": 15, "special": None},
   'c': {"name": "弹药", "id": "a", "space": 2, "points": 15, "special": None},
   'd': {"name": "急救箱", "id": "m", "space": 2, "points": 20, "special": None},
   'e': {"name": "吸入器", "id": "i", "space": 1, "points": 5, "special": "哮喘"},#需要吸入器
   'f': {"name": "刀", "id": "k", "space": 1, "points": 15, "special": None},
   'g': {"name": "斧头", "id": "x", "space": 3, "points": 20, "special": None},
   'h': {"name": "护身符", "id": "t", "space": 1, "points": 25, "special": None},
   'i': {"name": "烧瓶", "id": "f", "space": 1, "points": 15, "special": None},
   'j': {"name": "解药", "id": "d", "space": 1, "points": 10, "special": "被感染"},#需要解药
   'k': {"name": "食物", "id": "s", "space": 2, "points": 20, "special": None},
   'l': {"name": "弓弩", "id": "c", "space": 2, "points": 20, "special": None}
}

def gen_table():
    bag = 8
    total_points = 15
    pick_items = []
    without_items = []
    pick_items_points = 0
    without_items_points = 0


    for bianhao,item_1 in items.items():
        if item_1["space"] == 1 and item_1["space"] < bag:
            pick_items.append(item_1['name'])
            pick_items_points += item_1['points']
            bag -= 1
            
            print(item_1['name'])
        elif item_1["space"] > bag :
            without_items.append(item_1['name'])
            without_items_points += item_1['points']

    for bianhao_2,item_2 in items.items():
        if item_2['space'] == 2 and item_2['space'] < bag:                
            pick_items.append(item_2['name'])
            pick_items_points += item_2['points']
            bag -= 2
            print(item_2['name'])
        elif item_2["space"] > bag :
            without_items.append(item_2["name"])
            without_items_points += item_2['points']

    for bianhao_3,item_3 in items.items():
        if item_3['space'] == 3 and item_3['space'] < bag:              
            pick_items.append(item_3['name'])
            pick_items_points += item_3['points']
            bag -= 3   
            print(item_3['name'])
        elif item_3["space"] > bag :
            without_items += item_3['name']
            without_items_points += item_3['points']         

    total_points = total_points + pick_items_points - without_items_points

    #print(pick_items,pick_items_points)


    print(without_items_points)
    print(without_items)
    print(pick_items_points)  
    print(pick_items)                         
    print(total_points)
    #print(pick_items)
    #print(without_items)

gen_table()
