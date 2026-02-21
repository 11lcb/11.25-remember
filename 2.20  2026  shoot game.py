import random
import tkinter as tk
import time
import os

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW",root.destroy)
root.title("game")
main_frame = tk.Frame(root)
main_frame.pack()

control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

close_button = tk.Button(control_frame, text="不玩了", command=lambda:os._exit(0), 
                         bg="black", fg="white", width=10)
close_button.pack(side=tk.RIGHT, padx=5, pady=2)

#score_label = tk.Label(control_frame, text=f"请输入文本", font=("Arial", 12))
#core_label.pack(side=tk.LEFT, padx=5)

a = tk.Canvas(main_frame, width=600, height=400, bg='black')
a.pack()

B = a.create_rectangle(280, 350, 320, 370, fill='green')
e = []          # e = 敌人列表
b = []          # b = 子弹列表
z = []          # z = 增益1
score = 0
high_score = 0
                #canvas.move(对象ID,dx,dy)

#增益时间控制
zengyi_1 = False
zengyi_1_time_left = 0
zengyi_1_text = None
frame_count = 0
zengyi_1_text = a.create_text(300 ,20 ,text="", font=("Arial", 12),fill="yellow")

def time_1(seconds_left): 
    if seconds_left > 0 :    
        a.itemconfig(zengyi_1_text,text = f"强化子弹：{seconds_left}秒")
    else:
        a.itemconfig(zengyi_1_text,text =" ") 
           
def over():
    global zengyi_1
    zengyi_1 = False

#重新开始
def restart():
    popup.destroy()
    global e,b,z,score,speed,B,pause_bg,pause_text,Score,High_score,zengyi_1_text
    e = []  
    b = []   
    z = [] 
    speed = 0.5
    score = 0
    a.delete("all") 
    B = a.create_rectangle(280, 350, 320, 370, fill='green')
    pause_bg = a.create_rectangle(210,110,410,210,fill='pink',stipple ='gray50',outline='') 
    pause_text = a.create_text(310 ,160,text = "按P开始游戏",fill = "white",font = ("Arial",20))
    Score = a.create_text(500 ,20 ,text="", font=("Arial", 12),fill="yellow")
    High_score = a.create_text(150 ,20 ,text="", font=("Arial", 12),fill="red")
    zengyi_1_text = a.create_text(300 ,20 ,text="", font=("Arial", 12),fill="yellow")

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
        
def move(event):       
    global zengyi_1, paused ,pause_text ,pause_bg
    if event.keysym == 'p':
        paused = not paused
        if paused:
            print("游戏暂停")
            pause_bg = a.create_rectangle(210,110,410,210,fill='pink',stipple ='gray50',outline='') 
            pause_text = a.create_text(310 ,160,text = "游戏暂停",fill = "white",font = ("Arial",20))
        else:
            print("游戏继续")
            if pause_bg:
                a.delete(pause_bg)
                pause_bg = None
            if pause_text:    
                a.delete(pause_text)
                pause_text = None
    #射击设置            
    if not paused:
        colors=[ '#FFB6C1','#87CEEB','#98FB98','#DDA0DD'
                ,'#FFD700','#F0E68C','#E6E6FA','#B0E0E6']
        #if event.keysym == 'Left' and a.coords(B)[0] > 0: a.move(B, -15, 0)
        #elif event.keysym == 'Up' and a.coords(B)[1] > 0: a.move(B,0,-15)
        #elif event.keysym == 'Right' and a.coords(B)[2] < 600: a.move(B, 15, 0)
        #elif event.keysym == 'Down' and a.coords(B)[3] <400 : a.move(B,0,15)
        if event.keysym == 'space':
            b.append(a.create_rectangle
                    (a.coords(B)[0]+17, a.coords(B)[1], 
                    a.coords(B)[0]+23, a.coords(B)[1]-10, fill='white'))
            if zengyi_1 :
                cor = random.choice(colors)
                b.append(a.create_rectangle
                    (a.coords(B)[0]+5, a.coords(B)[1], 
                    a.coords(B)[0]+11, a.coords(B)[1]-10, fill=cor))
                b.append(a.create_rectangle
                    (a.coords(B)[0]+29, a.coords(B)[1], 
                    a.coords(B)[0]+35, a.coords(B)[1]-10, fill=cor))  
    else:
        pass                                                  
                
root.bind('<Key>', move)
pause_bg = None
pause_text = None

