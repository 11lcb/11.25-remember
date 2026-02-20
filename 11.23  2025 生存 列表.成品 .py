import random
import time
import sys
import tkinter as tk
from tkinter import simpledialog,messagebox

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
    m = input("勇士要带多大的背包？\n  背包格数： ")
    package = int(m)
    used_space = 0
    total_points = 15
    final_item = []
    final_item_name = []
    table = []

    new_items = sorted(items, key=lambda x: x[3]/x[2], reverse=True)
    #按照key要求的顺序进行排列   
    # sorted(可迭代对象，key = 排序依据，reverse = 是否反转)
    condition = random.choice(specious)

    if condition == '被感染' :
        print(f'\n{red}{"特殊情况： "}{a}')
        print(f'{red}{"被感染！！"}{a}') 
        loading_multiple(2)
        print()
        items.remove(("解药","d", 1 , 10 ) )
        package = package -1
        for item in new_items:
            name,number,size,points = item
            if used_space + size <= package:
                used_space += size
                total_points += points
                final_item.append(item)
                final_item_name.append(item[0])

        for item_x in final_item:
            new_items.remove(item_x)
            
        for no_items in new_items:
            name_2,number_2,size_2,points_2 = no_items
            total_points -= points_2

        final_item.append(("解药","d", 1 , 10 ))  
        final_item_name.append("解药")
        total_points += 10
        print(f'{blue}{final_item_name}{a}\n')

    elif condition == '哮喘' :
        print(f'\n{red}{"特殊情况： "}{a}')
        print(f'{red}{"哮喘！！"}{a}')
        loading_multiple(2)
        print()
        items.remove(("吸入器","i", 1, 5))
        package = package -1
        for item in new_items:
            name,number,size,points = item
            if used_space + size <= package:
                used_space += size
                total_points += points
                final_item.append(item) 
                final_item_name.append(item[0])
        for item_x in final_item:
            new_items.remove(item_x)
            
        for no_items in new_items:
            name_2,number_2,size_2,points_2 = no_items
            total_points -= points_2         

        final_item.append(("吸入器","i", 1 , 5 ))
        final_item_name.append("吸入器")
        total_points += 5
        print(f'{blue}{final_item_name}{a}\n')

    elif condition == '无事发生' :
        print(f'\n{blue}{"无事发生"}{a}')
        loading_multiple(2)
        print()
        for item in new_items:
            name,number,size,points = item
            if used_space + size <= package:
                final_item.append(item)
                used_space += size
                total_points += points
                final_item_name.append(item[0])
        print(f'{blue}{final_item_name}{a}\n')

        for item_x in final_item:
            new_items.remove(item_x)
            
        for no_items in new_items:
            name_2,number_2,size_2,points_2 = no_items
            total_points -= points_2     

    for item in final_item:
        for i in range(int(item[2])):
            table.append(f"[{item[1]}]")
    print(f'{white}{table[:4]}{a}')
    print(f'{white}{table[4:]}{a}\n')    

    print(f"{blue}总分数: {total_points}{a}\n")


    if total_points < 0 :
        print(f"{red}你毫无生还可能.....{a}")
    elif total_points == 0:
        print(f"{red} 你活下来了，只是非常艰难...{a}") 
    elif total_points > 0 :
        print(f"{blue}你成功存活！！{a}")      
    print(f"{blue}THE END{a}")

def publish():
    popup_1= tk.Toplevel()
    popup_1.geometry('300x300')
    print("ok")

def loading_multiple(m):
    bar = 30
    for p in range(m):
        for i in range(1, bar + 1):
            time.sleep(0.05)  
            percent = i * 100 // bar
            b=" "
            L = b * i + "0" * (bar - i)
            sys.stdout.write(f'\rTask {p+1}/{m} [{L}] {percent:3d}%')
            sys.stdout.flush()

        sys.stdout.write('\r' + ' ' * (50 + bar) + '\r')
        sys.stdout.flush()

root = tk.Tk()
root.title("publish")
root.geometry('300x300')

photo= tk.PhotoImage(file='gradient.png')
label_bg = tk.Label(root, image=photo)
label_bg.place(x=0, y=0, relwidth=1, relheight=1)

root_label = tk.Label(root,text = 'type the text ', bg='pink',font=("Arial",
                                                            16,"bold"))
root_label.place(relx = 0.04, rely = 0.15)

letter_entry = tk.Entry(root, width=5, font=('Verdana', 16))
letter_entry.insert(0, 'a')

root_button = tk.Button(root,text='button_1',command = publish ,bg='pink',
                                                        font=("Arial",14,"bold"))
root_button.place(relx = 0.35, rely = 0.4)

root_button = tk.Button(root,text='关闭',command = root.destroy,bg='pink',font=("Arial",
                                                                11,"bold"))
root_button.place(relx = 0.7, rely = 0.8)

root.mainloop()
print(f"{red}正在生成末日环境{a}")
loading_multiple(3)
method()