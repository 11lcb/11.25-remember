import random
import tkinter as tk
import time
import os
import math

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", root.destroy)
root.title("game")
main_frame = tk.Frame(root)
main_frame.pack()
m1 = root.winfo_screenwidth()//2 - 450
m2 = root.winfo_screenheight()//2 - 410
root.geometry(f'{900}x{750}+{m1}+{m2}')

control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

close_button = tk.Button(control_frame, text="不玩了", command=lambda: os._exit(0), 
                         bg="black", fg="white", width=10)
close_button.pack(side=tk.RIGHT, padx=5, pady=2)

score_label = tk.Label(control_frame, text=f"道具： ①蓝色：子弹强化 ②紫色：移速增加 ③青色：左shift 瞬移", font=("Arial", 12))
score_label.pack(side=tk.LEFT, padx=5)

a = tk.Canvas(main_frame, width=900, height=700, bg='black')
a.pack()

B = a.create_rectangle(430, 480, 470, 500, fill='green')
a_time = 0
e = []          # 敌人列表：[容器ID, 血条背景ID, 血条进度ID, 最大血量, 当前血量, 宽度, 高度]
b = []          # 子弹列表
z = []          # 增益1
z2 = []         # 增益2
z3 = []         # 增益3 
score = 0
high_score = 0
speed_user = 5  # 角色移动速度
hurt = 5        # 子弹伤害

# 菜单
def menu():
    menu_canvas = tk.Canvas(root, width=600, height=450, bg="black")
    menu_canvas.pack()
    menu_canvas.create_text(300, 100, text="shoot game", fill="white", font=("Arial", 30))
    start_button = tk.Button(menu_canvas, text="start", command=start_game)
    start_button.place(x=250, y=200)

def start_game():
    pass

#  生成 有血条的敌人
def create_enemy(x, y, width, height, max_hp):
    #  透明容器（用于整体移动）
    container = a.create_rectangle(x, y, x+width, y+height, fill='', outline='')
    #  黑色背景
    hp_bg = a.create_rectangle(x, y, x+width, y+height, fill='black', outline='red')
    #  红色血条，血量
    hp_bar = a.create_rectangle(x, y, x+width, y+height, fill='red', outline='')
    return [container, hp_bg, hp_bar, max_hp, max_hp, width, height]    # 返回完整结构

#  更新血条
def update_enemy_hp(enemy):
    try:
        enemy = container, hp_bg, hp_bar, max_hp, current_hp, width, height 
        x1, y1, _, y2 = a.coords(container)                   # 获取容器位置
        hp_bili = max(0, current_hp / max_hp)                # 血量比例（避免负数）
        new_hp_width = width * hp_bili                        # 剩余血条宽度
        a.coords(hp_bar, x1, y1, x1 + new_hp_width, y2)       # 缩短红色血条
    except:
        pass

# 重新开始
def restart():
    popup.destroy()
    global e, b, z, z2, z3, score, speed_user, B, pause_bg, pause_text, Score, High_score
    global zengyi_1_text, zengyi_2_text, shunyi_number, zengyi_3_text, zengyi_3_text_2, zengyi_3_text_3
    global zengyi_1_active, zengyi_1_time_left, zengyi_2_active, zengyi_2_time_left
    e = []  
    b = []   
    z = [] 
    z2 = []
    z3 = []
    score = 0
    shunyi_number = 0
    speed_user = 5
    zengyi_1_active = False
    zengyi_1_time_left = 0
    zengyi_2_active = False
    zengyi_2_time_left = 0
    
    a.delete("all") 
    B = a.create_rectangle(430, 480, 470, 500, fill='green')
    pause_bg = a.create_rectangle(350, 250, 550, 350, fill='pink', stipple='gray50', outline='') 
    pause_text = a.create_text(445, 300, text="按P开始游戏", fill="white", font=("Arial", 20))
    Score = a.create_text(850, 20, text="", font=("Arial", 12), fill="yellow")
    High_score = a.create_text(150, 20, text="", font=("Arial", 12), fill="red")
    zengyi_1_text = a.create_text(450, 20, text="", font=("Arial", 12), fill="yellow")
    zengyi_2_text = a.create_text(450, 40, text="", font=("Arial", 12), fill="yellow")
    zengyi_3_text = a.create_text(70, 80, text="", font=("Arial", 12), fill="yellow")
    zengyi_3_text_2 = a.create_text(120, 100, text="", font=("Arial", 12), fill="yellow")
    zengyi_3_text_3 = a.create_text(80, 120, text="", font=("Arial", 12), fill="yellow")

