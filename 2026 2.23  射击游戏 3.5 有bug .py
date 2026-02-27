import random
import tkinter as tk
import time
import os
import math

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW",root.destroy)
root.title("game")
main_frame = tk.Frame(root)
main_frame.pack()
m1 = root.winfo_screenwidth()//2-450
m2 = root.winfo_screenheight()//2-410
root.geometry(f'{900}x{750}+{m1}+{m2}')

control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

close_button = tk.Button(control_frame, text="不玩了", command=lambda:os._exit(0), 
                         bg="black", fg="white", width=10)
close_button.pack(side=tk.RIGHT, padx=5, pady=2)

score_label = tk.Label(control_frame, text=f"道具： ①蓝色：子弹强化 ②紫色：移速增加 ③青色：左shift 瞬移", font=("Arial", 12))
score_label.pack(side=tk.LEFT, padx=5)

a = tk.Canvas(main_frame, width=900, height=700, bg='black')
a.pack()

#菜单
def menu():
    menu_canvas =tk.Canvas(root,width=600,height=450,bg="black")
    menu_canvas.pack()
    menu_canvas.create_text(300,100,text="shoot game",fill = "black",font=("Arial",30))
    start_button = tk.Button(menu_canvas,text ="start",command =start_game)
    start_button.place(x=250 ,y=200)
def start_game():
    pass    


B = a.create_rectangle(430, 480, 470, 500, fill='green')
a_time = 0
e = []          # e = 敌人列表
b = []          # b = 子弹列表
z = []          # z = 增益1
z2 = []         # z2 = 增益2
z3 = []         # z3 = 增益3 
score = 0
high_score = 0
speed_user = 5  #角色移动
hurt = 500

                #canvas.move(对象ID,dx,dy)

#---------------------------------------------------------------------------------------------------------------------------------------------

# 增益时间控制

            #   ① 子弹
zengyi_1_active = False
zengyi_1_time_left = 0
zengyi_1_text = None
frame_count = 0
zengyi_1_text = a.create_text(450 ,20 ,text="", font=("Arial", 12),fill="yellow")

def time_1(seconds_left): 
    if seconds_left > 0 :    
        a.itemconfig(zengyi_1_text,text = f"强化子弹：{seconds_left}秒")
    else:
        a.itemconfig(zengyi_1_text,text =" ") 

            #   ②  移速
zengyi_2_active = False
zengyi_2_time_left = 0
zengyi_2_text = None
zengyi_2_text = a.create_text(450 ,40 ,text="", font=("Arial", 12),fill="yellow")

def time_2(seconds_left): 
    global speed_user
    if seconds_left > 0 :
        speed_user = 8    
        a.itemconfig(zengyi_2_text,text = f"强化移速：{seconds_left}秒")
    else:
        speed_user =5
        a.itemconfig(zengyi_2_text,text =" ") 

            #   ③  瞬移
zengyi_3_active = False
shunyi_number = 0
zengyi_3_text = None
zengyi_3_text = a.create_text(70 ,80 ,text="", font=("Arial", 12),fill="yellow")

zengyi_3_text_2 = a.create_text(120 ,100 ,text="", font=("Arial", 12),fill="yellow")
zengyi_3_text_3 = a.create_text(80 ,120 ,text="", font=("Arial", 12),fill="yellow")

zengyi_3_time_left_1 = 0
zengyi_3_time_left_2 = 3


def shunyi():
    global shunyi_number,score,zengyi_3_time_left_1,zengyi_3_time_left_2
    if shunyi_number >0:
        if len(e) >0 :
            for e22 in reversed(e):      
                enemy_y = a.coords(e22)[3]
                enemy_x_l = a.coords(e22)[0]
                enemy_x_r = a.coords(e22)[2]
                a.coords(B,(enemy_x_r - enemy_x_l)/2 + enemy_x_l-20,
                            enemy_y + 180,(enemy_x_r - enemy_x_l)/2 + enemy_x_l+20,
                            enemy_y + 200)
        else:
            score += 5
            a.itemconfig(Score,text=f'分数： {score}')
            #print("战场无敌人,获得十分")
            zengyi_3_time_left_2 = 3
            a.itemconfig(zengyi_3_text_3,state = 'normal', text = "战场无敌人,获得5分")        
    else:
        zengyi_3_time_left_1 = 3
        a.itemconfig(zengyi_3_text_2,state = 'normal',text = f"剩余瞬移次数: {shunyi_number}次,还未获得瞬移")      

    shunyi_number -= 1
    if shunyi_number < 1: 
        shunyi_number = 0
    a.itemconfig(zengyi_3_text,text = f"剩余瞬移次数: {shunyi_number}次")
    

#---------------------------------------------------------------------------------------------------------------------------------------------

