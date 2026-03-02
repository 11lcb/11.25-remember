import random
import tkinter as tk
import time
import os
import math

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", root.destroy)
root.title("大型地图射击(F11全屏)")

# --- 全屏设置 ---
is_fullscreen = False


def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)
    if not is_fullscreen: root.geometry(f'900x750')


root.bind("<F11>", toggle_fullscreen)

main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

# 顶部UI
control_frame = tk.Frame(main_frame, bg="#222")
control_frame.pack(side=tk.TOP, fill=tk.X)
tk.Button(control_frame, text="退出", command=lambda: os._exit(0), bg="#444", fg="white", width=8).pack(side=tk.RIGHT,
                                                                                                        padx=5)
info_label = tk.Label(control_frame, text="[战斗] 进房锁门 -> 杀敌+捡道具 -> 开门 | 蓝色:散弹 紫色:加速 青色:瞬移| 操作：WASD移动 | 鼠标射击 | Shift瞬移 | F11全屏", font=("Arial", 10), bg="#222",
                      fg="white")
info_label.pack(side=tk.LEFT, padx=5)

a = tk.Canvas(main_frame, bg='#222', highlightthickness=0)
a.pack(fill="both", expand=True)

# 小地图
minimap_scale = 2.5
minimap = tk.Canvas(main_frame, width=150, height=150, bg="black", highlightthickness=1, highlightbackground="gray")
minimap.place(x=10, y=50)
minimap_player_dot = None

# 悬浮UI
ui_score = tk.Label(main_frame, text="分数: 0", font=("Arial", 14, "bold"), fg="yellow", bg="#222")
ui_score.place(relx=0.95, y=50, anchor="ne")
ui_room_info = tk.Label(main_frame, text="安全区域", font=("Arial", 14, "bold"), fg="#00FF00", bg="#222")
ui_room_info.place(relx=0.5, y=50, anchor="n")
ui_buffs = tk.Label(main_frame, text="", font=("Arial", 12), fg="cyan", bg="#222")
ui_buffs.place(relx=0.05, rely=0.9, anchor="sw")

# --- 核心参数 ---
TILE_SIZE = 60
MAP_COLS = 60
MAP_ROWS = 60
game_map = []
room_list = []

# 游戏对象
B = None
e = []
b = []
items = []
spawning_queue = []

score = 0
speed_base = 7
speed_user = 7
current_room_index = -1
is_battle_locked = False
spawn_pending = False

# 增益
buff_scatter = False
buff_scatter_time = 0
buff_speed = False
buff_speed_time = 0
teleport_count = 0