# 暂停设置
paused = False
left_1 = False
up_1 = False 
right_1 = False
down_1 = False

# 方向键
root.bind("<KeyPress-Left>", lambda e: globals().update(left_1=True))
root.bind("<KeyRelease-Left>", lambda e: globals().update(left_1=False))
root.bind("<KeyPress-Right>", lambda e: globals().update(right_1=True))
root.bind("<KeyRelease-Right>", lambda e: globals().update(right_1=False))
root.bind("<KeyPress-Up>", lambda e: globals().update(up_1=True))
root.bind("<KeyRelease-Up>", lambda e: globals().update(up_1=False))
root.bind("<KeyPress-Down>", lambda e: globals().update(down_1=True))
root.bind("<KeyRelease-Down>", lambda e: globals().update(down_1=False))

def key_press():
    global paused, pause_text, pause_bg, pause_text_1, pause_bg_1, pause_text_2, pause_bg_2
    paused = not paused
    if paused:
        pause_bg = a.create_rectangle(350, 250, 550, 350, fill='pink', stipple='gray50', outline='') 
        pause_text = a.create_text(445, 300, text="游戏暂停", fill="white", font=("Arial", 20))
    else:
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

# 射击设置 
def shoot():
    colors = ['#FFB6C1','#87CEEB','#98FB98','#DDA0DD',
              '#FFD700','#F0E68C','#E6E6FA',"#8FDCE6"]
    # 基础子弹
    b.append(a.create_rectangle(a.coords(B)[0]+17, a.coords(B)[1], 
                    a.coords(B)[0]+23, a.coords(B)[1]-10, fill='white'))
    if zengyi_1_active :
        cor = random.choice(colors)
        b.append(a.create_rectangle(a.coords(B)[0]+5, a.coords(B)[1], 
            a.coords(B)[0]+11, a.coords(B)[1]-10, fill=cor))
        b.append(a.create_rectangle(a.coords(B)[0]+29, a.coords(B)[1], 
            a.coords(B)[0]+35, a.coords(B)[1]-10, fill=cor))
            
# 增益时间
# ① 子弹强化
zengyi_1_active = False
zengyi_1_time_left = 0
zengyi_1_text = a.create_text(450, 20, text="", font=("Arial", 12), fill="yellow")

def time_1(seconds_left): 
    if seconds_left > 0 :    
        a.itemconfig(zengyi_1_text, text=f"强化子弹：{seconds_left}秒")
    else:
        a.itemconfig(zengyi_1_text, text="") 

# ② 移速强化
zengyi_2_active = False
zengyi_2_time_left = 0
zengyi_2_text = a.create_text(450, 40, text="", font=("Arial", 12), fill="yellow")

def time_2(seconds_left): 
    global speed_user
    if seconds_left > 0 :
        speed_user = 8    
        a.itemconfig(zengyi_2_text, text=f"强化移速：{seconds_left}秒")
    else:
        speed_user = 5
        a.itemconfig(zengyi_2_text, text="") 

# ③ 瞬移
zengyi_3_active = False
shunyi_number = 0
zengyi_3_text = a.create_text(70, 80, text="", font=("Arial", 12), fill="yellow")
zengyi_3_text_2 = a.create_text(120, 100, text="", font=("Arial", 12), fill="yellow")
zengyi_3_text_3 = a.create_text(80, 120, text="", font=("Arial", 12), fill="yellow")
zengyi_3_time_left_1 = 0
zengyi_3_time_left_2 = 3

