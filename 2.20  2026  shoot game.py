import random
import tkinter as tk
import time

root = tk.Tk()
root.title("game")
main_frame = tk.Frame(root)
main_frame.pack()

control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

close_button = tk.Button(control_frame, text="不玩了", command=root.destroy, 
                         bg="black", fg="white", width=10)
close_button.pack(side=tk.RIGHT, padx=5, pady=2)

score_label = tk.Label(control_frame, text=f"请输入文本", font=("Arial", 12))
score_label.pack(side=tk.LEFT, padx=5)

a = tk.Canvas(main_frame, width=600, height=400, bg='black')
a.pack()
B = a.create_rectangle(280, 350, 320, 370, fill='green')
e = []          # e = 敌人列表
b = []          # b = 子弹列表
z = []          # z = 增益1
score = 0
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

#操作控制

def move(event):
    global zengyi_1
    if event.keysym == 'Left' and a.coords(B)[0] > 0: a.move(B, -15, 0)
    elif event.keysym == 'Up' and a.coords(B)[1] > 0: a.move(B,0,-15)
    elif event.keysym == 'Right' and a.coords(B)[2] < 600: a.move(B, 15, 0)
    elif event.keysym == 'Down' and a.coords(B)[3] <400 : a.move(B,0,15)
    elif event.keysym == 'space':
        b.append(a.create_rectangle
                (a.coords(B)[0]+17, a.coords(B)[1], 
                 a.coords(B)[0]+23, a.coords(B)[1]-10, fill='white'))
        if zengyi_1 :
            b.append(a.create_rectangle
                (a.coords(B)[0]+5, a.coords(B)[1], 
                 a.coords(B)[0]+11, a.coords(B)[1]-10, fill='white'))
            b.append(a.create_rectangle
                (a.coords(B)[0]+29, a.coords(B)[1], 
                 a.coords(B)[0]+35, a.coords(B)[1]-10, fill='white'))



while True:
    e2 = e[:]
    n = b[:]
    Z = z[:]

#敌人
    root.bind('<Key>', move)
    if random.random() < 0.02:                        
        el = random.randint(0,570)
        er = random.randint(30,600) 
        if er-el>10 :
            e.append(a.create_rectangle(el, 0, er, 30, fill='red'))

#敌人碰撞结束        
    for enemy in e:
        a.move(enemy, 0, 0.5)
        if a.coords(enemy)[3] > 400:
            a.delete(enemy); e.remove(enemy)
            print("game over")
            popup = tk.Toplevel(root)
            popup_width = 400
            popup_height = 200
            p1 = (root.winfo_screenwidth()-popup_width)//2-50
            p2 = (root.winfo_screenheight()-popup_height)//2-100
            popup.geometry(f'{popup_width}x{popup_height}+{p1}+{p2}')
            label = tk.Label(popup,text="你个菜福！",bg="red",
                     fg='black',font=("Arial",50,"bold"))
            label.place(relx=0.075,rely=0.25)

            button = tk.Button(popup,text="关闭",command = root.destroy,width= 15,bg="white"
                ,fg="black",font=("Arial",10))   
            button.place(relx=0.59, rely=0.7)
            root.after(3000,root.destroy)
            break
#子弹射击        
    for i in b:  
        a.move(i, 0, -5)
        if a.coords(i)[1] < 0:
            a.delete(i); b.remove(i)

#增益1
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
                    print("Score:", score)
            except:
                continue  

    root.update()
    time.sleep(0.01)
