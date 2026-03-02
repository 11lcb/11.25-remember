import pygame
import random
import math
import sys
import os

# ==========================================
# 1. 初始化与全局设置
# ==========================================
pygame.init()
pygame.font.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 750
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("绝境突围：无尽肉鸽")

# 颜色
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
RED, GREEN, BLUE = (255, 68, 68), (144, 238, 144), (135, 206, 235)
YELLOW, PURPLE, GRAY = (255, 215, 0), (138, 43, 226), (100, 100, 100)
BOSS_COLOR = (139, 0, 0)

TILE_SIZE = 60
MAP_COLS, MAP_ROWS = 60, 60
game_map, room_list = [], []

# 尝试使用支持中文的字体，如果没有则用系统默认
font_name = "SimHei" if "simhei" in pygame.font.get_fonts() else "Arial"
font_base = pygame.font.SysFont(font_name, 18)
font_large = pygame.font.SysFont(font_name, 26, bold=True)
font_title = pygame.font.SysFont(font_name, 50, bold=True)

# 难度倍率
difficulty_mult = {"hp": 1.0, "dmg": 1, "spd": 1.0}

# ==========================================
# 2. 辅助函数：安全加载图片
# ==========================================
def load_frames(image_paths, fallback_color, size, shape="rect"):
    frames = []
    for path in image_paths:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    if not frames:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(surface, fallback_color, (size[0]//2, size[1]//2), min(size)//2)
        elif shape == "cross": # 死亡特效默认图
            pygame.draw.line(surface, fallback_color, (0,0), size, 4)
            pygame.draw.line(surface, fallback_color, (0,size[1]), (size[0],0), 4)
        else:
            pygame.draw.rect(surface, fallback_color, (0,0, size[0], size[1]), border_radius=5)
        frames.append(surface)
    return frames

# ==========================================
# 3. 游戏核心类 (Sprites)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.idle_frames = load_frames(["player_idle.png"], GREEN, (30, 30), "circle")
        self.run_frames = load_frames(["player_run1.png", "player_run2.png"], GREEN, (30, 30), "circle")
        # 👉【需要替换的图片文件】角色死亡图片
        self.death_frames = load_frames(["player_death.png"], GRAY, (40, 40), "cross")
        
        self.frames = self.idle_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        
        # 属性
        self.max_hp = 5
        self.hp = 5
        self.invincible_timer = 0
        self.speed = 6
        self.bullet_damage = 15
        self.scatter_level = 0
        self.shoot_cd = 300 # 初始射击冷却(毫秒)
        
        # 天赋
        self.has_bounce = False
        self.has_magnet = False

    def update(self, dx, dy, is_dead=False):
        if is_dead:
            self.image = self.death_frames[0]
            return

        if self.invincible_timer > 0: self.invincible_timer -= 1

        if dx != 0 or dy != 0:
            self.frames = self.run_frames
            if dx > 0: self.facing_right = True
            elif dx < 0: self.facing_right = False
        else:
            self.frames = self.idle_frames

        self.current_frame += 0.15
        if self.current_frame >= len(self.frames): self.current_frame = 0
        self.image = self.frames[int(self.current_frame)].copy()
        
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            self.image.set_alpha(100)
            
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, floor):
        super().__init__()
        self.max_hp = hp * difficulty_mult["hp"]
        self.hp = self.max_hp
        self.speed = 2.0 + (floor * 0.1) * difficulty_mult["spd"] # 随层数加速
        self.frames = load_frames(["enemy_run.png"], RED, (30, 30), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, px, py):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            vx, vy = (dx / dist) * self.speed, (dy / dist) * self.speed
            if not is_wall(self.rect.centerx + vx, self.rect.centery): self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy): self.rect.centery += vy

    def draw_hp(self, surface, camera_x, camera_y):
        draw_x, draw_y = self.rect.x - camera_x, self.rect.y - camera_y - 10
        pygame.draw.rect(surface, BLACK, (draw_x, draw_y, 30, 5))
        pygame.draw.rect(surface, RED, (draw_x, draw_y, 30 * max(0, self.hp / self.max_hp), 5))