#重新开始
def restart():
    popup.destroy()
    global e,b,z,z2,z3,score,speed,B,pause_bg,pause_text,Score,High_score,zengyi_1_text,zengyi_2_text,shunyi_number,zengyi_3_text
    global zengyi_3_text_2,zengyi_3_text_3
    e = []  
    b = []   
    z = [] 
    z2 = []
    z3 = []
    speed = 0.5
    score = 0
    shunyi_number = 0
    a.delete("all") 
    B = a.create_rectangle(430, 480, 470, 500, fill='green')
    pause_bg = a.create_rectangle(350,250,550,350,fill='pink',stipple ='gray50',outline='') 
    pause_text = a.create_text(445 ,300,text = "按P开始游戏",fill = "white",font = ("Arial",20))
    Score = a.create_text(850 ,20 ,text="", font=("Arial", 12),fill="yellow")
    High_score = a.create_text(150 ,20 ,text="", font=("Arial", 12),fill="red")
    zengyi_1_text = a.create_text(450 ,20 ,text="", font=("Arial", 12),fill="yellow")
    zengyi_2_text = a.create_text(450 ,40 ,text="", font=("Arial", 12),fill="yellow")
    zengyi_3_text = a.create_text(70 ,80 ,text="", font=("Arial", 12),fill="yellow")
    zengyi_3_text_2 = a.create_text(120 ,100 ,text="", font=("Arial", 12),fill="yellow")
    zengyi_3_text_3 = a.create_text(80 ,120 ,text="", font=("Arial", 12),fill="yellow")

#
paused = False

#操作控制
left_1 = False
up_1 = False 
right_1 = False
down_1 = False
root.bind("<KeyPress-Left>",lambda e:globals().update(left_1 = True))
root.bind("<KeyRelease-Left>",lambda e:globals().update(left_1 = False))
root.bind("<KeyPress-Right>",lambda e:globals().update(right_1 = True))
root.bind("<KeyRelease-Right>",lambda e:globals().update(right_1 = False))
root.bind("<KeyPress-Up>",lambda e:globals().update(up_1 = True))
root.bind("<KeyRelease-Up>",lambda e:globals().update(up_1 = False))
root.bind("<KeyPress-Down>",lambda e:globals().update(down_1 = True))
root.bind("<KeyRelease-Down>",lambda e:globals().update(down_1 = False))

#暂停设置
def key_press():
    global paused,pause_text ,pause_bg,pause_text_1,pause_bg_1,pause_text_2,pause_bg_2
    paused = not paused
    if paused:
        #print("游戏暂停")
        pause_bg = a.create_rectangle(350,250,550,350,fill='pink',stipple ='gray50',outline='') 
        pause_text = a.create_text(445 ,300,text = "游戏暂停",fill = "white",font = ("Arial",20))
    else:
        #print("游戏继续")
        if pause_bg:
            a.delete(pause_bg)
            pause_bg = None
        if pause_text:    
            a.delete(pause_text)
            pause_text = None
        if pause_bg_1:
            a.delete(pause_bg_1)
            pause_bg_1 = None
        if pause_text_1:    
            a.delete(pause_text_1)
            pause_text_1 = None
        if pause_bg_2:
            a.delete(pause_bg_2)
            pause_bg_2 = None
        if pause_text_2:    
            a.delete(pause_text_2)
            pause_text_2 = None    
#射击设置 
def shoot():
    colors=[ '#FFB6C1','#87CEEB','#98FB98','#DDA0DD'
            ,'#FFD700','#F0E68C','#E6E6FA',"#8FDCE6"]
    b.append(a.create_rectangle(a.coords(B)[0]+17, a.coords(B)[1], 
                    a.coords(B)[0]+23, a.coords(B)[1]-10, fill='white'))
    if zengyi_1_active :
        cor = random.choice(colors)
        b.append(a.create_rectangle(a.coords(B)[0]+5, a.coords(B)[1], 
            a.coords(B)[0]+11, a.coords(B)[1]-10, fill=cor))
        b.append(a.create_rectangle(a.coords(B)[0]+29, a.coords(B)[1], 
            a.coords(B)[0]+35, a.coords(B)[1]-10, fill=cor))            

def move(event):       
    global zengyi_1, paused ,pause_text ,pause_bg
    if event.keysym == 'p':
        key_press()          
    if not paused:
        #if event.keysym == 'Left' and a.coords(B)[0] > 0: a.move(B, -15, 0)
        #elif event.keysym == 'Up' and a.coords(B)[1] > 0: a.move(B,0,-15)
        #elif event.keysym == 'Right' and a.coords(B)[2] < 600: a.move(B, 15, 0)
        #elif event.keysym == 'Down' and a.coords(B)[3] <400 : a.move(B,0,15)
        if event.keysym == 'space':
            shoot()  
        if event.keysym == "Shift_L":
            shunyi()        
    else:
        pass                                                  
                
