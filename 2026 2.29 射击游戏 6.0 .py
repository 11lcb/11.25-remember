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

# 屏幕与帧率
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("大型地图射击 - Pygame重制版")

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 68, 68)
GREEN = (144, 238, 144)
BLUE = (135, 206, 235)
DARK_GRAY = (34, 34, 34)
WALL_COLOR = (17, 17, 17)
GATE_COLOR = (255, 165, 0)

# 地图常量
TILE_SIZE = 60
MAP_COLS = 60
MAP_ROWS = 60
game_map = []
room_list = []

# 字体
font_base = pygame.font.SysFont("Arial", 16)
font_large = pygame.font.SysFont("Arial", 24, bold=True)
font_warn = pygame.font.SysFont("Arial", 40, bold=True)

# ==========================================
# 2. 辅助函数：安全加载动画帧
# ==========================================
def load_frames(image_paths, fallback_color, size):
    """如果找不到图片，生成纯色方块代替，防止崩溃"""
    frames = []
    for path in image_paths:
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    if not frames:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        # 画一个圆角矩形或圆形
        pygame.draw.circle(surface, fallback_color, (size[0]//2, size[1]//2), size[0]//2)
        frames.append(surface)
    return frames

# ==========================================
# 3. 游戏核心类 (精灵与动画)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 👉【需要替换的图片文件】玩家待机和跑动
        self.idle_frames = load_frames(["站立.jpg"], GREEN, (50, 50))
        self.run_frames = load_frames(["跑步1.jpg", "跑步2.jpg"], GREEN, (50, 50))
        
        self.frames = self.idle_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True

    def update(self, dx, dy):
        # 动画逻辑
        if dx != 0 or dy != 0:
            self.frames = self.run_frames
            if dx > 0: self.facing_right = True
            elif dx < 0: self.facing_right = False
        else:
            self.frames = self.idle_frames

        self.current_frame += 0.15
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
            
        self.image = self.frames[int(self.current_frame)]
        if  self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp):
        super().__init__()
        self.max_hp = hp
        self.hp = hp
        self.radius = 15
        
        # 👉【需要替换的图片文件】敌人跑动
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
            # 碰撞判断移动
            if not is_wall(self.rect.centerx + vx, self.rect.centery):
                self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy):
                self.rect.centery += vy
                
            # 朝向更新
            if vx > 0: self.facing_right = True
            elif vx < 0: self.facing_right = False

        # 动画更新
        self.current_frame += 0.1
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw_hp(self, surface, camera_x, camera_y):
        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y - camera_y - 10
        pygame.draw.rect(surface, BLACK, (draw_x, draw_y, 30, 5))
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, RED, (draw_x, draw_y, 30 * hp_ratio, 5))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, is_scatter=False):
        super().__init__()
        # 👉【需要替换的图片文件】子弹图片
        color = BLUE if is_scatter else WHITE
        self.frames = load_frames(["bullet.png"], color, (8, 8))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, itype):
        super().__init__()
        self.itype = itype
        colors = [(135, 206, 235), (221, 160, 221), (43, 155, 169)] # 蓝, 紫, 青
        # 👉【需要替换的图片文件】散弹、加速、瞬移道具图片
        paths = [["item_scatter.png"], ["item_speed.png"], ["item_teleport.png"]]
        
        self.frames = load_frames(paths[itype], colors[itype], (24, 24))
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.time_offset = random.random() * math.pi * 2

    def update(self):
        # 让道具上下浮动
        self.rect.centery = self.base_y + math.sin(pygame.time.get_ticks() / 200 + self.time_offset) * 5

class SpawnerWarning:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 60 # 60帧预警

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

def create_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= x < MAP_COLS and 0 <= y < MAP_ROWS:
            game_map[y][x] = 1; game_map[y+1][x] = 1