class Room:
    def __init__(self, x, y, w, h, is_start=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w // 2, y + h // 2
        self.cleared = is_start
        self.gates_coords = []
        self.enemy_count = random.randint(4, 8) if not is_start else 0

    def is_player_inside(self, px, py):
        margin = 40
        x1, y1 = self.x * TILE_SIZE + margin, self.y * TILE_SIZE + margin
        x2, y2 = (self.x + self.w) * TILE_SIZE - margin, (self.y + self.h) * TILE_SIZE - margin
        return x1 < px < x2 and y1 < py < y2


# --- 地图生成工具 ---
def create_h_tunnel(x1, x2, y):
    start, end = min(x1, x2), max(x1, x2)
    for x in range(start, end + 1):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            game_map[y][x] = 1
            game_map[y + 1][x] = 1


def create_v_tunnel(y1, y2, x):
    start, end = min(y1, y2), max(y1, y2)
    for y in range(start, end + 1):
        if 0 <= y < MAP_ROWS and 0 <= x < MAP_COLS:
            game_map[y][x] = 1
            game_map[y][x + 1] = 1


def connect_rooms(r1, r2):
    x1, y1 = r1.cx, r1.cy
    x2, y2 = r2.cx, r2.cy
    if random.random() < 0.5:
        create_h_tunnel(x1, x2, y1)
        create_v_tunnel(y1, y2, x2)
    else:
        create_v_tunnel(y1, y2, x1)
        create_h_tunnel(x1, x2, y2)


def decorate_room(x, y, w, h):
    if w > 6 and h > 6:
        style = random.randint(0, 4)
        if style == 1:
            game_map[y + 3][x + 3] = 0
            game_map[y + 3][x + w - 4] = 0
            game_map[y + h - 4][x + 3] = 0
            game_map[y + h - 4][x + w - 4] = 0
        elif style == 2:
            cx, cy = x + w // 2, y + h // 2
            game_map[cy][cx] = 0
            game_map[cy][cx + 1] = 0
        elif style == 3:
            for _ in range(4):
                rx = random.randint(x + 3, x + w - 4)
                ry = random.randint(y + 3, y + h - 4)
                game_map[ry][rx] = 0


def generate_map():
    global game_map, room_list
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []

    for i in range(25):
        w = random.randint(10, 16)
        h = random.randint(10, 16)
        x = random.randint(2, MAP_COLS - w - 2)
        y = random.randint(2, MAP_ROWS - h - 2)
        overlap = False
        for r in room_list:
            if not (x + w + 3 < r.x or x > r.x + r.w + 3 or y + h + 3 < r.y or y > r.y + r.h + 3):
                overlap = True
                break
        if not overlap:
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            if len(room_list) > 0: decorate_room(x, y, w, h)
            room_list.append(Room(x, y, w, h, len(room_list) == 0))

    for i in range(1, len(room_list)):
        target = i - 1
        if i > 2 and random.random() < 0.2: target = random.randint(0, i - 2)
        connect_rooms(room_list[i], room_list[target])

    a.delete("wall")
    a.delete("gate")
    a.config(bg="#222")
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if game_map[r][c] == 0:
                x1, y1 = c * TILE_SIZE, r * TILE_SIZE
                a.create_rectangle(x1, y1, x1 + TILE_SIZE, y1 + TILE_SIZE, fill="#111", outline="#333", tags="wall")

    a.config(scrollregion=(0, 0, MAP_COLS * TILE_SIZE, MAP_ROWS * TILE_SIZE))
    draw_minimap_static()
    return room_list[0].cx * TILE_SIZE, room_list[0].cy * TILE_SIZE


def draw_minimap_static():
    minimap.delete("all")
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if game_map[r][c] == 1:
                x, y = c * minimap_scale, r * minimap_scale
                minimap.create_rectangle(x, y, x + minimap_scale, y + minimap_scale, fill="#555", outline="")


def update_minimap_player(px, py):
    global minimap_player_dot
    if minimap_player_dot: minimap.delete(minimap_player_dot)
    mx, my = (px / TILE_SIZE) * minimap_scale, (py / TILE_SIZE) * minimap_scale
    minimap_player_dot = minimap.create_oval(mx - 3, my - 3, mx + 3, my + 3, fill="red", outline="white")


def toggle_room_gates(room, close=True):
    tag_name = f"gate_{room_list.index(room)}"
    if close:
        room.gates_coords = []
        for c in range(room.x, room.x + room.w):
            if game_map[room.y - 1][c] == 1: room.gates_coords.append((room.y - 1, c))
            if game_map[room.y + room.h][c] == 1: room.gates_coords.append((room.y + room.h, c))
        for r in range(room.y, room.y + room.h):
            if game_map[r][room.x - 1] == 1: room.gates_coords.append((r, room.x - 1))
            if game_map[r][room.x + room.w] == 1: room.gates_coords.append((r, room.x + room.w))
        for r, c in room.gates_coords:
            game_map[r][c] = 2
            x1, y1 = c * TILE_SIZE, r * TILE_SIZE
            a.create_rectangle(x1, y1, x1 + TILE_SIZE, y1 + TILE_SIZE, fill="orange", outline="yellow",
                               tags=("gate", tag_name))
    else:
        for r, c in room.gates_coords: game_map[r][c] = 1
        a.delete(tag_name)


# --- 敌人生成逻辑 (预警 + 安全距离) ---
def spawn_room_enemies(room):
    global spawn_pending
    spawn_pending = True

    count = room.enemy_count
    spawned = 0
    attempts = 0

    px, py = get_player_center()

    while spawned < count and attempts < 100:
        rx = random.randint(room.x + 1, room.x + room.w - 2)
        ry = random.randint(room.y + 1, room.y + room.h - 2)

        if game_map[ry][rx] == 1:
            ex, ey = rx * TILE_SIZE + TILE_SIZE / 2, ry * TILE_SIZE + TILE_SIZE / 2

            dist = math.hypot(ex - px, ey - py)
            if dist < 250:
                attempts += 1
                continue

            warn_id = a.create_text(ex, ey, text="!", font=("Arial", 30, "bold"), fill="red")
            warn_circle = a.create_oval(ex - 20, ey - 20, ex + 20, ey + 20, outline="red", width=2)

            spawning_queue.append([ex, ey, 60, [warn_id, warn_circle]])  # 60帧约为0.6~1秒

            spawned += 1
        attempts += 1


def spawn_room_items(room):
    num_items = random.randint(1, 2)
    for _ in range(num_items):
        rx = random.randint(room.x + 2, room.x + room.w - 3)
        ry = random.randint(room.y + 2, room.y + room.h - 3)
        if game_map[ry][rx] == 1:
            ix, iy = rx * TILE_SIZE + TILE_SIZE / 2, ry * TILE_SIZE + TILE_SIZE / 2
            itype = random.choices([0, 1, 2], weights=[60, 20, 20])[0]
            color = ['#87CEEB', '#DDA0DD', '#2B9BA9'][itype]
            item_id = a.create_rectangle(ix - 12, iy - 12, ix + 12, iy + 12, fill=color, outline='white')
            items.append([item_id, itype, ix, iy])


def is_wall(x, y):
    c, r = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if r < 0 or r >= MAP_ROWS or c < 0 or c >= MAP_COLS: return True
    return game_map[r][c] == 0 or game_map[r][c] == 2


def check_collision(px, py, rad=10):
    for x, y in [(px - rad, py), (px + rad, py), (px, py - rad), (px, py + rad)]:
        if is_wall(x, y): return True
    return False


def get_player_center():
    coords = a.coords(B)
    return ((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2)


def update_camera():
    if not B: return
    px, py = get_player_center()
    cw, ch = a.winfo_width(), a.winfo_height()
    a.xview_moveto((px - cw / 2) / (MAP_COLS * TILE_SIZE))
    a.yview_moveto((py - ch / 2) / (MAP_ROWS * TILE_SIZE))
    update_minimap_player(px, py)


def create_enemy(x, y, r, hp):
    c = a.create_oval(x - r, y - r, x + r, y + r, fill='#FF4444', outline='')
    bg = a.create_rectangle(x - r, y - r - 8, x + r, y - r - 3, fill='black', outline='red')
    bar = a.create_rectangle(x - r, y - r - 8, x + r, y - r - 3, fill='red', outline='')
    return [c, bg, bar, hp, hp, r]


def restart():
    global e, b, items, spawning_queue, score, B, current_room_index, is_battle_locked, spawn_pending
    global buff_scatter, buff_scatter_time, buff_speed, buff_speed_time, teleport_count, speed_user

    e, b, items, spawning_queue = [], [], [], []
    score = 0
    current_room_index = -1
    is_battle_locked = False
    spawn_pending = False

    buff_scatter = False
    buff_speed = False
    speed_user = speed_base
    teleport_count = 0

    a.delete("all")
    ui_score.config(text="分数: 0")

    sx, sy = generate_map()
    B = a.create_oval(sx - 10, sy - 10, sx + 10, sy + 10, fill='#90EE90', outline='white')
    global crosshair
    crosshair = a.create_text(0, 0, text="+", fill="white", font=("Arial", 14))
    update_camera()


left_1 = right_1 = up_1 = down_1 = False
root.bind("<KeyPress-a>", lambda e: globals().update(left_1=True))
root.bind("<KeyRelease-a>", lambda e: globals().update(left_1=False))
root.bind("<KeyPress-d>", lambda e: globals().update(right_1=True))
root.bind("<KeyRelease-d>", lambda e: globals().update(right_1=False))
root.bind("<KeyPress-w>", lambda e: globals().update(up_1=True))
root.bind("<KeyRelease-w>", lambda e: globals().update(up_1=False))
root.bind("<KeyPress-s>", lambda e: globals().update(down_1=True))
root.bind("<KeyRelease-s>", lambda e: globals().update(down_1=False))
shooting = False
a.bind("<ButtonPress-1>", lambda e: globals().update(shooting=True))
a.bind("<ButtonRelease-1>", lambda e: globals().update(shooting=False))
a.bind("<Motion>", lambda e: a.coords(crosshair, a.canvasx(e.x), a.canvasy(e.y)))


def trigger_teleport(event):
    global teleport_count
    if teleport_count > 0:
        px, py = get_player_center()
        mx = a.canvasx(root.winfo_pointerx() - root.winfo_rootx())
        my = a.canvasy(root.winfo_pointery() - root.winfo_rooty() - control_frame.winfo_height())
        dx, dy = mx - px, my - py
        dist = math.hypot(dx, dy)
        if dist > 0:
            jump_dist = 150
            nx = px + (dx / dist) * jump_dist
            ny = py + (dy / dist) * jump_dist
            if not is_wall(nx, ny):
                a.coords(B, nx - 10, ny - 10, nx + 10, ny + 10)
                teleport_count -= 1


root.bind("<Shift_L>", trigger_teleport)

last_shoot_time = 0


def shoot():
    px, py = get_player_center()
    mx = a.canvasx(root.winfo_pointerx() - root.winfo_rootx())
    my = a.canvasy(root.winfo_pointery() - root.winfo_rooty() - control_frame.winfo_height())
    dx, dy = mx - px, my - py
    d = math.hypot(dx, dy) or 1
    speed = 12
    vx, vy = dx / d * speed, dy / d * speed
    b.append([a.create_rectangle(px - 3, py - 3, px + 3, py + 3, fill="white", outline=''), vx, vy])
    if buff_scatter:
        angle = math.atan2(vy, vx)
        for offset in [-0.2, 0.2]:
            na = angle + offset
            nvx, nvy = math.cos(na) * speed, math.sin(na) * speed
            b.append([a.create_rectangle(px - 3, py - 3, px + 3, py + 3, fill="#87CEEB", outline=''), nvx, nvy])


root.geometry(f'900x750+{root.winfo_screenwidth() // 2 - 450}+{root.winfo_screenheight() // 2 - 410}')
restart()

while True:
    pc = a.coords(B)
    cx, cy = (pc[0] + pc[2]) / 2, (pc[1] + pc[3]) / 2
    mx, my = 0, 0
    if left_1: mx -= speed_user
    if right_1: mx += speed_user
    if up_1: my -= speed_user
    if down_1: my += speed_user

    if mx != 0 and not check_collision(cx + mx, cy): a.move(B, mx, 0)
    if my != 0 and not check_collision(cx if mx == 0 else a.coords(B)[0] + 10, cy + my): a.move(B, 0, my)

    update_camera()

    pc = a.coords(B)
    player_x, player_y = (pc[0] + pc[2]) / 2, (pc[1] + pc[3]) / 2

    for i, room in enumerate(room_list):
        if room.is_player_inside(player_x, player_y):
            if not room.cleared and not is_battle_locked:
                current_room_index = i
                is_battle_locked = True
                toggle_room_gates(room, close=True)
                spawn_room_enemies(room)
                spawn_room_items(room)
                ui_room_info.config(text="警告：敌人接近中！", fg="orange")
            break

    if is_battle_locked:
        for spawn in spawning_queue[:]:
            spawn[2] -= 1
            if spawn[2] <= 0:
                a.delete(spawn[3][0])
                a.delete(spawn[3][1])
                hp = 40 + score * 1.5
                new_e = create_enemy(spawn[0], spawn[1], 15, hp)
                e.append(new_e)
                spawning_queue.remove(spawn)

        # 检查是否所有敌人都生成完了
        if len(spawning_queue) == 0:
            spawn_pending = False
            ui_room_info.config(text="战斗开始！", fg="red")

        # 战斗结束检查 (必须队列为空且场上无敌人)
        if not spawn_pending and len(e) == 0:
            room = room_list[current_room_index]
            room.cleared = True
            is_battle_locked = False
            toggle_room_gates(room, close=False)
            ui_room_info.config(text="区域安全", fg="#00FF00")
            if sum(1 for r in room_list if not r.cleared) == 0:
                ui_room_info.config(text="全图通关！", fg="gold")

    if shooting and time.time() - last_shoot_time > 0.15:
        shoot()
        last_shoot_time = time.time()

    for bullet in b[:]:
        try:
            bid, vx, vy = bullet
            a.move(bid, vx, vy)
            bc = a.coords(bid)
            bx, by = (bc[0] + bc[2]) / 2, (bc[1] + bc[3]) / 2
            if is_wall(bx, by):
                a.delete(bid)
                b.remove(bullet)
                continue
            hit = False
            for enemy in e:
                ec = a.coords(enemy[0])
                if bc[0] < ec[2] and bc[2] > ec[0] and bc[1] < ec[3] and bc[3] > ec[1]:
                    enemy[4] -= 15
                    hp_ratio = max(0, enemy[4] / enemy[3])
                    ex1 = a.coords(enemy[0])[0]
                    ey1 = a.coords(enemy[0])[1]
                    a.coords(enemy[2], ex1, ey1 - 8, ex1 + 2 * enemy[5] * hp_ratio, ey1 - 3)
                    a.delete(bid)
                    b.remove(bullet)
                    hit = True
                    if enemy[4] <= 0:
                        for part in enemy[:3]: a.delete(part)
                        e.remove(enemy)
                        score += 10
                        ui_score.config(text=f"分数: {score}")
                    break
            if hit: continue
        except:
            if bullet in b: b.remove(bullet)

    for item in items[:]:
        try:
            iid, itype, ix, iy = item
            if math.hypot(player_x - ix, player_y - iy) < 30:
                a.delete(iid)
                items.remove(item)
                if itype == 0:
                    buff_scatter = True; buff_scatter_time = 300
                elif itype == 1:
                    buff_speed = True; buff_speed_time = 300; speed_user = 11
                elif itype == 2:
                    teleport_count += 1
        except:
            pass

    buff_text = ""
    if buff_scatter:
        buff_scatter_time -= 1
        buff_text += f"散弹: {buff_scatter_time // 10} "
        if buff_scatter_time <= 0: buff_scatter = False
    if buff_speed:
        buff_speed_time -= 1
        buff_text += f"加速: {buff_speed_time // 10} "
        if buff_speed_time <= 0: buff_speed = False; speed_user = speed_base
    if teleport_count > 0: buff_text += f"瞬移: {teleport_count}"
    ui_buffs.config(text=buff_text)

    for enemy in e:
        try:
            container = enemy[0]
            ec = a.coords(container)
            ex, ey = (ec[0] + ec[2]) / 2, (ec[1] + ec[3]) / 2
            dx, dy = player_x - ex, player_y - ey
            d = math.hypot(dx, dy)
            if d > 0:
                vx, vy = dx / d * 2.5, dy / d * 2.5
                if not is_wall(ex + vx, ey): a.move(enemy[0], vx, 0); a.move(enemy[1], vx, 0); a.move(enemy[2], vx, 0)
                if not is_wall(ex, ey + vy): a.move(enemy[0], 0, vy); a.move(enemy[1], 0, vy); a.move(enemy[2], 0, vy)
            if ec[0] < pc[2] and ec[2] > pc[0] and ec[1] < pc[3] and ec[3] > pc[1]:
                restart()
        except:
            pass

    root.update()
    time.sleep(0.01)