root.bind('<Key>', move)
#root.bind('<Key-Shift_L>',shunyi)
pause_bg = None
pause_text = None

Score = a.create_text(800 ,20 ,text="", font=("Arial", 12),fill="yellow")
High_score = a.create_text(150 ,20 ,text="", font=("Arial", 12),fill="red")

paused = True
pause_bg_1 = a.create_rectangle(25,70,165,110,fill='pink',stipple ='gray50',outline='') 
pause_text_1 = a.create_text(100 ,90,text = "游戏规则：",fill = "white",font = ("Arial",20))

pause_bg = a.create_rectangle(190,100,430,220,fill='pink',stipple ='gray50',outline='') 
pause_text = a.create_text(310 ,160,text =f" 1.↑↓←→ 控制移动 \n 2.‘P’暂停,开始 \n 3.空格射击"
                            ,fill = "white",font = ("Arial",20))

pause_bg_2 = a.create_rectangle(50,270,700,430,fill='pink',stipple ='gray50',outline='')
pause_text_2 = a.create_text(375 ,350,text =f" 1. 蓝色：强化子弹，持续15秒\n" 
                    " 2. 紫色：增强移速，持续十秒 \n "
                    "3. 青色：拾取后左shift，瞬移到最下方敌人的下面\n     如果地图中无敌人，消耗一次传送增加5分"
                            ,fill = "white",font = ("Arial",20))
key_press

