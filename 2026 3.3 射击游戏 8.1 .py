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

# 难度倍率（强化敌人强度曲线）
difficulty_mult = {"hp": 1.0, "dmg": 1, "spd": 1.0, "range_hp": 1.0, "range_spd": 1.0}

# 全局Debuff状态
debuffs = {
    "vision_reduce": 0,       # 视野减少剩余时间
    "buff_disable": 0,        # 增益失效剩余时间
    "last_shield_hit": 0      # 上次护盾受击时间
}

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
        self.death_frames = load_frames(["player_death.png"], GRAY, (40, 40), "cross")
        
        self.frames = self.idle_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        
        # 基础属性
        self.max_hp = 5
        self.hp = 5
        self.invincible_timer = 0
        self.speed = 6
        
        # 护盾系统
        self.max_shield = 2          # 初始护盾上限
        self.shield = self.max_shield  # 当前护盾值
        self.shield_recovery_rate = 0.2  # 护盾恢复速度
        self.last_shield_damage = 0   # 上次护盾受损时间
        
        # 武器系统
        self.weapon_slots = 2        # 默认武器栏数量
        self.current_weapon = 0      # 当前选中武器索引
        self.weapons = [
            {"type": "pistol", "name": "普通手枪", "damage": 15, "cd": 300, "scatter_level": 0},
            {"type": "melee", "name": "近战小刀", "damage": 30, "range": 40, "cd": 500}
        ]
        
        # 天赋相关
        self.has_bounce = False
        self.has_magnet = False
        self.has_explosion = False   # 敌人爆炸天赋
        self.explosion_damage = 20   # 基础爆炸伤害
        self.explosion_radius = 50   # 爆炸范围
        
        # 射击冷却
        self.last_shoot_time = 0

    def update(self, dx, dy, is_dead=False):
        if is_dead:
            self.image = self.death_frames[0]
            return

        # 护盾恢复逻辑（被攻击5秒后开始恢复）
        current_time = pygame.time.get_ticks()
        if self.shield < self.max_shield and current_time - self.last_shield_damage > 5000:
            self.shield = min(self.max_shield, self.shield + self.shield_recovery_rate)

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

    def take_damage(self, damage):
        """处理伤害计算，优先消耗护盾"""
        self.last_shield_damage = pygame.time.get_ticks()
        if self.shield > 0:
            damage_taken = min(self.shield, damage)
            self.shield -= damage_taken
            remaining_damage = damage - damage_taken
            if remaining_damage > 0:
                self.hp -= remaining_damage
                self.invincible_timer = 60
        else:
            self.hp -= damage
            self.invincible_timer = 60
        
        return self.hp <= 0

    def switch_weapon(self, direction):
        """切换武器（1切换下一把，-1切换上一把）"""
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)

    def attack(self, mx, my, camera_x, camera_y, bullets_group, enemy_bullets_group):
        """统一攻击逻辑"""
        current_time = pygame.time.get_ticks()
        weapon = self.weapons[self.current_weapon]
        
        # 检查冷却
        if current_time - self.last_shoot_time < weapon["cd"]:
            return
            
        self.last_shoot_time = current_time
        
        # 远程武器攻击
        if weapon["type"] == "pistol":
            wx, wy = mx + camera_x, my + camera_y
            angle = math.atan2(wy - self.rect.centery, wx - self.rect.centerx)
            
            # 基础子弹
            bullets_group.add(Bullet(
                self.rect.centerx, self.rect.centery, angle, 
                weapon["damage"], self
            ))
            
            # 散射逻辑
            if weapon["scatter_level"] >= 1:
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle-0.2, weapon["damage"], self))
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle+0.2, weapon["damage"], self))
            if weapon["scatter_level"] >= 2:
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle-0.4, weapon["damage"], self))
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle+0.4, weapon["damage"], self))
        
        # 近战武器攻击（清除弹幕+伤害敌人）
        elif weapon["type"] == "melee":
            # 计算攻击范围
            attack_rect = pygame.Rect(
                self.rect.centerx - weapon["range"],
                self.rect.centery - weapon["range"],
                weapon["range"] * 2,
                weapon["range"] * 2
            )
            
            # 清除敌人弹幕
            for bullet in enemy_bullets_group:
                if attack_rect.colliderect(bullet.rect):
                    bullet.kill()
            
            # 伤害范围内敌人
            return attack_rect

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, floor):
        super().__init__()
        self.max_hp = hp * difficulty_mult["hp"] * (1 + floor * 0.15)  # 强化血量成长
        self.hp = self.max_hp
        self.speed = 2.0 + (floor * 0.2) * difficulty_mult["spd"]     # 强化速度成长
        self.damage = 1 * difficulty_mult["dmg"] * (1 + floor * 0.1)  # 强化伤害成长
        self.frames = load_frames(["enemy_run.png"], RED, (30, 30), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.is_exploded = False  # 防止重复爆炸

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

    def explode(self, enemies_group, player):
        """敌人爆炸逻辑"""
        if self.is_exploded or not player.has_explosion:
            return
            
        self.is_exploded = True
        # 计算爆炸范围内的敌人
        explosion_rect = pygame.Rect(
            self.rect.centerx - player.explosion_radius,
            self.rect.centery - player.explosion_radius,
            player.explosion_radius * 2,
            player.explosion_radius * 2
        )
        
        # 对范围内敌人造成伤害
        for enemy in enemies_group:
            if enemy != self and explosion_rect.colliderect(enemy.rect):
                enemy.hp -= player.explosion_damage

# 远程敌人类
class RangedEnemy(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 0.6, floor)  # 血量只有普通敌人的60%
        self.max_hp = hp * difficulty_mult["range_hp"] * (1 + floor * 0.2)
        self.hp = self.max_hp
        self.speed = 1.5 + (floor * 0.15) * difficulty_mult["range_spd"]  # 移动速度稍慢
        self.frames = load_frames(["ranged_enemy.png"], BLUE, (25, 25), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        # 远程攻击属性
        self.attack_range = 400  # 攻击范围
        self.attack_cd = max(80, 150 - floor * 5)  # 攻击冷却，随层数缩短
        self.attack_timer = 0
        self.is_attacking = False  # 攻击时无法移动

    def update(self, px, py, enemy_bullets_group=None):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        
        # 攻击逻辑
        self.attack_timer += 1
        if dist < self.attack_range and self.attack_timer >= self.attack_cd:
            self.is_attacking = True
            self.attack_timer = 0
            # 发射子弹
            if enemy_bullets_group:
                angle = math.atan2(dy, dx)
                enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle, speed=5))
        else:
            self.is_attacking = False
        
        # 移动逻辑（攻击时无法移动）
        if not self.is_attacking and dist > 50:
            vx, vy = (dx / dist) * self.speed, (dy / dist) * self.speed
            if not is_wall(self.rect.centerx + vx, self.rect.centery): self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy): self.rect.centery += vy

