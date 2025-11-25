import random
import time
import sys
red='\u001b[41m'
white='\u001b[47m'
blue='\u001b[44m'
a='\u001b[0m'

items = [
    ("吸入器","i", 1 , 5 ),("步枪","r", 3 , 25 ),("手枪","p", 2 , 15 ),
    ("弹药","a", 2 , 15 ),("急救箱","m", 2 , 20 ),("刀","k", 1 , 15 ),
    ("斧头","x", 3 , 20 ),("护身符","t", 1 , 25 ),("烧瓶","f", 1 , 15 ),
    ("解药","d", 1 , 10 ),("食物","s", 2 , 20 ),("弓弩","c", 2 , 20 )
]

specious = ['被感染','哮喘','无事发生']


def method():
    package = 8
    used_space = 0
    total_points = 15
    final_item = []
    final_item_name = []
    table = []

    new_items = sorted(items, key=lambda x: x[3]/x[2], reverse=True)
    print(new_items)
    #按照key要求的顺序进行排列   
    # sorted(可迭代对象，key = 排序依据，reverse = 是否反转)
    condition = '无事发生'

    if condition == '无事发生' :
        print(f'\n{blue}{"无事发生"}{a}')
        #loading_multiple(2)
        print()
        for item in new_items:
            name,number,size,points = item
            if used_space + size <= package:
                final_item.append(item)
                used_space += size
                total_points += points
                final_item_name.append(item[0])

        for item_x in final_item:
            new_items.remove(item_x)
            
        for no_items in new_items:
            name_2,number_2,size_2,points_2 = no_items
            total_points -= points_2        
            
        print(f'{blue}{final_item_name}{a}\n')
        
        print(total_points)
method()        