#主循环
while True:    
    if not paused: 
        e2 = e[:]
        n = b[:]
        Z1 = z[:]
        Z2 = z2[:]
        Z3 = z3[:]

    #主循环控制移动
        if left_1 and a.coords(B)[0] >0: a.move(B, -speed_user, 0)
        if up_1 and a.coords(B)[1] > 0: a.move(B,0,-speed_user)
        if right_1 and a.coords(B)[2] < 900: a.move(B, speed_user, 0)
        if down_1 and a.coords(B)[3] <700 : a.move(B,0,speed_user)
    #敌人
        if random.random() < 0.005:                        
            up = random.randint(3,40)
            e_size = up                     
            e.append([a.create_rectangle(e_size*10, 0, 15*e_size , 30, fill='red'),up])
               
    #敌人移动，碰撞，结束, 结束菜单 
        speed = 0.5 + score*0.04     
        for enemy in e:
            a.move(enemy[0], 0, speed)    
            if a.coords(enemy[0])[3] > 700:
                a.delete(enemy[0]); e.remove(enemy)
                #print("game over")
                if score > high_score : high_score = score
                paused = True
                popup = tk.Toplevel(root)
                popup_width = 400
                popup_height = 300
                p1 = (root.winfo_screenwidth()-popup_width)//2-50
                p2 = (root.winfo_screenheight()-popup_height)//2-100
                popup.geometry(f'{popup_width}x{popup_height}+{p1}+{p2}')
                label = tk.Label(popup,text="可惜，你还得练！",bg="pink",
                        fg='black',font=("Arial",30,"bold"))
                label.place(relx=0.075,rely=0.35)

                label_1 = tk.Label(popup,text=f"你的得分是： {score}",bg="pink",
                        fg='black',font=("Arial",25,"bold"))
                label_1.place(relx=0.075,rely=0.15)

                label_1 = tk.Label(popup,text=f"最高分： {high_score}",bg="pink",
                        fg='black',font=("Arial",15,"bold"))
                label_1.place(relx=0.075,rely=0.06)

                button = tk.Button(popup,text="关闭",command=lambda:os._exit(0),width= 15,bg="pink"
                    ,fg="black",font=("Arial",10))   
                button.place(relx=0.59, rely=0.7)
                
                button = tk.Button(popup,text="再来一次",command=restart ,width= 15,bg="pink"
                    ,fg="black",font=("Arial",10))   
                button.place(relx=0.19, rely=0.7)
                break
    #子弹射击        
        for i in b:  
            a.move(i, 0, -5)
            if a.coords(i)[1] < 0:
                a.delete(i); b.remove(i)


    #增益 1 三发子弹
        if random.random() < 0.003:                      
            zengyi1 = random.randint(1,870)
            z.append(a.create_rectangle(zengyi1, 0, zengyi1+20, 30, fill='blue')) 

        for z1 in Z1:
            a.move(z1, 0, 0.9)
            if a.coords(z1)[1] > 700:
                a.delete(z1); z.remove(z1)

        frame_count += 0.7                               #  增益时间
        if frame_count >= 50:
            frame_count = 0
            if zengyi_1_time_left > 0 :
                zengyi_1_time_left -= 1
                time_1(zengyi_1_time_left)
                if zengyi_1_time_left <= 0 :
                    zengyi_1_active = False
            if zengyi_2_time_left > 0 :
                zengyi_2_time_left -= 1
                time_2(zengyi_2_time_left)
                if zengyi_2_time_left <= 0 :
                    zengyi_2_active = False 
            if zengyi_3_time_left_1 > 0 :
                zengyi_3_time_left_1 -= 1
                if zengyi_3_time_left_1 <= 0 :
                    a.itemconfig(zengyi_3_text_2,state = 'hidden',text = f"剩余瞬移次数: {shunyi_number}次,还未获得瞬移")
            if zengyi_3_time_left_2 > 0 :
                zengyi_3_time_left_2 -= 1
                if zengyi_3_time_left_2 <= 0 :     
                    a.itemconfig(zengyi_3_text_3,state = 'hidden', text = "战场无敌人,获得5分")
        for z11 in Z1:        
            try:    
                if (a.coords(z11)[0] < a.coords(B)[2] and
                    a.coords(z11)[2] > a.coords(B)[0] and
                    a.coords(z11)[1] < a.coords(B)[3] and
                    a.coords(z11)[3] > a.coords(B)[1] ):
                    if z1 in z:
                        a.delete(z11); z.remove(z11)
                        #print ("获得增益: 15秒强化子弹")
                        zengyi_1_active = True
                        zengyi_1_time_left = 15            
            except:
                continue 
    #增益 2 移速增加
        if random.random() < 0.0015:                             #  增益生成
            zengyi_2_x= random.randint(1,870)
            zengyi_2_math = random.randint(0,360)
            z2.append(a.create_oval(zengyi_2_x, +0, zengyi_2_x+20,+30, fill="#9A45C1"))
 

        for z22 in Z2:                                          #  增益移动
            zengyi_2_move = 0 + 3*math.sin(zengyi_2_math)
            a.move(z22, zengyi_2_move, 2)
            if a.coords(z22)[1] > 700:
                a.delete(z22); z2.remove(z22)

        for z222 in Z2:                                          #  增益获得方法
            try:    
                if (a.coords(z222)[0] < a.coords(B)[2] and
                    a.coords(z222)[2] > a.coords(B)[0] and
                    a.coords(z222)[1] < a.coords(B)[3] and
                    a.coords(z222)[3] > a.coords(B)[1] ):
                    if z22 in z2:
                        a.delete(z222); z2.remove(z222)
                        #print ("获得增益: 10秒强化移动速度")
                        zengyi_2_active = True
                        zengyi_2_time_left = 10             
            except:
                continue 

    # 增益 3 瞬移
        if random.random() < 0.001+score*0.00008:                             
            zengyi_3= random.randint(1,870)
            z3.append(a.create_oval(zengyi_3, 0, zengyi_3+20, 25, fill='#2B9BA9'))        

        for z33 in Z3:                                     
            a.move(z33, 0, 0.9)
            if a.coords(z33)[1] > 900:
                a.delete(z33); z3.remove(z33)

        for z333 in Z3: 
            try:    
                if (a.coords(z333)[0] < a.coords(B)[2] and
                    a.coords(z333)[2] > a.coords(B)[0] and
                    a.coords(z333)[1] < a.coords(B)[3] and
                    a.coords(z333)[3] > a.coords(B)[1] ):
                    if z33 in z3:
                        a.delete(z333); z3.remove(z333)
                        #print ("获得增益: 瞬移")
                        shunyi_number += 1
                        a.itemconfig(zengyi_3_text,text = f"剩余瞬移次数: {shunyi_number}次")
                                
            except:
                continue 

    #子弹射敌效果
        remove_enemy = []
        for zidan in n:
            for enemy2 in e2:
                weizhi = enemy[0]  # 敌人的矩形ID
                try:                                  # 碰撞检测
                    if (a.coords(zidan)[0] < a.coords(weizhi)[2] and
                        a.coords(zidan)[2] > a.coords(weizhi)[0] and
                        a.coords(zidan)[1] < a.coords(weizhi)[3] and
                        a.coords(zidan)[3] > a.coords(weizhi)[1]):
                        a.delete(zidan)
                        if zidan in b:    
                            b.remove(zidan)
                            enemy2[1] -= hurt
                            if enemy2[1] <= 0:
                                print(enemy2[1])
                                a.delete(enemy2[0])
                                remove_enemy.append(enemy2)    

                        break    
                except:
                    continue
        for em in remove_enemy:
            if em in e:
                e.remove(em)
                score += 1
                a.itemconfig(Score,text=f'分数： {score}')
                a.itemconfig(High_score,text=f'最高分数： {high_score}') 
        remove_enemy.clear()                           

    else:                        
        pass

    root.update()
    time.sleep(0.008)
        