def shunyi():
    global shunyi_number, score, zengyi_3_time_left_1, zengyi_3_time_left_2
    if shunyi_number > 0:
        if len(e) > 0 :
            # 找到最下方的敌人
            lowest_enemy = max(e, key=lambda en: a.coords(en[0])[3])
            enemy_y = a.coords(lowest_enemy[0])[3]
            enemy_x_l = a.coords(lowest_enemy[0])[0]
            enemy_x_r = a.coords(lowest_enemy[0])[2]
            # 瞬移到敌人下方
            new_x = (enemy_x_r - enemy_x_l)/2 + enemy_x_l - 20
            new_y = enemy_y + 80
            new_x = max(0, min(new_x, 880))       # 确保角色不超出画布边界
            new_y = max(0, min(new_y, 680))
            a.coords(B, new_x, new_y, new_x + 40, new_y + 20)
        else:
            score += 5
            a.itemconfig(Score, text=f'分数： {score}')
            zengyi_3_time_left_2 = 3
            a.itemconfig(zengyi_3_text_3, state='normal', text="战场无敌人,获得5分")        
    else:
        zengyi_3_time_left_1 = 3
        a.itemconfig(zengyi_3_text_2, state='normal', text=f"剩余瞬移次数: {shunyi_number}次,还未获得瞬移")      

    shunyi_number -= 1
    shunyi_number = max(0, shunyi_number)  # 确保次数不为负
    a.itemconfig(zengyi_3_text, text=f"剩余瞬移次数: {shunyi_number}次")
    #if shunyi_number >0:
        #a.itemconfig(zengyi_3_text, text=f"剩余瞬移次数: {shunyi_number}次")

def move(event):       
    global paused, pause_text, pause_bg
    if event.keysym == 'p':
        key_press()          
    if not paused:
        if event.keysym == 'space':
            shoot()  
        if event.keysym == "Shift_L":
            shunyi()        
    else:
        pass                                                  

root.bind('<Key>', move)
pause_bg = None
pause_text = None
pause_bg_1 = None
pause_text_1 = None
pause_bg_2 = None
pause_text_2 = None

# 创建分数显示
Score = a.create_text(800, 20, text="", font=("Arial", 12), fill="yellow")
High_score = a.create_text(150, 20, text="", font=("Arial", 12), fill="red")

# 初始游戏说明界面
paused = True
pause_bg_1 = a.create_rectangle(25, 70, 165, 110, fill='pink', stipple='gray50', outline='') 
pause_text_1 = a.create_text(100, 90, text="游戏规则：", fill="white", font=("Arial", 20))

pause_bg = a.create_rectangle(190, 100, 430, 220, fill='pink', stipple='gray50', outline='') 
pause_text = a.create_text(310, 160, text=f" 1.↑↓←→ 控制移动 \n 2.‘P’暂停,开始 \n 3.空格射击",
                            fill="white", font=("Arial", 20))

pause_bg_2 = a.create_rectangle(50, 270, 700, 430, fill='pink', stipple='gray50', outline='')
pause_text_2 = a.create_text(375, 350, text=f" 1. 蓝色：强化子弹，持续15秒\n" 
                    " 2. 紫色：增强移速，持续十秒 \n "
                    "3. 青色：拾取后左shift，瞬移到最下方敌人的下面\n     如果地图中无敌人，消耗一次传送增加5分",
                            fill="white", font=("Arial", 20))