def create_v_tunnel(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= y < MAP_ROWS and 0 <= x < MAP_COLS:
            game_map[y][x] = 1; game_map[y][x+1] = 1

def generate_map():
    global game_map, room_list
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []

    for _ in range(25):
        w, h = random.randint(10, 16), random.randint(10, 16)
        x, y = random.randint(2, MAP_COLS - w - 2), random.randint(2, MAP_ROWS - h - 2)
        overlap = any(not (x + w + 3 < r.x or x > r.x + r.w + 3 or y + h + 3 < r.y or y > r.y + r.h + 3) for r in room_list)
        if not overlap:
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            room_list.append(Room(x, y, w, h, len(room_list) == 0))

    for i in range(1, len(room_list)):
        target = random.randint(0, i - 2) if i > 2 and random.random() < 0.2 else i - 1
        r1, r2 = room_list[i], room_list[target]
        if random.random() < 0.5:
            create_h_tunnel(r1.cx, r2.cx, r1.cy)
            create_v_tunnel(r1.cy, r2.cy, r2.cx)
        else:
            create_v_tunnel(r1.cy, r2.cy, r1.cx)
            create_h_tunnel(r1.cx, r2.cx, r2.cy)

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
# 5. 主程序与游戏循环
# ==========================================
def main():
    clock = pygame.time.Clock()
    
    # 全局状态变量
    score = 0
    speed_base = 7
    speed_user = speed_base
    
    buff_scatter = False
    buff_scatter_time = 0
    buff_speed = False
    buff_speed_time = 0
    teleport_count = 0

    is_battle_locked = False
    current_room_index = -1
    spawn_pending = False
    
    # 预先加载背景地砖图片
    # 👉【需要替换的图片文件】墙壁和地板
    wall_img = load_frames(["wall.png"], WALL_COLOR, (TILE_SIZE, TILE_SIZE))[0]
    floor_img = load_frames(["floor.png"], DARK_GRAY, (TILE_SIZE, TILE_SIZE))[0]

    def reset_game():
        nonlocal score, speed_user, buff_scatter, buff_speed, teleport_count, is_battle_locked, current_room_index, spawn_pending
        score = 0
        speed_user = speed_base
        buff_scatter = buff_speed = False
        teleport_count = 0
        is_battle_locked = spawn_pending = False
        current_room_index = -1
        
        sx, sy = generate_map()
        return Player(sx, sy), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), []

    player, bullets, enemies, items, spawners = reset_game()
    last_shoot_time = 0

    running = True
    while running:
        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                # 瞬移逻辑
                if event.key == pygame.K_LSHIFT and teleport_count > 0:
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = mx + camera_x, my + camera_y # 转为世界坐标
                    dx, dy = wx - player.rect.centerx, wy - player.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        nx = player.rect.centerx + (dx / dist) * 150
                        ny = player.rect.centery + (dy / dist) * 150
                        if not is_wall(nx, ny):
                            player.rect.centerx = nx
                            player.rect.centery = ny
                            teleport_count -= 1

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        # --- 玩家移动 ---
        dx, dy = 0, 0
        if keys[pygame.K_a]: dx -= speed_user
        if keys[pygame.K_d]: dx += speed_user
        if keys[pygame.K_w]: dy -= speed_user
        if keys[pygame.K_s]: dy += speed_user

        # 碰撞检测（类似原来Tkinter的简化逻辑）
        if dx != 0 and not is_wall(player.rect.centerx + dx + (15 if dx>0 else -15), player.rect.centery):
            player.rect.centerx += dx
        if dy != 0 and not is_wall(player.rect.centerx, player.rect.centery + dy + (15 if dy>0 else -15)):
            player.rect.centery += dy
            
        player.update(dx, dy)

        # --- 相机更新 ---
        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_y = player.rect.centery - SCREEN_HEIGHT // 2

        # --- 射击逻辑 ---
        if mouse_pressed[0] and pygame.time.get_ticks() - last_shoot_time > 150:
            mx, my = pygame.mouse.get_pos()
            wx, wy = mx + camera_x, my + camera_y
            angle = math.atan2(wy - player.rect.centery, wx - player.rect.centerx)
            
            bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle, False))
            if buff_scatter:
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle - 0.2, True))
                bullets.add(Bullet(player.rect.centerx, player.rect.centery, angle + 0.2, True))
            last_shoot_time = pygame.time.get_ticks()

        # --- 房间战斗触发逻辑 ---
        room_info_text = "安全区域"
        room_info_color = GREEN
        
        for i, room in enumerate(room_list):
            if room.is_player_inside(player.rect.centerx, player.rect.centery):
                if not room.cleared and not is_battle_locked:
                    current_room_index = i
                    is_battle_locked = True
                    spawn_pending = True
                    toggle_room_gates(room, close=True)
                    
                    # 生成预警点
                    attempts = 0
                    spawned = 0
                    while spawned < room.enemy_count and attempts < 100:
                        rx = random.randint(room.x + 1, room.x + room.w - 2) * TILE_SIZE + TILE_SIZE//2
                        ry = random.randint(room.y + 1, room.y + room.h - 2) * TILE_SIZE + TILE_SIZE//2
                        if not is_wall(rx, ry) and math.hypot(rx - player.rect.centerx, ry - player.rect.centery) > 250:
                            spawners.append(SpawnerWarning(rx, ry))
                            spawned += 1
                        attempts += 1
                        
                    # 生成道具
                    for _ in range(random.randint(1, 2)):
                        rx = random.randint(room.x + 2, room.x + room.w - 3) * TILE_SIZE + TILE_SIZE//2
                        ry = random.randint(room.y + 2, room.y + room.h - 3) * TILE_SIZE + TILE_SIZE//2
                        if not is_wall(rx, ry):
                            itype = random.choices([0, 1, 2], weights=[60, 20, 20])[0]
                            items.add(Item(rx, ry, itype))
                break

        # --- 战斗状态机 ---
        if is_battle_locked:
            room_info_text = "警告：敌人接近中！" if spawn_pending else "战斗开始！"
            room_info_color = (255, 165, 0) if spawn_pending else RED
            
            # 处理预警生成敌人
            for s in spawners[:]:
                s.timer -= 1
                if s.timer <= 0:
                    hp = 40 + score * 1.5
                    enemies.add(Enemy(s.x, s.y, hp))
                    spawners.remove(s)
            
            if len(spawners) == 0: spawn_pending = False
            
            # 战斗结束判断
            if not spawn_pending and len(enemies) == 0:
                room_list[current_room_index].cleared = True
                is_battle_locked = False
                toggle_room_gates(room_list[current_room_index], close=False)
                if all(r.cleared for r in room_list):
                    room_info_text, room_info_color = "全图通关！", (255, 215, 0)

        # --- 更新精灵 ---
        bullets.update()
        for b in bullets:
            if is_wall(b.rect.centerx, b.rect.centery): b.kill()
            
        enemies.update(player.rect.centerx, player.rect.centery)
        items.update()

        # 碰撞: 子弹打敌人
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            enemy.hp -= 15 * len(bullet_list)
            if enemy.hp <= 0:
                enemy.kill()
                score += 10
                
        # 碰撞: 敌人碰到玩家 (重新开始)
        if pygame.sprite.spritecollideany(player, enemies):
            player, bullets, enemies, items, spawners = reset_game()
            continue

        # 碰撞: 玩家吃道具
        collected = pygame.sprite.spritecollide(player, items, True)
        for item in collected:
            if item.itype == 0: buff_scatter = True; buff_scatter_time = 300
            elif item.itype == 1: buff_speed = True; buff_speed_time = 300; speed_user = 11
            elif item.itype == 2: teleport_count += 1

        # 更新 Buff 时间
        buff_str = ""
        if buff_scatter:
            buff_scatter_time -= 1
            buff_str += f"散弹: {buff_scatter_time//60}s "
            if buff_scatter_time <= 0: buff_scatter = False
        if buff_speed:
            buff_speed_time -= 1
            buff_str += f"加速: {buff_speed_time//60}s "
            if buff_speed_time <= 0: buff_speed = False; speed_user = speed_base
        if teleport_count > 0: buff_str += f"瞬移: {teleport_count}"

        # ==========================================
        # 渲染阶段 (Drawing)
        # ==========================================
        screen.fill(BLACK)

        # 1. 画地图 (根据相机视野裁剪)
        start_c, end_c = int(camera_x // TILE_SIZE), int((camera_x + SCREEN_WIDTH) // TILE_SIZE) + 1
        start_r, end_r = int(camera_y // TILE_SIZE), int((camera_y + SCREEN_HEIGHT) // TILE_SIZE) + 1
        for r in range(max(0, start_r), min(MAP_ROWS, end_r)):
            for c in range(max(0, start_c), min(MAP_COLS, end_c)):
                tile_val = game_map[r][c]
                draw_x, draw_y = c * TILE_SIZE - camera_x, r * TILE_SIZE - camera_y
                if tile_val == 0:
                    screen.blit(wall_img, (draw_x, draw_y))
                elif tile_val == 1:
                    screen.blit(floor_img, (draw_x, draw_y))
                elif tile_val == 2:
                    pygame.draw.rect(screen, GATE_COLOR, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, RED, (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 2)

        # 2. 画预警阵
        for s in spawners:
            draw_x, draw_y = s.x - camera_x, s.y - camera_y
            pygame.draw.circle(screen, RED, (int(draw_x), int(draw_y)), 20, 2)
            warn_txt = font_warn.render("!", True, RED)
            screen.blit(warn_txt, warn_txt.get_rect(center=(draw_x, draw_y)))

        # 3. 画精灵 (加上相机偏移)
        for entity in list(items) + list(enemies) + list(bullets) + [player]:
            screen.blit(entity.image, (entity.rect.x - camera_x, entity.rect.y - camera_y))
        
        # 4. 画血条
        for e in enemies: e.draw_hp(screen, camera_x, camera_y)

        # 5. 画十字准星 (代替系统鼠标)
        pygame.mouse.set_visible(False)
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
        pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

        # 6. UI & 小地图
        # 顶部背景条
        pygame.draw.rect(screen, (34, 34, 34), (0, 0, SCREEN_WIDTH, 40))
        # 提示文字
        info_txt = font_base.render("进房锁门 -> 杀敌+捡道具 | 蓝:散弹 紫:加速 青:瞬移 | WASD移动 鼠标射击 Shift瞬移", True, WHITE)
        screen.blit(info_txt, (10, 10))
        # 分数
        score_txt = font_large.render(f"分数: {score}", True, (255, 255, 0))
        screen.blit(score_txt, (SCREEN_WIDTH - 120, 10))
        # 房间状态
        room_txt = font_large.render(room_info_text, True, room_info_color)
        screen.blit(room_txt, (SCREEN_WIDTH//2 - room_txt.get_width()//2, 50))
        # Buff状态
        if buff_str:
            buff_txt = font_large.render(buff_str, True, (0, 255, 255))
            screen.blit(buff_txt, (20, SCREEN_HEIGHT - 40))

        # 绘制小地图 (缩放比例)
        minimap_scale = 2.5
        minimap_surf = pygame.Surface((MAP_COLS * minimap_scale, MAP_ROWS * minimap_scale))
        minimap_surf.fill(BLACK)
        for r in range(MAP_ROWS):
            for c in range(MAP_COLS):
                if game_map[r][c] == 1:
                    pygame.draw.rect(minimap_surf, (85, 85, 85), (c * minimap_scale, r * minimap_scale, minimap_scale, minimap_scale))
        # 小地图玩家位置
        px_mini = (player.rect.centerx / TILE_SIZE) * minimap_scale
        py_mini = (player.rect.centery / TILE_SIZE) * minimap_scale
        pygame.draw.circle(minimap_surf, RED, (int(px_mini), int(py_mini)), 2)
        
        # 将小地图画在左上角
        screen.blit(minimap_surf, (10, 50))
        pygame.draw.rect(screen, (100, 100, 100), (10, 50, minimap_surf.get_width(), minimap_surf.get_height()), 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()