# --- 新增：BOSS 类 ---
class Boss(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 3, floor) # Boss血量极厚
        # 👉【需要替换的图片文件】BOSS图片
        self.frames = load_frames(["boss.png"], BOSS_COLOR, (80, 80), "rect")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1.5 * difficulty_mult["spd"]
        self.shoot_timer = 0
        self.shoot_cd = max(60, 120 - floor * 5) # 层数越高，射得越快

    def update(self, px, py, enemy_bullets_group):
        super().update(px, py)
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cd:
            self.shoot_timer = 0
            # 向玩家发射红色子弹
            angle = math.atan2(py - self.rect.centery, px - self.rect.centerx)
            # Boss 散射技能
            enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle))
            enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle - 0.3))
            enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle + 0.3))

    def draw_hp(self, surface, camera_x, camera_y):
        # Boss大血条画在屏幕正下方
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20))
        pygame.draw.rect(surface, BOSS_COLOR, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400 * max(0, self.hp / self.max_hp), 20))
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20), 2)
        txt = font_base.render("守 门 巨 兽", True, WHITE)
        surface.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT - 65))

# --- 新增：敌人子弹类 ---
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (6, 6), 6)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 3) # 火球特效
        self.rect = self.image.get_rect(center=(x, y))
        speed = 7 * difficulty_mult["spd"]
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage, player):
        super().__init__()
        self.frames = load_frames(["bullet.png"], WHITE, (8, 8), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        self.player = player
        self.speed = 15
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.bounces = 1 if player.has_bounce else 0

    def update(self):
        # 分离XY轴判断，完美实现子弹反弹墙壁
        self.rect.x += self.vx
        if is_wall(self.rect.centerx, self.rect.centery):
            if self.bounces > 0:
                self.rect.x -= self.vx
                self.vx = -self.vx
                self.bounces -= 1
            else: self.kill(); return

        self.rect.y += self.vy
        if is_wall(self.rect.centerx, self.rect.centery):
            if self.bounces > 0:
                self.rect.y -= self.vy
                self.vy = -self.vy
                self.bounces -= 1
            else: self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = load_frames(["coin.png"], YELLOW, (15, 15), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.time_offset = random.random() * math.pi * 2

    def update(self, player):
        # 金币磁铁天赋
        if player.has_magnet:
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 250: # 吸附范围
                self.rect.centerx += (dx / dist) * 8
                self.rect.centery += (dy / dist) * 8
                return # 飞行时停止上下浮动动画

        self.rect.centery = self.base_y + math.sin(pygame.time.get_ticks() / 150 + self.time_offset) * 5

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_base = load_frames(["portal.png"], PURPLE, (50, 50), "circle")[0]
        self.image = self.image_base
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0

    def update(self):
        self.angle = (self.angle + 3) % 360
        self.image = pygame.transform.rotate(self.image_base, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class SpawnerWarning:
    def __init__(self, x, y): self.x, self.y, self.timer = x, y, 60

# ==========================================
# 4. 地图生成 (普通迷宫 & Boss房)
# ==========================================
class Room:
    def __init__(self, x, y, w, h, is_start=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w // 2, y + h // 2
        self.cleared = is_start
        self.gates_coords = []
        self.enemy_count = random.randint(4, 8) if not is_start else 0

    def is_player_inside(self, px, py):
        m = 40
        return self.x*TILE_SIZE+m < px < (self.x+self.w)*TILE_SIZE-m and self.y*TILE_SIZE+m < py < (self.y+self.h)*TILE_SIZE-m

def generate_map(floor):
    global game_map, room_list
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []
    
    # 每 5 关生成 Boss 房间 (大角斗场)
    if floor % 5 == 0:
        w, h = 30, 30
        x, y = (MAP_COLS - w)//2, (MAP_ROWS - h)//2
        for r in range(y, y+h):
            for c in range(x, x+w): game_map[r][c] = 1
        room = Room(x, y, w, h, False) # 不设为已清理，直接进入战斗
        room.enemy_count = 0 # 不刷普通怪，刷Boss
        room_list.append(room)
        return room.cx * TILE_SIZE, (room.y + 2) * TILE_SIZE # 玩家出生在房间顶部
        
    # 普通迷宫
    for _ in range(15):
        w, h = random.randint(10, 16), random.randint(10, 16)
        x, y = random.randint(2, MAP_COLS - w - 2), random.randint(2, MAP_ROWS - h - 2)
        if not any(not (x+w+3<r.x or x>r.x+r.w+3 or y+h+3<r.y or y>r.y+r.h+3) for r in room_list):
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            room_list.append(Room(x, y, w, h, len(room_list) == 0))

    for i in range(1, len(room_list)):
        target = random.randint(0, i-2) if i > 2 and random.random() < 0.2 else i-1
        r1, r2 = room_list[i], room_list[target]
        if random.random() < 0.5:
            for x in range(min(r1.cx, r2.cx), max(r1.cx, r2.cx)+1): game_map[r1.cy][x] = game_map[r1.cy+1][x] = 1
            for y in range(min(r1.cy, r2.cy), max(r1.cy, r2.cy)+1): game_map[y][r2.cx] = game_map[y][r2.cx+1] = 1
        else:
            for y in range(min(r1.cy, r2.cy), max(r1.cy, r2.cy)+1): game_map[y][r1.cx] = game_map[y][r1.cx+1] = 1
            for x in range(min(r1.cx, r2.cx), max(r1.cx, r2.cx)+1): game_map[r2.cy][x] = game_map[r2.cy+1][x] = 1

    return room_list[0].cx * TILE_SIZE, room_list[0].cy * TILE_SIZE

def is_wall(x, y):
    c, r = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if r < 0 or r >= MAP_ROWS or c < 0 or c >= MAP_COLS: return True
    return game_map[r][c] == 0 or game_map[r][c] == 2

def toggle_room_gates(room, close=True):
    if close:
        room.gates_coords = []
        for c in range(room.x, room.x + room.w):
            if game_map[room.y-1][c] == 1: room.gates_coords.append((room.y-1, c))
            if game_map[room.y+room.h][c] == 1: room.gates_coords.append((room.y+room.h, c))
        for r in range(room.y, room.y + room.h):
            if game_map[r][room.x-1] == 1: room.gates_coords.append((r, room.x-1))
            if game_map[r][room.x+room.w] == 1: room.gates_coords.append((r, room.x+room.w))
        for r, c in room.gates_coords: game_map[r][c] = 2
    else:
        for r, c in room.gates_coords: game_map[r][c] = 1

# ==========================================
# 5. UI 弹窗绘制函数
# ==========================================
def draw_button(screen, text, x, y, w, h, color, hover_color, mx, my):
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mx, my)
    pygame.draw.rect(screen, hover_color if is_hover else color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    txt_surf = font_large.render(text, True, BLACK if is_hover else WHITE)
    screen.blit(txt_surf, (x + w//2 - txt_surf.get_width()//2, y + h//2 - txt_surf.get_height()//2))
    return is_hover

def draw_menu(screen, mx, my):
    screen.fill((20, 20, 30))
    title = font_title.render("绝 境 突 围", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    
    play_hover = draw_button(screen, "开始游戏", SCREEN_WIDTH//2-100, 350, 200, 50, (50,150,50), (100,200,100), mx, my)
    diff_hover = draw_button(screen, "难度选择", SCREEN_WIDTH//2-100, 420, 200, 50, (150,100,50), (200,150,100), mx, my)
    intro_hover = draw_button(screen, "游戏介绍", SCREEN_WIDTH//2-100, 490, 200, 50, (50,100,150), (100,150,200), mx, my)
    quit_hover = draw_button(screen, "退出游戏", SCREEN_WIDTH//2-100, 560, 200, 50, (150,50,50), (200,100,100), mx, my)
    return play_hover, diff_hover, intro_hover, quit_hover

def draw_shop(screen, player, coins, shop_items, mx, my):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200); overlay.fill(BLACK); screen.blit(overlay, (0, 0))

    pw, ph = 600, 450
    px, py = (SCREEN_WIDTH - pw)//2, (SCREEN_HEIGHT - ph)//2
    pygame.draw.rect(screen, (40,40,40), (px, py, pw, ph), border_radius=10)
    pygame.draw.rect(screen, YELLOW, (px, py, pw, ph), 3, border_radius=10)

    title = font_title.render("—— 神 秘 商 店 ——", True, YELLOW)
    screen.blit(title, (px+pw//2 - title.get_width()//2, py+20))
    screen.blit(font_large.render(f"持有金币: {coins}", True, WHITE), (px+30, py+80))

    buttons = []
    for i, item in enumerate(shop_items):
        y = py + 130 + i*60
        name_color = GRAY if item['level'] >= item['max'] else WHITE
        lvl_txt = "(Max)" if item['level'] >= item['max'] else f"(Lv.{item['level']})"
        screen.blit(font_large.render(f"{item['name']} {lvl_txt}", True, name_color), (px+40, y))
        
        btn_rect = pygame.Rect(px+pw-160, y-5, 120, 40)
        can_buy = coins >= item['cost'] and item['level'] < item['max']
        is_hover = can_buy and btn_rect.collidepoint(mx, my)
        
        pygame.draw.rect(screen, (100,200,100) if is_hover else (50,150,50) if can_buy else GRAY, btn_rect, border_radius=5)
        cost_txt = font_base.render(f"${item['cost']}", True, BLACK if is_hover else WHITE)
        screen.blit(cost_txt, (btn_rect.x+60-cost_txt.get_width()//2, btn_rect.y+10))
        buttons.append((btn_rect, item, can_buy))

    tip = font_base.render("按 TAB 键关闭", True, GRAY)
    screen.blit(tip, (px+pw//2 - tip.get_width()//2, py+ph-30))
    return buttons

def draw_talent(screen, talents, mx, my):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(230); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
    
    title = font_title.render("神 赐 天 赋 (三选一)", True, PURPLE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    buttons = []
    for i, t in enumerate(talents):
        bx = SCREEN_WIDTH//2 - 150
        by = 250 + i * 120
        is_hover = draw_button(screen, f"{t['name']} : {t['desc']}", bx, by, 300, 80, (50,50,80), (80,80,120), mx, my)
        buttons.append((is_hover, t))
    return buttons

# ==========================================
# 6. 主程序与状态机
# ==========================================
def main():
    clock = pygame.time.Clock()
    wall_img = load_frames(["wall.png"], (20, 20, 25), (TILE_SIZE, TILE_SIZE), "rect")[0]
    floor_img = load_frames(["floor.png"], (40, 40, 45), (TILE_SIZE, TILE_SIZE), "rect")[0]

    # 状态机：MENU, DIFF, INTRO, PLAYING, SHOP, TALENT, GAMEOVER_ANIM, GAMEOVER
    game_state = "MENU"
    coins = 0
    current_floor = 1
    difficulty_name = "普通"
    death_timer = 0
    
    # 商店与天赋数据
    shop_items = [
        {"id": "dmg", "name": "提升攻击力", "cost": 10, "level": 0, "max": 10, "cost_up": 5},
        {"id": "spd", "name": "提升移动速度", "cost": 15, "level": 0, "max": 5, "cost_up": 10},
        {"id": "fir", "name": "提升射速", "cost": 20, "level": 0, "max": 5, "cost_up": 10},
        {"id": "sct", "name": "多重射击", "cost": 30, "level": 0, "max": 2, "cost_up": 30},
        {"id": "hp", "name": "恢复1点生命", "cost": 10, "level": 0, "max": 999, "cost_up": 0}
    ]
    
    all_talents = [
        {"id": "bounce", "name": "反弹墙壁", "desc": "子弹触墙可反弹1次"},
        {"id": "hp_up", "name": "生命涌动", "desc": "生命上限+2并回满血"},
        {"id": "magnet", "name": "金币磁铁", "desc": "大范围自动吸附金币"}
    ]
    current_talents = [] # 随机抽出的3个天赋

    def reset_floor(player_instance=None):
        sx, sy = generate_map(current_floor)
        p = Player(sx, sy) if player_instance is None else player_instance
        p.rect.center = (sx, sy)
        return p, pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), [], False

    player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor()
    last_shoot_time = 0
    is_battle_locked, current_room_index, spawn_pending = False, -1, False

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        events = pygame.event.get()
        
        # ==========================
        # 全局事件抓取
        # ==========================
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: pygame.display.toggle_fullscreen()

            # 状态切换逻辑
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "MENU":
                    if play_hover: 
                        coins, current_floor = 0, 1
                        for item in shop_items: item['level'] = 0
                        player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor()
                        game_state = "PLAYING"
                    elif diff_hover: game_state = "DIFF"
                    elif intro_hover: game_state = "INTRO"
                    elif quit_hover: running = False
                
                elif game_state == "DIFF":
                    if btn_easy: difficulty_mult.update({"hp":0.8, "dmg":1, "spd":0.9}); difficulty_name="简单"; game_state="MENU"
                    elif btn_norm: difficulty_mult.update({"hp":1.0, "dmg":1, "spd":1.0}); difficulty_name="普通"; game_state="MENU"
                    elif btn_hard: difficulty_mult.update({"hp":1.5, "dmg":2, "spd":1.2}); difficulty_name="困难"; game_state="MENU"
                
                elif game_state == "INTRO":
                    if btn_back: game_state = "MENU"
                
                elif game_state == "SHOP":
                    clicked = False
                    for btn_rect, item, can_buy in shop_btns:
                        if btn_rect.collidepoint(mx, my):
                            clicked = True
                            if can_buy:
                                coins -= item['cost']
                                item['level'] += 1
                                item['cost'] += item['cost_up']
                                if item['id'] == 'dmg': player.bullet_damage += 5
                                elif item['id'] == 'spd': player.speed += 1
                                elif item['id'] == 'fir': player.shoot_cd = max(100, player.shoot_cd - 40)
                                elif item['id'] == 'sct': player.scatter_level += 1
                                elif item['id'] == 'hp': 
                                    player.hp = min(player.max_hp, player.hp + 1)
                                    item['level'] -= 1
                    if not clicked and not pygame.Rect((SCREEN_WIDTH-600)//2, (SCREEN_HEIGHT-450)//2, 600, 450).collidepoint(mx, my):
                        game_state = "PLAYING"
                        
                elif game_state == "TALENT":
                    for is_hover, t in talent_btns:
                        if is_hover:
                            if t['id'] == 'bounce': player.has_bounce = True
                            elif t['id'] == 'hp_up': player.max_hp += 2; player.hp = player.max_hp
                            elif t['id'] == 'magnet': player.has_magnet = True
                            game_state = "PLAYING" # 选完继续

                elif game_state == "GAMEOVER":
                    if btn_restart:
                        game_state = "MENU"
                    elif btn_quit:
                        running = False

            if event.type == pygame.KEYDOWN and game_state in ["PLAYING", "SHOP"]:
                if event.key == pygame.K_TAB:
                    game_state = "SHOP" if game_state == "PLAYING" else "PLAYING"

        # ==========================
        # 菜单系统渲染
        # ==========================
        pygame.mouse.set_visible(game_state != "PLAYING")
        
        if game_state == "MENU":
            play_hover, diff_hover, intro_hover, quit_hover = draw_menu(screen, mx, my)
            # 难度提示
            diff_txt = font_base.render(f"当前难度: {difficulty_name}", True, GRAY)
            screen.blit(diff_txt, (SCREEN_WIDTH//2 - diff_txt.get_width()//2, 630))
            pygame.display.flip(); clock.tick(FPS); continue

        elif game_state == "DIFF":
            screen.fill((20,20,30))
            screen.blit(font_title.render("选 择 难 度", True, WHITE), (SCREEN_WIDTH//2-120, 150))
            btn_easy = draw_button(screen, "简单 (推荐新手)", SCREEN_WIDTH//2-150, 300, 300, 60, (50,150,50), (100,200,100), mx, my)
            btn_norm = draw_button(screen, "普通 (标准体验)", SCREEN_WIDTH//2-150, 400, 300, 60, (150,100,50), (200,150,100), mx, my)
            btn_hard = draw_button(screen, "困难 (硬核狂人)", SCREEN_WIDTH//2-150, 500, 300, 60, (150,50,50), (200,100,100), mx, my)
            pygame.display.flip(); clock.tick(FPS); continue
            
        elif game_state == "INTRO":
            screen.fill((20,20,30))
            lines = [
                "【绝境突围：无尽肉鸽】",
                "操作说明：WASD移动，鼠标左键射击，TAB键打开商店。",
                "游戏机制：清空房间怪物后解锁下一区域。",
                "          击败敌人掉落金币，金币用于商店强化。",
                "          每过3关可选择强力天赋。",
                "          每过5关将遭遇强大BOSS！",
                "生存下去，看看你能抵达多少层！"
            ]
            for i, line in enumerate(lines):
                c = YELLOW if i==0 else WHITE
                screen.blit(font_large.render(line, True, c), (100, 150 + i*40))
            btn_back = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 600, 200, 50, GRAY, WHITE, mx, my)
            pygame.display.flip(); clock.tick(FPS); continue

        # ==========================
        # 游戏主逻辑 (PLAYING & ANIMATIONS)
        # ==========================
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_a]: dx -= player.speed
            if keys[pygame.K_d]: dx += player.speed
            if keys[pygame.K_w]: dy -= player.speed
            if keys[pygame.K_s]: dy += player.speed

            if dx != 0 and not is_wall(player.rect.centerx+dx+(15 if dx>0 else -15), player.rect.centery): player.rect.centerx += dx
            if dy != 0 and not is_wall(player.rect.centerx, player.rect.centery+dy+(15 if dy>0 else -15)): player.rect.centery += dy
            player.update(dx, dy)

            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2

            # 射击
            if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - last_shoot_time > player.shoot_cd:
                wx, wy = mx + camera_x, my + camera_y
                angle = math.atan2(wy - player.rect.centery, wx - player.rect.centerx)
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle, player.bullet_damage, player))
                if player.scatter_level >= 1:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle-0.2, player.bullet_damage, player))
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle+0.2, player.bullet_damage, player))
                if player.scatter_level >= 2:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle-0.4, player.bullet_damage, player))
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle+0.4, player.bullet_damage, player))
                last_shoot_time = pygame.time.get_ticks()

            # 房间战斗触发
            room_info_text, room_info_color = f"第 {current_floor} 层", GREEN
            
            for i, room in enumerate(room_list):
                if room.is_player_inside(player.rect.centerx, player.rect.centery):
                    if not room.cleared and not is_battle_locked:
                        current_room_index = i
                        is_battle_locked, spawn_pending = True, True
                        toggle_room_gates(room, close=True)
                        
                        if current_floor % 5 == 0: # Boss房生成
                            room.enemy_count = 0
                            spawners.append(SpawnerWarning(room.cx*TILE_SIZE, room.cy*TILE_SIZE)) # 中心刷Boss
                        else:
                            room.enemy_count += current_floor
                            spawned = 0
                            while spawned < room.enemy_count:
                                rx = random.randint(room.x+1, room.x+room.w-2)*TILE_SIZE + TILE_SIZE//2
                                ry = random.randint(room.y+1, room.y+room.h-2)*TILE_SIZE + TILE_SIZE//2
                                if not is_wall(rx, ry) and math.hypot(rx-player.rect.centerx, ry-player.rect.centery) > 250:
                                    spawners.append(SpawnerWarning(rx, ry)); spawned += 1
                    break

            # 战斗逻辑
            if is_battle_locked:
                room_info_text = "敌人接近中！" if spawn_pending else "战斗中！"
                room_info_color = (255, 165, 0) if spawn_pending else RED
                
                for s in spawners[:]:
                    s.timer -= 1
                    if s.timer <= 0:
                        if current_floor % 5 == 0:
                            enemies.add(Boss(s.x, s.y, 200 + current_floor*50, current_floor))
                        else:
                            enemies.add(Enemy(s.x, s.y, 30 + current_floor*15, current_floor))
                        spawners.remove(s)
                
                if len(spawners) == 0: spawn_pending = False
                
                if not spawn_pending and len(enemies) == 0:
                    room_list[current_room_index].cleared = True
                    is_battle_locked = False
                    toggle_room_gates(room_list[current_room_index], close=False)
                    
            if all(r.cleared for r in room_list) and not portal_spawned:
                last_r = room_list[current_room_index]
                portals.add(Portal(last_r.cx * TILE_SIZE, last_r.cy * TILE_SIZE))
                portal_spawned = True
                
            if portal_spawned: room_info_text, room_info_color = "寻找传送门", PURPLE

            # 更新所有精灵
            bullets.update()
            enemy_bullets.update()
            for b in enemy_bullets:
                if is_wall(b.rect.centerx, b.rect.centery): b.kill()
            if current_floor % 5 == 0:
                enemies.update(player.rect.centerx, player.rect.centery, enemy_bullets) # Boss需要传入子弹组
            else:
                enemies.update(player.rect.centerx, player.rect.centery)
                
            coins_group.update(player)
            portals.update()

            # 碰撞逻辑
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for b in bullet_list: enemy.hp -= b.damage
                if enemy.hp <= 0:
                    enemy.kill()
                    coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    if random.random() < 0.4: coins_group.add(Coin(enemy.rect.centerx+15, enemy.rect.centery))
                    if isinstance(enemy, Boss): # Boss大爆
                        for _ in range(10): coins_group.add(Coin(enemy.rect.centerx+random.randint(-30,30), enemy.rect.centery+random.randint(-30,30)))
                    
            if player.invincible_timer <= 0:
                hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
                hit_bullets = pygame.sprite.spritecollide(player, enemy_bullets, True)
                damage_taken = 0
                if hit_enemies: damage_taken += difficulty_mult["dmg"]
                if hit_bullets: damage_taken += difficulty_mult["dmg"]
                
                if damage_taken > 0:
                    player.hp -= damage_taken
                    player.invincible_timer = 60
                    if player.hp <= 0:
                        game_state = "GAMEOVER_ANIM"
                        death_timer = pygame.time.get_ticks()

            coins += len(pygame.sprite.spritecollide(player, coins_group, True))
                
            if pygame.sprite.spritecollide(player, portals, False):
                current_floor += 1
                player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor(player)
                is_battle_locked, current_room_index, spawn_pending = False, -1, False
                # 每3关触发天赋选择 (第4, 7, 10...层刚进入时)
                if (current_floor - 1) % 3 == 0:
                    # 随机抽取3个天赋，由于天赋目前只有3个，就全展示，后续你可以往 all_talents 加更多
                    current_talents = random.sample(all_talents, min(3, len(all_talents)))
                    game_state = "TALENT"

        # ==========================
        # 游戏渲染层
        # ==========================
        if game_state in ["PLAYING", "SHOP", "TALENT", "GAMEOVER_ANIM", "GAMEOVER"]:
            screen.fill(BLACK)
            # 1. 视差地图渲染
            start_c, end_c = int(camera_x//TILE_SIZE), int((camera_x+SCREEN_WIDTH)//TILE_SIZE)+1
            start_r, end_r = int(camera_y//TILE_SIZE), int((camera_y+SCREEN_HEIGHT)//TILE_SIZE)+1
            for r in range(max(0, start_r), min(MAP_ROWS, end_r)):
                for c in range(max(0, start_c), min(MAP_COLS, end_c)):
                    val, draw_x, draw_y = game_map[r][c], c*TILE_SIZE - camera_x, r*TILE_SIZE - camera_y
                    if val == 0: screen.blit(wall_img, (draw_x, draw_y))
                    elif val == 1: screen.blit(floor_img, (draw_x, draw_y))
                    elif val == 2:
                        pygame.draw.rect(screen, (255,165,0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, RED, (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 2)

            for s in spawners:
                pygame.draw.circle(screen, RED, (s.x-camera_x, s.y-camera_y), 20, 2)

            for e in list(portals)+list(coins_group)+list(enemies)+list(bullets)+list(enemy_bullets):
                screen.blit(e.image, (e.rect.x-camera_x, e.rect.y-camera_y))
            for e in enemies: e.draw_hp(screen, camera_x, camera_y)
            
            # 画玩家（死亡时播放特殊状态）
            if game_state == "GAMEOVER_ANIM" or game_state == "GAMEOVER":
                player.update(0, 0, is_dead=True)
            screen.blit(player.image, (player.rect.x-camera_x, player.rect.y-camera_y))

            # UI 面板
            pygame.draw.rect(screen, GRAY, (20, 20, 150, 20))
            pygame.draw.rect(screen, RED, (20, 20, 150 * max(0, player.hp/player.max_hp), 20))
            screen.blit(font_base.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE), (30, 22))
            screen.blit(font_large.render(f"金币: {coins}", True, YELLOW), (20, 50))
            
            room_txt = font_large.render(room_info_text, True, room_info_color)
            screen.blit(room_txt, (SCREEN_WIDTH//2 - room_txt.get_width()//2, 20))

            if game_state == "PLAYING":
                pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
                pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

            # 各种弹窗渲染
            if game_state == "SHOP":
                shop_btns = draw_shop(screen, player, coins, shop_items, mx, my)
            elif game_state == "TALENT":
                talent_btns = draw_talent(screen, current_talents, mx, my)
            elif game_state == "GAMEOVER_ANIM":
                # 死亡特效停留3秒
                if pygame.time.get_ticks() - death_timer > 3000:
                    game_state = "GAMEOVER"
            elif game_state == "GAMEOVER":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(200); overlay.fill(BLACK)
                screen.blit(overlay, (0,0))
                screen.blit(font_title.render("你 死 了", True, RED), (SCREEN_WIDTH//2-90, 200))
                info = font_large.render(f"最终抵达层数: {current_floor} | 收集金币: {coins}", True, WHITE)
                screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 300))
                btn_restart = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 400, 200, 50, GRAY, WHITE, mx, my)
                btn_quit = draw_button(screen, "退出游戏", SCREEN_WIDTH//2-100, 480, 200, 50, RED, (255,100,100), mx, my)

        pygame.display.flip(); clock.tick(FPS)

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()