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

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("无尽肉鸽射击 - Pygame重制版")

# 颜色
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
RED, GREEN, BLUE = (255, 68, 68), (144, 238, 144), (135, 206, 235)
YELLOW, PURPLE, GRAY = (255, 215, 0), (138, 43, 226), (100, 100, 100)

TILE_SIZE = 60
MAP_COLS, MAP_ROWS = 60, 60
game_map = []
room_list = []

font_base = pygame.font.SysFont("SimHei", 18) # 换成支持中文的字体，如果没有SimHei会自动退化
font_large = pygame.font.SysFont("SimHei", 24, bold=True)
font_title = pygame.font.SysFont("SimHei", 40, bold=True)

# ==========================================
# 2. 辅助函数
# ==========================================
def load_frames(image_paths, fallback_color, size):
    frames = []
    for path in image_paths:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    if not frames:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surface, fallback_color, (size[0]//2, size[1]//2), min(size)//2)
        frames.append(surface)
    return frames

# ==========================================
# 3. 游戏核心类 (Sprites)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.idle_frames = load_frames(["站立.jpg"], GREEN, (40, 40))
        self.run_frames = load_frames(["跑步1.jpg", "跑步2.jpg"], GREEN, (40, 40))
        
        self.frames = self.idle_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        
        # --- 新增：角色属性 ---
        self.max_hp = 5
        self.hp = 5
        self.invincible_timer = 0  # 受击无敌时间
        
        # 成长属性 (可通过商店升级)
        self.speed = 6
        self.bullet_damage = 15
        self.scatter_level = 0 # 0:单发, 1:三向, 2:五向

    def update(self, dx, dy):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        if dx != 0 or dy != 0:
            self.frames = self.run_frames
            if dx > 0: self.facing_right = True
            elif dx < 0: self.facing_right = False
        else:
            self.frames = self.idle_frames

        self.current_frame += 0.15
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            
        self.image = self.frames[int(self.current_frame)].copy()
        
        # 受击闪烁效果
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0:
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(255)
            
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp):
        super().__init__()
        self.max_hp = hp
        self.hp = hp
        self.frames = load_frames(["enemy_run1.png", "enemy_run2.png"], RED, (30, 30))
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True

    def update(self, px, py):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            vx, vy = (dx / dist) * 2.5, (dy / dist) * 2.5
            if not is_wall(self.rect.centerx + vx, self.rect.centery):
                self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy):
                self.rect.centery += vy
                
            if vx > 0: self.facing_right = True
            elif vx < 0: self.facing_right = False

        self.current_frame += 0.1
        if self.current_frame >= len(self.frames): self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)

    def draw_hp(self, surface, camera_x, camera_y):
        draw_x, draw_y = self.rect.x - camera_x, self.rect.y - camera_y - 10
        pygame.draw.rect(surface, BLACK, (draw_x, draw_y, 30, 5))
        pygame.draw.rect(surface, RED, (draw_x, draw_y, 30 * max(0, self.hp / self.max_hp), 5))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__()
        self.frames = load_frames(["bullet.png"], WHITE, (8, 8))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = damage
        speed = 15
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

# --- 新增：金币类 ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 👉【需要替换的图片文件】金币贴图
        self.frames = load_frames(["coin.png"], YELLOW, (20, 20))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.time_offset = random.random() * math.pi * 2

    def update(self):
        # 原地悬浮动画
        self.rect.centery = self.base_y + math.sin(pygame.time.get_ticks() / 150 + self.time_offset) * 5