Score = a.create_text(500 ,20 ,text="", font=("Arial", 12),fill="yellow")
High_score = a.create_text(150 ,20 ,text="", font=("Arial", 12),fill="red")

#主循环
while True:    
    if not paused: 
        e2 = e[:]
        n = b[:]
        Z = z[:]

    #主循环控制移动
        speed_user = 5
        if left_1 and a.coords(B)[0] >0: a.move(B, -speed_user, 0)
        if up_1 and a.coords(B)[1] > 0: a.move(B,0,-speed_user)
        if right_1 and a.coords(B)[2] < 600: a.move(B, speed_user, 0)
        if down_1 and a.coords(B)[3] <400 : a.move(B,0,speed_user)
    #敌人
        if random.random() < 0.02:                        
            el = random.randint(0,570)
            er = random.randint(30,600) 
            if er-el>10 :
                e.append(a.create_rectangle(el, 0, er, 30, fill='red'))

    #敌人移动，碰撞，结束, 结束菜单 
        speed = 0.5 + score*0.05     
        for enemy in e:
            a.move(enemy, 0, speed)    
            if a.coords(enemy)[3] > 400:
                a.delete(enemy); e.remove(enemy)
                print("game over")
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
        if random.random() < 0.001:                      
            zengyi1 = random.randint(1,570)
            z.append(a.create_rectangle(zengyi1, 0, zengyi1+20, 30, fill='blue')) 

        for z1 in Z:
            a.move(z1, 0, 0.9)
            if a.coords(z1)[1] > 400:
                a.delete(z1); z.remove(z1)

        frame_count += 1
        if frame_count >= 50:
            frame_count = 0
            if zengyi_1_time_left > 0 :
                zengyi_1_time_left -= 1
                time_1(zengyi_1_time_left)
                if zengyi_1_time_left <= 0 :
                    zengyi_1 = False

        for z11 in Z:        
            try:    
                if (a.coords(z11)[0] < a.coords(B)[2] and
                    a.coords(z11)[2] > a.coords(B)[0] and
                    a.coords(z11)[1] < a.coords(B)[3] and
                    a.coords(z11)[3] > a.coords(B)[1] ):
                    if z1 in z:
                        a.delete(z11); z.remove(z11)
                        print ("获得增益: 10秒强化子弹")
                        zengyi_1 = True
                        zengyi_1_time_left = 10             
            except:
                continue 
    #增益 2 移速增加
        if random.random() < 0.0007:                      
            zengyi2 = random.randint(1,570)
            z.append(a.create_rectangle(zengyi2, 0, zengyi2+20, 30, fill='purple')) 

        for z1 in Z:
            a.move(z1, 0, 0.9)
            if a.coords(z1)[1] > 400:
                a.delete(z1); z.remove(z1)

        frame_count += 1
        if frame_count >= 50:
            frame_count = 0
            if zengyi_1_time_left > 0 :
                zengyi_1_time_left -= 1
                time_1(zengyi_1_time_left)
                if zengyi_1_time_left <= 0 :
                    zengyi_1 = False

        for z11 in Z:        
            try:    
                if (a.coords(z11)[0] < a.coords(B)[2] and
                    a.coords(z11)[2] > a.coords(B)[0] and
                    a.coords(z11)[1] < a.coords(B)[3] and
                    a.coords(z11)[3] > a.coords(B)[1] ):
                    if z1 in z:
                        a.delete(z11); z.remove(z11)
                        print ("获得增益: 10秒强化移速")
                        speed_user = 9
                        zengyi_1 = True
                        zengyi_1_time_left = 10             
            except:
                continue            

    #子弹射敌效果
        for zidan in n:
            for enemy2 in e2:
                try:
                    if (a.coords(zidan)[0] < a.coords(enemy2)[2] and 
                        a.coords(zidan)[2] > a.coords(enemy2)[0] and
                        a.coords(zidan)[1] < a.coords(enemy2)[3] and
                        a.coords(zidan)[3] > a.coords(enemy2)[1]):
                        if enemy2 in e:
                            a.delete(enemy2); e.remove(enemy2)
                        if zidan in b:    
                            a.delete(zidan); b.remove(zidan)
                        score += 1
                        a.itemconfig(Score,text=f'分数： {score}')
                        a.itemconfig(High_score,text=f'最高分数： {high_score}')
                except:
                    continue
    else:                        
        pass

    root.update()
    time.sleep(0.01)
        