# BOSS类（强化版）
class Boss(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 5, floor)  # 大幅提升血量
        self.max_hp = hp * 5 * difficulty_mult["hp"] * (1 + floor * 0.3)
        self.hp = self.max_hp
        self.speed = 1.8 * difficulty_mult["spd"]  # 提升移动速度
        self.frames = load_frames(["boss.png"], BOSS_COLOR, (80, 80), "rect")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        # BOSS技能属性
        self.shoot_timer = 0
        self.shoot_cd = max(40, 100 - floor * 5)
        self.skill_timer = 0
        self.skill_cd = 300  # 技能冷却
        self.dash_distance = 200  # 冲刺距离
        self.aoe_radius = 100     # 范围攻击半径
        self.aoe_damage = 3       # 范围攻击伤害

    def update(self, px, py, enemy_bullets_group):
        super().update(px, py)
        
        # 普通射击
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cd:
            self.shoot_timer = 0
            angle = math.atan2(py - self.rect.centery, px - self.rect.centerx)
            # 散射子弹
            for i in range(-3, 4):
                if i % 2 == 0:
                    enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle + i * 0.15, speed=6))
        
        # BOSS技能循环
        self.skill_timer += 1
        if self.skill_timer >= self.skill_cd:
            self.skill_timer = 0
            skill_type = random.choice(["dash", "aoe", "debuff"])
            
            # 1. 冲刺技能
            if skill_type == "dash":
                dx, dy = px - self.rect.centerx, py - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    vx, vy = (dx / dist) * self.dash_distance, (dy / dist) * self.dash_distance
                    new_x = self.rect.centerx + vx
                    new_y = self.rect.centery + vy
                    if not is_wall(new_x, new_y):
                        self.rect.centerx = new_x
                        self.rect.centery = new_y
            
            # 2. 范围攻击
            elif skill_type == "aoe":
                # 绘制范围提示（红色圆圈）
                aoe_surface = pygame.Surface((self.aoe_radius*2, self.aoe_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(aoe_surface, (255, 0, 0, 100), (self.aoe_radius, self.aoe_radius), self.aoe_radius)
                screen.blit(aoe_surface, (self.rect.centerx - self.aoe_radius - camera_x, self.rect.centery - self.aoe_radius - camera_y))
                
                # 对范围内玩家造成伤害
                player_dist = math.hypot(px - self.rect.centerx, py - self.rect.centery)
                if player_dist < self.aoe_radius:
                    player.take_damage(self.aoe_damage)
            
            # 3. 施加Debuff
            elif skill_type == "debuff":
                debuff_type = random.choice(["vision", "buff"])
                if debuff_type == "vision":
                    debuffs["vision_reduce"] = 300  # 视野减少5秒
                else:
                    debuffs["buff_disable"] = 300   # 增益失效5秒

    def draw_hp(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20))
        pygame.draw.rect(surface, BOSS_COLOR, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400 * max(0, self.hp / self.max_hp), 20))
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20), 2)
        txt = font_base.render("守 门 巨 兽", True, WHITE)
        surface.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT - 65))