# --- 新增：下一层传送门 ---
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 👉【需要替换的图片文件】传送门贴图
        self.frames = load_frames(["portal.png"], PURPLE, (50, 50))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0

    def update(self):
        # 旋转动画（如果没有真实图片，这里只是让图层旋转）
        self.angle = (self.angle + 2) % 360
        self.image = pygame.transform.rotate(self.frames[0], self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class SpawnerWarning:
    def __init__(self, x, y):
        self.x, self.y, self.timer = x, y, 60

# ==========================================
# 4. 地图生成与逻辑
# ==========================================
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

def create_tunnel(r1, r2, is_h):
    if is_h:
        for x in range(min(r1, r2), max(r1, r2) + 1):
            if 0 <= x < MAP_COLS: game_map[r1][x] = game_map[r1+1][x] = 1
    else:
        for y in range(min(r1, r2), max(r1, r2) + 1):
            if 0 <= y < MAP_ROWS: game_map[y][r1] = game_map[y][r1+1] = 1

def generate_map():
    global game_map, room_list
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []
    for _ in range(20):
        w, h = random.randint(10, 16), random.randint(10, 16)
        x, y = random.randint(2, MAP_COLS - w - 2), random.randint(2, MAP_ROWS - h - 2)
        if not any(not (x + w + 3 < r.x or x > r.x + r.w + 3 or y + h + 3 < r.y or y > r.y + r.h + 3) for r in room_list):
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            room_list.append(Room(x, y, w, h, len(room_list) == 0))

    for i in range(1, len(room_list)):
        target = random.randint(0, i - 2) if i > 2 and random.random() < 0.2 else i - 1
        r1, r2 = room_list[i], room_list[target]
        if random.random() < 0.5:
            for x in range(min(r1.cx, r2.cx), max(r1.cx, r2.cx) + 1): game_map[r1.cy][x] = game_map[r1.cy+1][x] = 1
            for y in range(min(r1.cy, r2.cy), max(r1.cy, r2.cy) + 1): game_map[y][r2.cx] = game_map[y][r2.cx+1] = 1
        else:
            for y in range(min(r1.cy, r2.cy), max(r1.cy, r2.cy) + 1): game_map[y][r1.cx] = game_map[y][r1.cx+1] = 1
            for x in range(min(r1.cx, r2.cx), max(r1.cx, r2.cx) + 1): game_map[r2.cy][x] = game_map[r2.cy+1][x] = 1

    return room_list[0].cx * TILE_SIZE, room_list[0].cy * TILE_SIZE

def is_wall(x, y):
    c, r = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if r < 0 or r >= MAP_ROWS or c < 0 or c >= MAP_COLS: return True
    return game_map[r][c] == 0 or game_map[r][c] == 2

def toggle_room_gates(room, close=True):
    if close:
        room.gates_coords = []
        for c in range(room.x, room.x + room.w):
            if game_map[room.y - 1][c] == 1: room.gates_coords.append((room.y - 1, c))
            if game_map[room.y + room.h][c] == 1: room.gates_coords.append((room.y + room.h, c))
        for r in range(room.y, room.y + room.h):
            if game_map[r][room.x - 1] == 1: room.gates_coords.append((r, room.x - 1))
            if game_map[r][room.x + room.w] == 1: room.gates_coords.append((r, room.x + room.w))
        for r, c in room.gates_coords: game_map[r][c] = 2
    else:
        for r, c in room.gates_coords: game_map[r][c] = 1

# ==========================================
# 5. 商店系统 UI
# ==========================================
def draw_shop(screen, player, coins, shop_items):
    # 画一个半透明的黑色遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # 商店主面板
    panel_w, panel_h = 500, 400
    px, py = (SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2
    pygame.draw.rect(screen, (40, 40, 40), (px, py, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(screen, YELLOW, (px, py, panel_w, panel_h), 3, border_radius=10)

    title = font_title.render("—— 神 秘 商 店 ——", True, YELLOW)
    screen.blit(title, (px + panel_w//2 - title.get_width()//2, py + 20))
    
    coin_txt = font_large.render(f"持有金币: {coins}", True, WHITE)
    screen.blit(coin_txt, (px + 20, py + 70))

    buttons = [] # 记录按钮区域用于点击检测
    start_y = py + 120
    for i, item in enumerate(shop_items):
        y = start_y + i * 60
        # 物品名字与当前等级
        name_color = GRAY if item['level'] >= item['max'] else WHITE
        lvl_txt = f"(Max)" if item['level'] >= item['max'] else f"(Lv.{item['level']})"
        text = font_large.render(f"{item['name']} {lvl_txt}", True, name_color)
        screen.blit(text, (px + 30, y + 10))
        
        # 购买按钮
        btn_rect = pygame.Rect(px + panel_w - 150, y, 120, 40)
        btn_color = GREEN if coins >= item['cost'] and item['level'] < item['max'] else GRAY
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=5)
        
        cost_txt = font_base.render(f"${item['cost']}", True, BLACK)
        screen.blit(cost_txt, (btn_rect.x + 60 - cost_txt.get_width()//2, btn_rect.y + 10))
        
        buttons.append((btn_rect, item))

    tip = font_base.render("按 TAB 键或点击外部关闭商店", True, GRAY)
    screen.blit(tip, (px + panel_w//2 - tip.get_width()//2, py + panel_h - 30))
    
    return buttons

# ==========================================
# 6. 主程序与游戏循环
# ==========================================
def main():
    clock = pygame.time.Clock()
    
    wall_img = load_frames(["wall.png"], (17, 17, 17), (TILE_SIZE, TILE_SIZE))[0]
    floor_img = load_frames(["floor.png"], (34, 34, 34), (TILE_SIZE, TILE_SIZE))[0]

    # 全局游戏数据
    coins = 0
    current_floor = 1
    game_state = "PLAYING" # PLAYING, SHOP, GAMEOVER
    
    # 商店商品数据
    shop_items = [
        {"id": "dmg", "name": "提升攻击力", "cost": 10, "level": 0, "max": 10, "cost_up": 5},
        {"id": "spd", "name": "提升移动速度", "cost": 15, "level": 0, "max": 5, "cost_up": 10},
        {"id": "sct", "name": "多重射击(增加弹道)", "cost": 30, "level": 0, "max": 2, "cost_up": 30},
        {"id": "hp", "name": "恢复1点生命", "cost": 10, "level": 0, "max": 999, "cost_up": 0} # 不设上限
    ]

    def reset_floor(player_instance=None):
        sx, sy = generate_map()
        if player_instance is None:
            p = Player(sx, sy)
        else:
            p = player_instance
            p.rect.center = (sx, sy)
        return p, pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), [], False

    # 首次初始化
    player, bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor()
    last_shoot_time = 0
    is_battle_locked, current_room_index, spawn_pending = False, -1, False

    running = True
    while running:
        # ==========================
        # 事件处理
        # ==========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                # 呼出/关闭商店
                if event.key == pygame.K_TAB and game_state != "GAMEOVER":
                    game_state = "SHOP" if game_state == "PLAYING" else "PLAYING"
                # 死亡后按 R 重启
                if event.key == pygame.K_r and game_state == "GAMEOVER":
                    coins, current_floor = 0, 1
                    for item in shop_items: item['level'] = 0 # 重置商店
                    shop_items[0]['cost'], shop_items[1]['cost'], shop_items[2]['cost'] = 10, 15, 30
                    player, bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor()
                    game_state = "PLAYING"

            # 商店鼠标点击检测
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == "SHOP":
                mx, my = pygame.mouse.get_pos()
                clicked_btn = False
                for btn_rect, item in shop_buttons:
                    if btn_rect.collidepoint(mx, my):
                        clicked_btn = True
                        if coins >= item['cost'] and item['level'] < item['max']:
                            coins -= item['cost']
                            item['level'] += 1
                            item['cost'] += item['cost_up']
                            # 应用属性
                            if item['id'] == 'dmg': player.bullet_damage += 5
                            elif item['id'] == 'spd': player.speed += 1
                            elif item['id'] == 'sct': player.scatter_level += 1
                            elif item['id'] == 'hp': 
                                player.hp = min(player.max_hp, player.hp + 1)
                                item['level'] -= 1 # 回血不记最大等级
                # 点击外部关闭商店
                if not clicked_btn:
                    panel_rect = pygame.Rect((SCREEN_WIDTH-500)//2, (SCREEN_HEIGHT-400)//2, 500, 400)
                    if not panel_rect.collidepoint(mx, my):
                        game_state = "PLAYING"

        if game_state == "GAMEOVER" or game_state == "SHOP":
            # 暂停游戏逻辑，只渲染
            pass
        else:
            # ==========================
            # 游戏主逻辑 (PLAYING)
            # ==========================
            keys = pygame.key.get_pressed()
            mouse_pressed = pygame.mouse.get_pressed()

            # --- 玩家移动 ---
            dx, dy = 0, 0
            if keys[pygame.K_a]: dx -= player.speed
            if keys[pygame.K_d]: dx += player.speed
            if keys[pygame.K_w]: dy -= player.speed
            if keys[pygame.K_s]: dy += player.speed

            if dx != 0 and not is_wall(player.rect.centerx + dx + (15 if dx>0 else -15), player.rect.centery):
                player.rect.centerx += dx
            if dy != 0 and not is_wall(player.rect.centerx, player.rect.centery + dy + (15 if dy>0 else -15)):
                player.rect.centery += dy
                
            player.update(dx, dy)

            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2

            # --- 射击 ---
            if mouse_pressed[0] and pygame.time.get_ticks() - last_shoot_time > 200:
                mx, my = pygame.mouse.get_pos()
                wx, wy = mx + camera_x, my + camera_y
                angle = math.atan2(wy - player.rect.centery, wx - player.rect.centerx)
                
                # 根据散弹等级发射不同数量子弹
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle, player.bullet_damage))
                if player.scatter_level >= 1:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle - 0.2, player.bullet_damage))
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle + 0.2, player.bullet_damage))
                if player.scatter_level >= 2:
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle - 0.4, player.bullet_damage))
                    bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle + 0.4, player.bullet_damage))
                    
                last_shoot_time = pygame.time.get_ticks()

            # --- 房间战斗触发 ---
            room_info_text = f"第 {current_floor} 层 - 安全区域"
            room_info_color = GREEN
            
            for i, room in enumerate(room_list):
                if room.is_player_inside(player.rect.centerx, player.rect.centery):
                    if not room.cleared and not is_battle_locked:
                        current_room_index = i
                        is_battle_locked, spawn_pending = True, True
                        toggle_room_gates(room, close=True)
                        
                        room.enemy_count += current_floor # 随层数增加敌人数量
                        spawned = 0
                        while spawned < room.enemy_count:
                            rx = random.randint(room.x + 1, room.x + room.w - 2) * TILE_SIZE + TILE_SIZE//2
                            ry = random.randint(room.y + 1, room.y + room.h - 2) * TILE_SIZE + TILE_SIZE//2
                            if not is_wall(rx, ry) and math.hypot(rx - player.rect.centerx, ry - player.rect.centery) > 250:
                                spawners.append(SpawnerWarning(rx, ry))
                                spawned += 1
                    break

            # --- 战斗状态机 ---
            if is_battle_locked:
                room_info_text = "警告：敌人接近中！" if spawn_pending else "战斗中！"
                room_info_color = (255, 165, 0) if spawn_pending else RED
                
                for s in spawners[:]:
                    s.timer -= 1
                    if s.timer <= 0:
                        # 随层数增加敌人血量
                        hp = 30 + (current_floor * 15)
                        enemies.add(Enemy(s.x, s.y, hp))
                        spawners.remove(s)
                
                if len(spawners) == 0: spawn_pending = False
                
                # 战斗结束，房门打开
                if not spawn_pending and len(enemies) == 0:
                    room_list[current_room_index].cleared = True
                    is_battle_locked = False
                    toggle_room_gates(room_list[current_room_index], close=False)
                    
            # 检查是否清空了全图 -> 生成传送门
            if all(r.cleared for r in room_list) and not portal_spawned:
                # 在最后一个房间正中心生成传送门
                last_r = room_list[current_room_index]
                portals.add(Portal(last_r.cx * TILE_SIZE, last_r.cy * TILE_SIZE))
                portal_spawned = True
                
            if portal_spawned:
                room_info_text, room_info_color = "寻找传送门进入下一层", PURPLE

            # --- 各种更新与碰撞 ---
            bullets.update()
            for b in bullets:
                if is_wall(b.rect.centerx, b.rect.centery): b.kill()
                
            enemies.update(player.rect.centerx, player.rect.centery)
            coins_group.update()
            portals.update()

            # 子弹打敌人
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for b in bullet_list: enemy.hp -= b.damage
                if enemy.hp <= 0:
                    enemy.kill()
                    # 必定掉落1个金币，有概率掉多个
                    coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    if random.random() < 0.3:
                        coins_group.add(Coin(enemy.rect.centerx + 10, enemy.rect.centery + 10))
                    
            # 敌人碰玩家 (扣血逻辑)
            if player.invincible_timer <= 0:
                hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
                if hit_enemies:
                    player.hp -= 1
                    player.invincible_timer = 60 # 60帧(1秒)无敌时间
                    if player.hp <= 0:
                        game_state = "GAMEOVER"

            # 玩家捡金币
            collected = pygame.sprite.spritecollide(player, coins_group, True)
            for c in collected:
                coins += 1
                
            # 玩家进传送门
            if pygame.sprite.spritecollide(player, portals, False):
                current_floor += 1
                # 保留玩家数据，重置地图
                _, bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor(player)
                is_battle_locked, current_room_index, spawn_pending = False, -1, False

        # ==========================
        # 渲染阶段 (Drawing)
        # ==========================
        screen.fill(BLACK)

        # 1. 画地图
        start_c, end_c = int(camera_x // TILE_SIZE), int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1
        start_r, end_r = int(camera_y // TILE_SIZE), int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1
        for r in range(max(0, start_r), min(MAP_ROWS, end_r)):
            for c in range(max(0, start_c), min(MAP_COLS, end_c)):
                tile_val = game_map[r][c]
                draw_x, draw_y = c * TILE_SIZE - camera_x, r * TILE_SIZE - camera_y
                if tile_val == 0: screen.blit(wall_img, (draw_x, draw_y))
                elif tile_val == 1: screen.blit(floor_img, (draw_x, draw_y))
                elif tile_val == 2:
                    pygame.draw.rect(screen, (255, 165, 0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, RED, (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 2)

        # 2. 画阵法
        for s in spawners:
            draw_x, draw_y = s.x - camera_x, s.y - camera_y
            pygame.draw.circle(screen, RED, (int(draw_x), int(draw_y)), 20, 2)
            warn_txt = font_title.render("!", True, RED)
            screen.blit(warn_txt, warn_txt.get_rect(center=(draw_x, draw_y)))

        # 3. 画精灵
        for entity in list(portals) + list(coins_group) + list(enemies) + list(bullets) + [player]:
            screen.blit(entity.image, (entity.rect.x - camera_x, entity.rect.y - camera_y))
        
        for e in enemies: e.draw_hp(screen, camera_x, camera_y)

        # 4. 画十字准星
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
        pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

        # ==========================
        # 界面 UI
        # ==========================
        # 顶部提示栏
        if game_state != "GAMEOVER":
            room_txt = font_large.render(room_info_text, True, room_info_color)
            screen.blit(room_txt, (SCREEN_WIDTH//2 - room_txt.get_width()//2, 20))

        # 【左上角】：生命值和金币
        ui_bg = pygame.Surface((200, 80))
        ui_bg.set_alpha(150)
        ui_bg.fill(BLACK)
        screen.blit(ui_bg, (10, 10))
        
        # 画血条
        pygame.draw.rect(screen, GRAY, (20, 20, 150, 20))
        hp_ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(screen, RED, (20, 20, 150 * hp_ratio, 20))
        pygame.draw.rect(screen, WHITE, (20, 20, 150, 20), 2)
        hp_txt = font_base.render(f"HP: {player.hp}/{player.max_hp}", True, WHITE)
        screen.blit(hp_txt, (30, 22))
        
        # 画金币数
        coin_txt = font_large.render(f"金币: {coins}", True, YELLOW)
        screen.blit(coin_txt, (20, 50))

        # 【右上角】：小地图 & 商店提示
        minimap_scale = 2.5
        minimap_surf = pygame.Surface((MAP_COLS * minimap_scale, MAP_ROWS * minimap_scale))
        minimap_surf.set_alpha(200)
        minimap_surf.fill(BLACK)
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if game_map[r][c] == 1:
                    pygame.draw.rect(minimap_surf, (85, 85, 85), (c * minimap_scale, r * minimap_scale, minimap_scale, minimap_scale))
        px_mini, py_mini = (player.rect.centerx / TILE_SIZE) * minimap_scale, (player.rect.centery / TILE_SIZE) * minimap_scale
        pygame.draw.circle(minimap_surf, RED, (int(px_mini), int(py_mini)), 2)
        
        map_x = SCREEN_WIDTH - minimap_surf.get_width() - 10
        screen.blit(minimap_surf, (map_x, 10))
        pygame.draw.rect(screen, (100, 100, 100), (map_x, 10, minimap_surf.get_width(), minimap_surf.get_height()), 2)
        
        shop_txt = font_base.render("[TAB] 开启商店", True, YELLOW)
        screen.blit(shop_txt, (map_x + minimap_surf.get_width()//2 - shop_txt.get_width()//2, 10 + minimap_surf.get_height() + 10))

        # ==========================
        # 弹窗覆盖层 (商店 / 死亡)
        # ==========================
        shop_buttons = []
        if game_state == "SHOP":
            pygame.mouse.set_visible(True) # 显示鼠标以供点击
            shop_buttons = draw_shop(screen, player, coins, shop_items)
            
        elif game_state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            go_txt = font_title.render("你 死 了", True, RED)
            screen.blit(go_txt, (SCREEN_WIDTH//2 - go_txt.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            info_txt = font_large.render(f"最终抵达层数: {current_floor} | 收集金币: {coins}", True, WHITE)
            screen.blit(info_txt, (SCREEN_WIDTH//2 - info_txt.get_width()//2, SCREEN_HEIGHT//2 + 20))
            
            restart_txt = font_large.render("按 [R] 键重新开始", True, GRAY)
            screen.blit(restart_txt, (SCREEN_WIDTH//2 - restart_txt.get_width()//2, SCREEN_HEIGHT//2 + 80))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()