# 主循环
frame_count = 0
while True:    
    if not paused: 
        # 复制列表避免遍历时修改原列表导致的问题,真nm恶心的地方，早知道就用倒着遍历了，省的一直改md
        e2 = e[:]
        n = b[:]
        Z1 = z[:]
        Z2 = z2[:]
        Z3 = z3[:]

        # 角色移动控制
        if left_1 and a.coords(B)[0] > 0: 
            a.move(B, -speed_user, 0)
        if up_1 and a.coords(B)[1] > 0: 
            a.move(B, 0, -speed_user)
        if right_1 and a.coords(B)[2] < 900: 
            a.move(B, speed_user, 0)
        if down_1 and a.coords(B)[3] < 700: 
            a.move(B, 0, speed_user)

        # 生成敌人
        if random.random() < 0.005:                        
            up = random.randint(5, 40)
            e_size = up                     
            enemy_x = e_size * 10
            enemy_y = 0
            enemy_width = 5 * e_size  # 敌人宽度
            enemy_height = 10         # 敌人高度
            enemy_max_hp = up * 2     # 敌人最大血量（和尺寸挂钩，数值调低适配hurt=5）
           
            new_enemy = create_enemy(enemy_x, enemy_y, enemy_width, enemy_height, enemy_max_hp)
            e.append(new_enemy)
               
        # 敌人移动（移动容器   he  血条）
        speed = 0.5 + score * 0.04     
        game_over = False
        for enemy in e2:
            try:
                container, hp_bg, hp_bar, max_hp, current_hp, width, height = enemy
                # 移动容器 + 血条背景 + 血条进度（同步移动 ！！！
                a.move(container, 0, speed)
                a.move(hp_bg, 0, speed)
                a.move(hp_bar, 0, speed)
                
                # 敌人超出画布底部，游戏结束

                if a.coords(container)[3] > 700:
                    # 删除敌人所有元素（容器+血条）
                    a.delete(container)
                    a.delete(hp_bg)
                    a.delete(hp_bar)
                    if enemy in e:
                        e.remove(enemy)
                    # 更新最高分
                    if score > high_score : 
                        high_score = score
                    paused = True
                    game_over = True
                    break
            except:
                if enemy in e:
                    e.remove(enemy)
                continue
        
        # 游戏结束弹窗
        if game_over:
            popup = tk.Toplevel(root)
            popup_width = 400
            popup_height = 300
            p1 = (root.winfo_screenwidth() - popup_width) // 2 - 50
            p2 = (root.winfo_screenheight() - popup_height) // 2 - 100
            popup.geometry(f'{popup_width}x{popup_height}+{p1}+{p2}')
            popup.configure(bg="pink")
            
            label_high = tk.Label(popup, text=f"最高分： {high_score}", bg="pink",
                    fg='black', font=("Arial", 15, "bold"))
            label_high.place(relx=0.075, rely=0.06)

            label_score = tk.Label(popup, text=f"你的得分是： {score}", bg="pink",
                    fg='black', font=("Arial", 25, "bold"))
            label_score.place(relx=0.075, rely=0.15)

            label = tk.Label(popup, text="可惜，你还得练！", bg="pink",
                    fg='black', font=("Arial", 30, "bold"))
            label.place(relx=0.075, rely=0.35)

            button_close = tk.Button(popup, text="关闭", command=lambda: os._exit(0), width=15, bg="white"
                , fg="black", font=("Arial", 10))   
            button_close.place(relx=0.59, rely=0.7)
            
            button_restart = tk.Button(popup, text="再来一次", command=restart, width=15, bg="white"
                , fg="black", font=("Arial", 10))   
            button_restart.place(relx=0.19, rely=0.7)
            continue

        # 子弹移动
        for bullet in n:
            try:
                a.move(bullet, 0, -5)
                if a.coords(bullet)[1] < 0:
                    a.delete(bullet)
                    if bullet in b:
                        b.remove(bullet)
            except:
                if bullet in b:
                    b.remove(bullet)
                continue

    # 增益1：子弹强化
        if random.random() < 0.003:                      
            zengyi1 = random.randint(1, 870)
            z.append(a.create_rectangle(zengyi1, 0, zengyi1+20, 30, fill='blue')) 

        # 增益1移动
        for z1 in Z1:
            try:
                a.move(z1, 0, 0.9)
                if a.coords(z1)[1] > 700:
                    a.delete(z1)
                    if z1 in z:
                        z.remove(z1)
            except:
                if z1 in z:
                    z.remove(z1)
                continue
        frame_count += 0.7 

        # 拾取增益1
        for z11 in Z1:        
            try:    
                if (a.coords(z11)[0] < a.coords(B)[2] and
                    a.coords(z11)[2] > a.coords(B)[0] and
                    a.coords(z11)[1] < a.coords(B)[3] and
                    a.coords(z11)[3] > a.coords(B)[1] ):
                    a.delete(z11)
                    if z11 in z:
                        z.remove(z11)
                    zengyi_1_active = True
                    zengyi_1_time_left = 15            
            except:
                if z11 in z:
                    z.remove(z11)
                continue 

    # 增益2：移速增加
        if random.random() < 0.0015:   
            zengyi_2_x= random.randint(1,870)
            zengyi_2_math = random.randint(0,360)
            z2.append(a.create_oval(zengyi_2_x, +0, zengyi_2_x+20,+30, fill="#9A45C1"))
 
        # 增益移动
        for z22 in Z2:                                          
            zengyi_2_move = 0 + 3*math.sin(zengyi_2_math)
            a.move(z22, zengyi_2_move, 2)
            if a.coords(z22)[1] > 700:
                a.delete(z22); z2.remove(z22)

        # 拾取增益2
        for z222 in Z2:
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

    # 增益3：瞬移
        if random.random() < 0.001 + score * 0.00008:                             
            zengyi_3 = random.randint(1, 870)
            z3.append(a.create_oval(zengyi_3, 0, zengyi_3+20, 25, fill='#2B9BA9'))        

        # 增益3移动
        for z33 in Z3:                                     
            try:
                a.move(z33, 0, 0.9)
                if a.coords(z33)[1] > 900:
                    a.delete(z33)
                    if z33 in z3:
                        z3.remove(z33)
            except:
                if z33 in z3:
                    z3.remove(z33)
                continue

        # 拾取增益3
        for z333 in Z3: 
            try:    
                if (a.coords(z333)[0] < a.coords(B)[2] and
                    a.coords(z333)[2] > a.coords(B)[0] and
                    a.coords(z333)[1] < a.coords(B)[3] and
                    a.coords(z333)[3] > a.coords(B)[1] ):
                    a.delete(z333)
                    if z333 in z3:
                        z3.remove(z333)
                    shunyi_number += 1
                    a.itemconfig(zengyi_3_text, text=f"剩余瞬移次数: {shunyi_number}次")
            except:
                if z333 in z3:
                    z3.remove(z333)
                continue
        
    # 增益时间计数
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
                    a.itemconfig(zengyi_3_text_2, state='hidden')
            if zengyi_3_time_left_2 > 0 :
                zengyi_3_time_left_2 -= 1
                if zengyi_3_time_left_2 <= 0 :     
                    a.itemconfig(zengyi_3_text_3, state='hidden')             

        # 子弹击中敌人的掉血效果 ，更是阴间
        remove_enemy = []
        for zidan in n:                  # 遍历每一颗子弹
            hit_flag = False             # 标记是否击中敌人（避免一颗子弹打多个）
            for enemy2 in e2:            # 遍历每一个敌人
                if hit_flag:
                    continue
                try:                                  
                    container, hp_bg, hp_bar, max_hp, current_hp, width, height = enemy2
                    # 碰撞检测：子弹和敌人容器碰撞
                    if (a.coords(zidan)[0] < a.coords(container)[2] and
                        a.coords(zidan)[2] > a.coords(container)[0] and
                        a.coords(zidan)[1] < a.coords(container)[3] and
                        a.coords(zidan)[3] > a.coords(container)[1]):
                        a.delete(zidan)
                        if zidan in b:    
                            b.remove(zidan)
                        # 敌人掉血
                        enemy2[4] -= hurt
                        # 更新血条
                        update_enemy_hp(enemy2)
                        if enemy2[4] <= 0:
                            a.delete(container)
                            a.delete(hp_bg)
                            a.delete(hp_bar)
                            remove_enemy.append(enemy2)    
                        hit_flag = True  # 一颗子弹只击中一个敌人
                except:
                    continue
        
        # 删除被击败的敌人 更新分数
        for em in remove_enemy:
            if em in e:
                e.remove(em)
                score += 1
                a.itemconfig(Score, text=f'分数： {score}')
                a.itemconfig(High_score, text=f'最高分数： {high_score}') 
        remove_enemy.clear()                           

    root.update()
    time.sleep(0.008)