# 子弹类
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=7):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (6, 6), 6)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed * difficulty_mult["spd"]
        self.vx, self.vy = math.cos(angle) * self.speed, math.sin(angle) * self.speed

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
        self.bounces = 1 if player.has_bounce and debuffs["buff_disable"] == 0 else 0

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

# 其他精灵类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = load_frames(["coin.png"], YELLOW, (15, 15), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y = y
        self.time_offset = random.random() * math.pi * 2

    def update(self, player):
        # 金币磁铁天赋（受debuff影响）
        if player.has_magnet and debuffs["buff_disable"] == 0:
            dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 250:
                self.rect.centerx += (dx / dist) * 8
                self.rect.centery += (dy / dist) * 8
                return

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
# 4. 地图生成
# ==========================================
class Room:
    def __init__(self, x, y, w, h, is_start=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w // 2, y + h // 2
        self.cleared = is_start
        self.gates_coords = []
        # 强化敌人数量
        self.enemy_count = random.randint(6, 10) if not is_start else 0
        self.ranged_enemy_ratio = 0.3  # 远程敌人比例

    def is_player_inside(self, px, py):
        m = 40
        return self.x*TILE_SIZE+m < px < (self.x+self.w)*TILE_SIZE-m and self.y*TILE_SIZE+m < py < (self.y+self.h)*TILE_SIZE-m

def generate_map(floor):
    global game_map, room_list
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []
    
    # Boss房
    if floor % 5 == 0:
        w, h = 30, 30
        x, y = (MAP_COLS - w)//2, (MAP_ROWS - h)//2
        for r in range(y, y+h):
            for c in range(x, x+w): game_map[r][c] = 1
        room = Room(x, y, w, h, False)
        room.enemy_count = 0
        room_list.append(room)
        return room.cx * TILE_SIZE, (room.y + 2) * TILE_SIZE
        
    # 普通迷宫
    for _ in range(15):
        w, h = random.randint(10, 16), random.randint(10, 16)
        x, y = random.randint(2, MAP_COLS - w - 2), random.randint(2, MAP_ROWS - h - 2)
        if not any(not (x+w+3<r.x or x>r.x+r.w+3 or y+h+3<r.y or y>r.y+r.h+3) for r in room_list):
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            room = Room(x, y, w, h, len(room_list) == 0)
            # 随层数提升远程敌人比例
            room.ranged_enemy_ratio = min(0.7, 0.3 + floor * 0.05)
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
# 5. UI 绘制函数
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

    pw, ph = 700, 500
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

    tip = font_base.render("按 TAB 键关闭 | 数字键1/2切换武器", True, GRAY)
    screen.blit(tip, (px+pw//2 - tip.get_width()//2, py+ph-30))
    return buttons

def draw_talent(screen, talents, mx, my, acquired_talents):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(230); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
    
    title = font_title.render("神 赐 天 赋 (三选一)", True, PURPLE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    buttons = []
    for i, t in enumerate(talents):
        bx = SCREEN_WIDTH//2 - 150
        by = 250 + i * 120
        # 已获取的天赋不可选
        if t['id'] in acquired_talents:
            pygame.draw.rect(screen, GRAY, (bx, by, 300, 80), border_radius=8)
            pygame.draw.rect(screen, WHITE, (bx, by, 300, 80), 2, border_radius=8)
            txt_surf = font_large.render(f"{t['name']} : {t['desc']} (已获取)", True, (150,150,150))
            screen.blit(txt_surf, (bx + 150 - txt_surf.get_width()//2, by + 40 - txt_surf.get_height()//2))
            buttons.append((False, t))
        else:
            is_hover = draw_button(screen, f"{t['name']} : {t['desc']}", bx, by, 300, 80, (50,50,80), (80,80,120), mx, my)
            buttons.append((is_hover, t))
    return buttons

def draw_weapon_bar(screen, player):
    """绘制武器栏"""
    bar_bg = pygame.Rect(50, SCREEN_HEIGHT - 80, SCREEN_WIDTH - 100, 60)
    pygame.draw.rect(screen, (30,30,30), bar_bg, border_radius=10)
    pygame.draw.rect(screen, GRAY, bar_bg, 2, border_radius=10)
    
    # 绘制武器槽
    slot_width = (bar_bg.width - 40) // player.weapon_slots
    for i in range(player.weapon_slots):
        slot_rect = pygame.Rect(
            bar_bg.x + 20 + i * slot_width,
            bar_bg.y + 10,
            slot_width - 10,
            40
        )
        # 选中的武器高亮
        color = YELLOW if i == player.current_weapon else GRAY
        pygame.draw.rect(screen, color, slot_rect, 2, border_radius=5)
        
        # 绘制武器信息
        if i < len(player.weapons):
            weapon = player.weapons[i]
            name_txt = font_base.render(weapon["name"], True, WHITE)
            dmg_txt = font_base.render(f"伤害: {weapon['damage']}", True, WHITE)
            screen.blit(name_txt, (slot_rect.x + 5, slot_rect.y + 5))
            screen.blit(dmg_txt, (slot_rect.x + 5, slot_rect.y + 25))

def draw_hud(screen, player):
    """绘制玩家HUD（血量、护盾、debuff等）"""
    # 血量条
    pygame.draw.rect(screen, GRAY, (20, 20, 150, 20))
    pygame.draw.rect(screen, RED, (20, 20, 150 * max(0, player.hp/player.max_hp), 20))
    screen.blit(font_base.render(f"HP: {player.hp:.0f}/{player.max_hp}", True, WHITE), (30, 22))
    
    # 护盾条
    pygame.draw.rect(screen, GRAY, (20, 50, 150, 20))
    pygame.draw.rect(screen, BLUE, (20, 50, 150 * max(0, player.shield/player.max_shield), 20))
    screen.blit(font_base.render(f"护盾: {player.shield:.1f}/{player.max_shield}", True, WHITE), (30, 52))
    
    # 金币
    screen.blit(font_large.render(f"金币: {coins}", True, YELLOW), (20, 80))
    
    # Debuff提示
    if debuffs["vision_reduce"] > 0:
        debuffs["vision_reduce"] -= 1
        vision_txt = font_base.render("视野减少！", True, ORANGE if debuffs["vision_reduce"] > 60 else RED)
        screen.blit(vision_txt, (SCREEN_WIDTH - 100, 20))
    
    if debuffs["buff_disable"] > 0:
        debuffs["buff_disable"] -= 1
        buff_txt = font_base.render("增益失效！", True, ORANGE if debuffs["buff_disable"] > 60 else RED)
        screen.blit(buff_txt, (SCREEN_WIDTH - 100, 50))

# ==========================================
# 6. 主程序
# ==========================================
def main():
    global clock, wall_img, floor_img, coins, current_floor, camera_x, camera_y, ORANGE
    ORANGE = (255, 165, 0)
    
    clock = pygame.time.Clock()
    wall_img = load_frames(["wall.png"], (20, 20, 25), (TILE_SIZE, TILE_SIZE), "rect")[0]
    floor_img = load_frames(["floor.png"], (40, 40, 45), (TILE_SIZE, TILE_SIZE), "rect")[0]

    game_state = "MENU"
    coins = 0
    current_floor = 1
    difficulty_name = "普通"
    death_timer = 0
    acquired_talents = []  # 已获取的天赋
    
    # 扩展商店物品
    shop_items = [
        {"id": "ranged_dmg", "name": "提升远程伤害", "cost": 10, "level": 0, "max": 10, "cost_up": 5},
        {"id": "melee_dmg", "name": "提升近战伤害", "cost": 15, "level": 0, "max": 8, "cost_up": 8},
        {"id": "spd", "name": "提升移动速度", "cost": 15, "level": 0, "max": 5, "cost_up": 10},
        {"id": "fir", "name": "提升射速", "cost": 20, "level": 0, "max": 5, "cost_up": 10},
        {"id": "sct", "name": "多重射击", "cost": 30, "level": 0, "max": 2, "cost_up": 30},
        {"id": "hp", "name": "恢复1点生命", "cost": 10, "level": 0, "max": 999, "cost_up": 0},
        {"id": "shield_max", "name": "提升护盾上限", "cost": 50, "level": 0, "max": 5, "cost_up": 20},
        {"id": "explosion", "name": "提升爆炸伤害", "cost": 40, "level": 0, "max": 5, "cost_up": 20}
    ]
    
    # 扩展天赋列表
    all_talents = [
        {"id": "bounce", "name": "反弹墙壁", "desc": "子弹触墙可反弹1次（一次性）"},
        {"id": "hp_up", "name": "生命涌动", "desc": "生命上限+2并回满血"},
        {"id": "magnet", "name": "金币磁铁", "desc": "大范围自动吸附金币"},
        {"id": "explosion", "name": "敌人爆炸", "desc": "击败敌人有概率爆炸伤害周围敌人"},
        {"id": "weapon_slot", "name": "武器栏+1", "desc": "解锁额外武器栏位"}
    ]
    current_talents = []

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
        
        # 全局事件处理
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: pygame.display.toggle_fullscreen()

            # 状态切换
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "MENU":
                    if play_hover: 
                        coins, current_floor = 0, 1
                        acquired_talents = []
                        for item in shop_items: item['level'] = 0
                        player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor()
                        game_state = "PLAYING"
                    elif diff_hover: game_state = "DIFF"
                    elif intro_hover: game_state = "INTRO"
                    elif quit_hover: running = False
                
                elif game_state == "DIFF":
                    if btn_easy: difficulty_mult.update({"hp":0.8, "dmg":1, "spd":0.9, "range_hp":0.7, "range_spd":0.8}); difficulty_name="简单"; game_state="MENU"
                    elif btn_norm: difficulty_mult.update({"hp":1.0, "dmg":1, "spd":1.0, "range_hp":1.0, "range_spd":1.0}); difficulty_name="普通"; game_state="MENU"
                    elif btn_hard: difficulty_mult.update({"hp":1.8, "dmg":2, "spd":1.3, "range_hp":1.5, "range_spd":1.2}); difficulty_name="困难"; game_state="MENU"
                
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
                                
                                # 商店物品效果
                                if item['id'] == 'ranged_dmg':
                                    for weapon in player.weapons:
                                        if weapon["type"] == "pistol":
                                            weapon["damage"] += 5
                                elif item['id'] == 'melee_dmg':
                                    for weapon in player.weapons:
                                        if weapon["type"] == "melee":
                                            weapon["damage"] += 3
                                elif item['id'] == 'spd':
                                    player.speed += 1
                                elif item['id'] == 'fir':
                                    for weapon in player.weapons:
                                        weapon["cd"] = max(100, weapon["cd"] - 40)
                                elif item['id'] == 'sct':
                                    for weapon in player.weapons:
                                        if weapon["type"] == "pistol":
                                            weapon["scatter_level"] += 1
                                elif item['id'] == 'hp': 
                                    player.hp = min(player.max_hp, player.hp + 1)
                                    item['level'] -= 1
                                elif item['id'] == 'shield_max':
                                    player.max_shield += 1
                                elif item['id'] == 'explosion' and player.has_explosion:
                                    player.explosion_damage += 10
                    if not clicked and not pygame.Rect((SCREEN_WIDTH-700)//2, (SCREEN_HEIGHT-500)//2, 700, 500).collidepoint(mx, my):
                        game_state = "PLAYING"
                        
                elif game_state == "TALENT":
                    for is_hover, t in talent_btns:
                        if is_hover and t['id'] not in acquired_talents:
                            # 天赋效果
                            if t['id'] == 'bounce': 
                                player.has_bounce = True
                                acquired_talents.append('bounce')  # 一次性天赋
                            elif t['id'] == 'hp_up': 
                                player.max_hp += 2
                                player.hp = player.max_hp
                            elif t['id'] == 'magnet': 
                                player.has_magnet = True
                            elif t['id'] == 'explosion': 
                                player.has_explosion = True
                                # 解锁商店爆炸伤害选项
                                for item in shop_items:
                                    if item['id'] == 'explosion':
                                        item['max'] = 5
                            elif t['id'] == 'weapon_slot':
                                player.weapon_slots += 1
                                player.weapons.append({"type": "pistol", "name": "备用手枪", "damage": 10, "cd": 250, "scatter_level": 0})
                            acquired_talents.append(t['id'])
                            game_state = "PLAYING"

                elif game_state == "GAMEOVER":
                    if btn_restart:
                        game_state = "MENU"
                    elif btn_quit:
                        running = False

            # 键盘事件
            if event.type == pygame.KEYDOWN:
                if game_state in ["PLAYING", "SHOP"]:
                    if event.key == pygame.K_TAB:
                        game_state = "SHOP" if game_state == "PLAYING" else "PLAYING"
                    # 武器切换
                    elif event.key == pygame.K_1:
                        player.switch_weapon(-1)
                    elif event.key == pygame.K_2:
                        player.switch_weapon(1)

        # 菜单渲染
        pygame.mouse.set_visible(game_state != "PLAYING")
        
        if game_state == "MENU":
            play_hover, diff_hover, intro_hover, quit_hover = draw_menu(screen, mx, my)
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
                "操作说明：WASD移动，鼠标左键射击，TAB键打开商店，1/2切换武器。",
                "游戏机制：清空房间怪物后解锁下一区域。",
                "          击败敌人掉落金币，金币用于商店强化。",
                "          每过3关可选择强力天赋。",
                "          每过5关将遭遇强大BOSS！",
                "          护盾在未受攻击5秒后自动恢复。",
                "生存下去，看看你能抵达多少层！"
            ]
            for i, line in enumerate(lines):
                c = YELLOW if i==0 else WHITE
                screen.blit(font_large.render(line, True, c), (100, 150 + i*40))
            btn_back = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 600, 200, 50, GRAY, WHITE, mx, my)
            pygame.display.flip(); clock.tick(FPS); continue

        # 游戏主逻辑
        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_a]: dx -= player.speed
            if keys[pygame.K_d]: dx += player.speed
            if keys[pygame.K_w]: dy -= player.speed
            if keys[pygame.K_s]: dy += player.speed

            # 玩家移动
            if dx != 0 and not is_wall(player.rect.centerx+dx+(15 if dx>0 else -15), player.rect.centery): 
                player.rect.centerx += dx
            if dy != 0 and not is_wall(player.rect.centerx, player.rect.centery+dy+(15 if dy>0 else -15)): 
                player.rect.centery += dy
            player.update(dx, dy)

            # 相机跟随
            camera_x = player.rect.centerx - SCREEN_WIDTH // 2
            camera_y = player.rect.centery - SCREEN_HEIGHT // 2

            # 视野限制（Debuff）
            vision_radius = 400 if debuffs["vision_reduce"] == 0 else 150
            
            # 玩家攻击
            if pygame.mouse.get_pressed()[0]:
                attack_rect = player.attack(mx, my, camera_x, camera_y, bullets, enemy_bullets)
                # 近战攻击伤害处理
                if attack_rect:
                    for enemy in enemies:
                        if attack_rect.colliderect(enemy.rect):
                            enemy.hp -= player.weapons[player.current_weapon]["damage"]
                            if enemy.hp <= 0:
                                enemy.explode(enemies, player)
                                enemy.kill()
                                coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))

            # 房间战斗触发
            room_info_text, room_info_color = f"第 {current_floor} 层", GREEN
            
            for i, room in enumerate(room_list):
                if room.is_player_inside(player.rect.centerx, player.rect.centery):
                    if not room.cleared and not is_battle_locked:
                        current_room_index = i
                        is_battle_locked, spawn_pending = True, True
                        toggle_room_gates(room, close=True)
                        
                        if current_floor % 5 == 0:
                            room.enemy_count = 0
                            spawners.append(SpawnerWarning(room.cx*TILE_SIZE, room.cy*TILE_SIZE))
                        else:
                            # 混合生成普通和远程敌人
                            room.enemy_count += current_floor * 2
                            spawned = 0
                            ranged_count = int(room.enemy_count * room.ranged_enemy_ratio)
                            normal_count = room.enemy_count - ranged_count
                            
                            # 生成普通敌人
                            while spawned < normal_count:
                                rx = random.randint(room.x+1, room.x+room.w-2)*TILE_SIZE + TILE_SIZE//2
                                ry = random.randint(room.y+1, room.y+room.h-2)*TILE_SIZE + TILE_SIZE//2
                                if not is_wall(rx, ry) and math.hypot(rx-player.rect.centerx, ry-player.rect.centery) > 250:
                                    spawners.append(SpawnerWarning(rx, ry))
                                    spawned += 1
                            
                            # 生成远程敌人
                            spawned = 0
                            while spawned < ranged_count:
                                rx = random.randint(room.x+1, room.x+room.w-2)*TILE_SIZE + TILE_SIZE//2
                                ry = random.randint(room.y+1, room.y+room.h-2)*TILE_SIZE + TILE_SIZE//2
                                if not is_wall(rx, ry) and math.hypot(rx-player.rect.centerx, ry-player.rect.centery) > 300:
                                    spawners.append(SpawnerWarning(rx, ry))
                                    spawned += 1
                    break

            # 战斗逻辑
            if is_battle_locked:
                room_info_text = "敌人接近中！" if spawn_pending else "战斗中！"
                room_info_color = ORANGE if spawn_pending else RED
                
                for s in spawners[:]:
                    s.timer -= 1
                    if s.timer <= 0:
                        if current_floor % 5 == 0:
                            enemies.add(Boss(s.x, s.y, 200 + current_floor*80, current_floor))
                        else:
                            # 生成普通或远程敌人
                            if random.random() < room_list[current_room_index].ranged_enemy_ratio:
                                enemies.add(RangedEnemy(s.x, s.y, 30 + current_floor*15, current_floor))
                            else:
                                enemies.add(Enemy(s.x, s.y, 30 + current_floor*20, current_floor))
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

            # 更新精灵
            bullets.update()
            enemy_bullets.update()
            for b in enemy_bullets:
                if is_wall(b.rect.centerx, b.rect.centery): b.kill()
            
            # 区分BOSS和普通敌人更新
            for enemy in enemies:
                if isinstance(enemy, Boss):
                    enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets)
                elif isinstance(enemy, RangedEnemy):
                    enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets)
                else:
                    enemy.update(player.rect.centerx, player.rect.centery)
                
            coins_group.update(player)
            portals.update()

            # 碰撞检测
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for b in bullet_list: enemy.hp -= b.damage
                if enemy.hp <= 0:
                    # 敌人爆炸天赋
                    enemy.explode(enemies, player)
                    enemy.kill()
                    # 掉落金币
                    coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    if random.random() < 0.4: 
                        coins_group.add(Coin(enemy.rect.centerx+15, enemy.rect.centery))
                    if isinstance(enemy, Boss):
                        for _ in range(10): 
                            coins_group.add(Coin(enemy.rect.centerx+random.randint(-30,30), enemy.rect.centery+random.randint(-30,30)))
                    
            # 玩家受伤处理（优先护盾）
            if player.invincible_timer <= 0:
                hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
                hit_bullets = pygame.sprite.spritecollide(player, enemy_bullets, True)
                damage_taken = 0
                
                if hit_enemies: 
                    damage_taken += difficulty_mult["dmg"] * (1 + current_floor * 0.1)
                if hit_bullets: 
                    damage_taken += difficulty_mult["dmg"] * (1 + current_floor * 0.1)
                
                if damage_taken > 0:
                    is_dead = player.take_damage(damage_taken)
                    if is_dead:
                        game_state = "GAMEOVER_ANIM"
                        death_timer = pygame.time.get_ticks()

            # 收集金币
            coins += len(pygame.sprite.spritecollide(player, coins_group, True))
                
            # 进入下一层
            if pygame.sprite.spritecollide(player, portals, False):
                current_floor += 1
                player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned = reset_floor(player)
                is_battle_locked, current_room_index, spawn_pending = False, -1, False
                
                # 天赋选择（排除已获取的一次性天赋）
                if (current_floor - 1) % 3 == 0:
                    available_talents = [t for t in all_talents if t['id'] not in acquired_talents or t['id'] not in ['bounce']]
                    current_talents = random.sample(available_talents, min(3, len(available_talents)))
                    game_state = "TALENT"

        # 游戏渲染
        if game_state in ["PLAYING", "SHOP", "TALENT", "GAMEOVER_ANIM", "GAMEOVER"]:
            screen.fill(BLACK)
            
            # 视野限制效果
            if debuffs["vision_reduce"] > 0:
                vision_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                vision_surface.fill(BLACK)
                pygame.draw.circle(vision_surface, (0,0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), vision_radius)
                vision_surface.set_colorkey((0,0,0))
                screen.blit(vision_surface, (0,0))

            # 地图渲染
            start_c, end_c = int(camera_x//TILE_SIZE), int((camera_x+SCREEN_WIDTH)//TILE_SIZE)+1
            start_r, end_r = int(camera_y//TILE_SIZE), int((camera_y+SCREEN_HEIGHT)//TILE_SIZE)+1
            for r in range(max(0, start_r), min(MAP_ROWS, end_r)):
                for c in range(max(0, start_c), min(MAP_COLS, end_c)):
                    val, draw_x, draw_y = game_map[r][c], c*TILE_SIZE - camera_x, r*TILE_SIZE - camera_y
                    if val == 0: screen.blit(wall_img, (draw_x, draw_y))
                    elif val == 1: screen.blit(floor_img, (draw_x, draw_y))
                    elif val == 2:
                        pygame.draw.rect(screen, ORANGE, (draw_x, draw_y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, RED, (draw_x, draw_y, TILE_SIZE, TILE_SIZE), 2)

            # 绘制生成警告
            for s in spawners:
                pygame.draw.circle(screen, RED, (s.x-camera_x, s.y-camera_y), 20, 2)

            # 绘制精灵
            for e in list(portals)+list(coins_group)+list(enemies)+list(bullets)+list(enemy_bullets):
                screen.blit(e.image, (e.rect.x-camera_x, e.rect.y-camera_y))
            for e in enemies: e.draw_hp(screen, camera_x, camera_y)
            
            # 绘制玩家
            if game_state == "GAMEOVER_ANIM" or game_state == "GAMEOVER":
                player.update(0, 0, is_dead=True)
            screen.blit(player.image, (player.rect.x-camera_x, player.rect.y-camera_y))

            # 绘制HUD
            draw_hud(screen, player)
            room_txt = font_large.render(room_info_text, True, room_info_color)
            screen.blit(room_txt, (SCREEN_WIDTH//2 - room_txt.get_width()//2, 20))

            # 武器栏
            draw_weapon_bar(screen, player)

            if game_state == "PLAYING":
                pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
                pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

            # 弹窗渲染
            if game_state == "SHOP":
                shop_btns = draw_shop(screen, player, coins, shop_items, mx, my)
            elif game_state == "TALENT":
                talent_btns = draw_talent(screen, current_talents, mx, my, acquired_talents)
            elif game_state == "GAMEOVER_ANIM":
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