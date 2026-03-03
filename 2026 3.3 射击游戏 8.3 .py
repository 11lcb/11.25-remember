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
ORANGE = (255, 165, 0)
PALE_YELLOW = (255, 255, 150)  # 受击伤害数字的淡黄色

TILE_SIZE = 60
MAP_COLS, MAP_ROWS = 60, 60
game_map, room_list = [], []
explored_map = []  

font_name = "SimHei" if "simhei" in pygame.font.get_fonts() else "Arial"
font_base = pygame.font.SysFont(font_name, 18)
font_large = pygame.font.SysFont(font_name, 26, bold=True)
font_title = pygame.font.SysFont(font_name, 50, bold=True)

difficulty_mult = {"hp": 1.0, "dmg": 1, "spd": 1.0, "range_hp": 1.0, "range_spd": 1.0}

debuffs = {"vision_reduce": 0, "buff_disable": 0, "last_shield_hit": 0}

# ==========================================
# 2. 特效类
# ==========================================
class DamageText(pygame.sprite.Sprite):
    """伤害跳字特效"""
    def __init__(self, x, y, damage_val, is_heal=False):
        super().__init__()
        self.x, self.y = x, y
        self.color = GREEN if is_heal else PALE_YELLOW
        self.text = f"+{int(damage_val)}" if is_heal else f"-{int(damage_val)}"
        self.lifetime = 60  # 持续1秒
        self.timer = 0

    def update(self):
        self.timer += 1
        self.y -= 1  # 向上飘动
        if self.timer >= self.lifetime:
            self.kill()

    def draw(self, surface, camera_x, camera_y):
        alpha = int(255 * (1 - self.timer / self.lifetime))
        txt_surf = font_large.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        surface.blit(txt_surf, (self.x - camera_x - txt_surf.get_width()//2, self.y - camera_y))

class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        self.x, self.y = x, y
        self.max_radius = damage * 1.5
        self.current_radius = 0
        self.alpha = 255
        self.lifetime = 30 
        self.timer = 0

    def update(self):
        self.timer += 1
        self.current_radius = self.max_radius * (self.timer / self.lifetime)
        self.alpha = 255 * (1 - self.timer / self.lifetime)
        if self.timer >= self.lifetime: self.kill()

    def draw(self, surface, camera_x, camera_y):
        s = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 200, 0, int(self.alpha)), (self.max_radius, self.max_radius), int(self.current_radius), 2)
        pygame.draw.circle(s, (255, 100, 0, int(self.alpha/2)), (self.max_radius, self.max_radius), int(self.current_radius/2))
        surface.blit(s, (self.x - self.max_radius - camera_x, self.y - self.max_radius - camera_y))

class MeleeSlashEffect(pygame.sprite.Sprite):
    def __init__(self, player_x, player_y, player_facing_right, attack_range, target_x, target_y):
        super().__init__()
        self.x, self.y = player_x, player_y
        self.range = attack_range
        self.lifetime = 12 
        self.timer = 0
        angle = math.atan2(target_y - player_y, target_x - player_x)
        self.angle_left = angle - math.pi/3
        self.angle_right = angle + math.pi/3

    def update(self):
        self.timer += 1
        if self.timer >= self.lifetime: self.kill()

    def draw(self, surface, camera_x, camera_y):
        s = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        progress = self.timer / self.lifetime
        current_sweep_angle = self.angle_left + (self.angle_right - self.angle_left) * progress
        alpha = int(255 * (1 - progress))
        points = [(self.range, self.range)]
        for angle in range(int(math.degrees(self.angle_left)), int(math.degrees(current_sweep_angle)) + 1, 2):
            rad = math.radians(angle)
            points.append((self.range + math.cos(rad) * self.range, self.range + math.sin(rad) * self.range))
        if len(points) > 2: pygame.draw.polygon(s, (255, 255, 255, alpha), points)
        surface.blit(s, (self.x - self.range - camera_x, self.y - self.range - camera_y))

class BossAoeEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, damage, player):
        super().__init__()
        self.x, self.y, self.radius, self.damage, self.player = x, y, radius, damage, player
        self.lifetime, self.timer = 60, 0

    def update(self):
        self.timer += 1
        if self.timer == self.lifetime:
            if math.hypot(self.player.rect.centerx - self.x, self.player.rect.centery - self.y) <= self.radius:
                self.player.take_damage(self.damage)
        elif self.timer >= self.lifetime + 15: self.kill()

    def draw(self, surface, camera_x, camera_y):
        draw_x, draw_y = self.x - camera_x, self.y - camera_y
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        if self.timer < self.lifetime:
            inner_r = int(self.radius * (self.timer / self.lifetime))
            pygame.draw.circle(s, (255, 0, 0, 80), (self.radius, self.radius), inner_r)
            pygame.draw.circle(s, (255, 0, 0, 200), (self.radius, self.radius), self.radius, 2)
        else:
            alpha = int(255 * (1 - (self.timer - self.lifetime) / 15))
            pygame.draw.circle(s, (255, 0, 0, alpha), (self.radius, self.radius), self.radius)
        surface.blit(s, (draw_x - self.radius, draw_y - self.radius))

# ==========================================
# 3. 辅助函数
# ==========================================
def load_frames(image_paths, fallback_color, size, shape="rect"):
    frames = []
    for path in image_paths:
        if os.path.exists(path): frames.append(pygame.transform.scale(pygame.image.load(path).convert_alpha(), size))
    if not frames:
        s = pygame.Surface(size, pygame.SRCALPHA)
        if shape == "circle": pygame.draw.circle(s, fallback_color, (size[0]//2, size[1]//2), min(size)//2)
        elif shape == "cross": 
            pygame.draw.line(s, fallback_color, (0,0), size, 4)
            pygame.draw.line(s, fallback_color, (0,size[1]), (size[0],0), 4)
        else: pygame.draw.rect(s, fallback_color, (0,0, size[0], size[1]), border_radius=5)
        frames.append(s)
    return frames

# ==========================================
# 4. 游戏核心类 (Sprites)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.idle_frames = load_frames(["player_idle.png"], GREEN, (30, 30), "circle")
        self.run_frames = load_frames(["player_run1.png", "player_run2.png"], GREEN, (30, 30), "circle")
        self.death_frames = load_frames(["player_death.png"], GRAY, (40, 40), "cross")
        self.frames, self.current_frame = self.idle_frames, 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        
        self.max_hp = 5
        self.hp = 5
        self.invincible_timer = 0
        self.speed = 6
        
        self.max_shield = 2          
        self.shield = self.max_shield  
        self.last_shield_damage = 0   
        
        self.weapon_slots = 2        
        self.current_weapon = 0      
        self.weapons = [
            {"type": "pistol", "name": "普通手枪", "damage": 25, "cd": 300, "scatter_level": 0},
            {"type": "melee", "name": "近战小刀", "damage": 20, "range": 40, "cd": 400}
        ]
        
        self.has_bounce, self.has_magnet, self.has_explosion = False, False, False
        self.explosion_damage, self.explosion_radius = 20, 50   
        self.last_shoot_time = 0

    def update(self, dx, dy, is_dead=False):
        if is_dead: self.image = self.death_frames[0]; return
        if self.shield < self.max_shield and pygame.time.get_ticks() - self.last_shield_damage > 5000:
            self.shield = min(self.max_shield, self.shield + 0.2)
        if self.invincible_timer > 0: self.invincible_timer -= 1

        if dx != 0 or dy != 0:
            self.frames = self.run_frames
            self.facing_right = True if dx > 0 else (False if dx < 0 else self.facing_right)
        else: self.frames = self.idle_frames

        self.current_frame = (self.current_frame + 0.15) % len(self.frames)
        self.image = self.frames[int(self.current_frame)].copy()
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0: self.image.set_alpha(100)
        if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, damage):
        damage = int(damage)
        self.last_shield_damage = pygame.time.get_ticks()
        if self.shield > 0:
            dmg_taken = min(self.shield, damage)
            self.shield -= dmg_taken
            remaining = damage - dmg_taken
            if remaining > 0: self.hp -= remaining
        else: self.hp -= damage
        self.invincible_timer = 60
        return self.hp <= 0  # 确保浮点数不会导致UI显示0而不死

    def switch_weapon(self, direction):
        if len(self.weapons) > 0:
            self.current_weapon = (self.current_weapon + direction) % len(self.weapons)

    def attack(self, mx, my, camera_x, camera_y, bullets_group, enemy_bullets_group, effects_group):
        if not self.weapons: return None
        weapon = self.weapons[self.current_weapon]
        if pygame.time.get_ticks() - self.last_shoot_time < weapon["cd"]: return None
        self.last_shoot_time = pygame.time.get_ticks()
        wx, wy = mx + camera_x, my + camera_y
        
        if weapon["type"] == "pistol":
            angle = math.atan2(wy - self.rect.centery, wx - self.rect.centerx)
            bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle, weapon["damage"], self))
            if weapon["scatter_level"] >= 1:
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle-0.2, weapon["damage"], self))
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle+0.2, weapon["damage"], self))
            if weapon["scatter_level"] >= 2:
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle-0.4, weapon["damage"], self))
                bullets_group.add(Bullet(self.rect.centerx, self.rect.centery, angle+0.4, weapon["damage"], self))
        
        elif weapon["type"] == "melee":
            effects_group.add(MeleeSlashEffect(self.rect.centerx, self.rect.centery, self.facing_right, weapon["range"], wx, wy))
            attack_rect = pygame.Rect(self.rect.centerx - weapon["range"], self.rect.centery - weapon["range"], weapon["range"] * 2, weapon["range"] * 2)
            for bullet in enemy_bullets_group:
                if attack_rect.colliderect(bullet.rect): bullet.kill()
            return attack_rect
        return None

# ================= 新增：物品与箱子系统 =================
class GroundItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, weapon_data=None):
        super().__init__()
        self.item_type = item_type
        self.weapon_data = weapon_data
        self.image = pygame.Surface((25, 25))
        if item_type == "potion":
            self.image = load_frames(["potion.png"], (255,105,180), (25,25), "circle")[0]
        else:
            self.image = load_frames(["weapon_drop.png"], (150,150,150), (25,25), "rect")[0]
        self.rect = self.image.get_rect(center=(x, y))

    def draw_prompt(self, surface, camera_x, camera_y):
        txt = f"按F拾取 [{self.weapon_data['name']}]" if self.item_type == "weapon" else "按F拾取 [恢复血瓶]"
        surf = font_base.render(txt, True, WHITE)
        surface.blit(surf, (self.rect.centerx - camera_x - surf.get_width()//2, self.rect.y - camera_y - 25))

class Crate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_frames(["crate.png"], WHITE, (45, 45), "rect")[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 30

    def take_damage(self, amount, items_group, effects_group):
        amount = int(amount)
        self.hp -= amount
        effects_group.add(DamageText(self.rect.centerx, self.rect.top, amount))
        if self.hp <= 0:
            self.kill()
            rand = random.random()
            if rand < 0.25:  # 25% 概率掉落武器
                w_type = random.choice([
                    {"type": "pistol", "name": "左轮手枪", "damage": 55, "cd": 550, "scatter_level": 0},
                    {"type": "melee", "name": "近战小刀", "damage": 20, "range": 40, "cd": 400},
                    {"type": "melee", "name": "大刀", "damage": 40, "range": 70, "cd": 800} # 新武器
                ])
                items_group.add(GroundItem(self.rect.centerx, self.rect.centery, "weapon", w_type))
            elif rand < 0.55:  # 30% 概率掉血瓶
                items_group.add(GroundItem(self.rect.centerx, self.rect.centery, "potion"))

# ================= 敌人逻辑 =================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, floor):
        super().__init__()
        self.max_hp = hp * difficulty_mult["hp"] * (1 + floor * 0.15)
        self.hp = self.max_hp
        self.speed = 2.0 + (floor * 0.2) * difficulty_mult["spd"]
        # 强制敌人伤害为整数且至少为1
        self.damage = max(1, int(1 * difficulty_mult["dmg"] * (1 + floor * 0.1)))
        self.frames = load_frames(["enemy_run.png"], RED, (30, 30), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.is_exploded = False

    def update(self, px, py):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            vx, vy = (dx / dist) * self.speed, (dy / dist) * self.speed
            if not is_wall(self.rect.centerx + vx, self.rect.centery): self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy): self.rect.centery += vy

    def draw_hp(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, BLACK, (self.rect.x - camera_x, self.rect.y - camera_y - 10, 30, 5))
        pygame.draw.rect(surface, RED, (self.rect.x - camera_x, self.rect.y - camera_y - 10, 30 * max(0, self.hp / self.max_hp), 5))

    def explode(self, enemies_group, player, effects_group):
        if self.is_exploded or not player.has_explosion: return
        self.is_exploded = True
        effects_group.add(ExplosionEffect(self.rect.centerx, self.rect.centery, player.explosion_damage))
        explosion_rect = pygame.Rect(self.rect.centerx - player.explosion_radius, self.rect.centery - player.explosion_radius, player.explosion_radius * 2, player.explosion_radius * 2)
        for enemy in enemies_group:
            if enemy != self and explosion_rect.colliderect(enemy.rect):
                enemy.hp -= player.explosion_damage
                effects_group.add(DamageText(enemy.rect.centerx, enemy.rect.top, player.explosion_damage))

class RangedEnemy(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 0.6, floor)
        self.frames = load_frames(["ranged_enemy.png"], BLUE, (25, 25), "circle")
        self.image = self.frames[0]
        self.attack_range, self.attack_cd, self.attack_timer, self.is_attacking = 400, max(80, 150 - floor * 5), 0, False

    def update(self, px, py, enemy_bullets_group=None):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        self.attack_timer += 1
        
        if dist < self.attack_range and self.attack_timer >= self.attack_cd:
            self.is_attacking = True
            self.attack_timer = 0
            if enemy_bullets_group is not None:
                enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, math.atan2(dy, dx), speed=5, damage=self.damage))
        else: self.is_attacking = False
            
        if not self.is_attacking and dist > 50:
            vx, vy = (dx / dist) * self.speed, (dy / dist) * self.speed
            if not is_wall(self.rect.centerx + vx, self.rect.centery): self.rect.centerx += vx
            if not is_wall(self.rect.centerx, self.rect.centery + vy): self.rect.centery += vy

class Boss(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 5, floor)
        self.frames = load_frames(["boss.png"], BOSS_COLOR, (80, 80), "rect")
        self.image = self.frames[0]
        self.shoot_timer, self.shoot_cd = 0, max(40, 100 - floor * 5)
        self.skill_timer, self.skill_cd = 0, 300
        self.dash_distance, self.aoe_radius, self.aoe_damage = 200, 120, max(3, self.damage * 2)

    def update(self, px, py, enemy_bullets_group, effects_group, player):
        super().update(px, py)
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cd:
            self.shoot_timer = 0
            angle = math.atan2(py - self.rect.centery, px - self.rect.centerx)
            for i in range(-3, 4):
                if i % 2 == 0:
                    enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle + i * 0.15, speed=6, damage=self.damage))
        
        self.skill_timer += 1
        if self.skill_timer >= self.skill_cd:
            self.skill_timer = 0
            skill_type = random.choice(["dash", "aoe", "debuff"])
            if skill_type == "dash":
                dist = math.hypot(px - self.rect.centerx, py - self.rect.centery)
                if dist > 0:
                    nx, ny = self.rect.centerx + ((px - self.rect.centerx) / dist) * self.dash_distance, self.rect.centery + ((py - self.rect.centery) / dist) * self.dash_distance
                    if not is_wall(nx, ny) and not is_wall(self.rect.centerx, ny) and not is_wall(nx, self.rect.centery):
                        self.rect.centerx, self.rect.centery = nx, ny
            elif skill_type == "aoe": effects_group.add(BossAoeEffect(self.rect.centerx, self.rect.centery, self.aoe_radius, self.aoe_damage, player))
            elif skill_type == "debuff":
                if random.choice(["vision", "buff"]) == "vision": debuffs["vision_reduce"] = 300
                else: debuffs["buff_disable"] = 300

    def draw_hp(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20))
        pygame.draw.rect(surface, BOSS_COLOR, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400 * max(0, self.hp / self.max_hp), 20))
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, 400, 20), 2)
        surface.blit(font_base.render("浩 淼 大 人", True, WHITE), (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT - 65))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (6, 6), 6)
        pygame.draw.circle(self.image, YELLOW, (6, 6), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed, self.damage = speed * difficulty_mult["spd"], int(damage)
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
        self.damage = int(damage)
        self.player = player
        self.vx, self.vy = math.cos(angle) * 15, math.sin(angle) * 15
        self.bounces = 1 if player.has_bounce and debuffs["buff_disable"] == 0 else 0

    def update(self):
        self.rect.x += self.vx
        if is_wall(self.rect.centerx, self.rect.centery):
            if self.bounces > 0: self.rect.x -= self.vx; self.vx = -self.vx; self.bounces -= 1
            else: self.kill(); return
        self.rect.y += self.vy
        if is_wall(self.rect.centerx, self.rect.centery):
            if self.bounces > 0: self.rect.y -= self.vy; self.vy = -self.vy; self.bounces -= 1
            else: self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = load_frames(["coin.png"], YELLOW, (15, 15), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.base_y, self.time_offset = y, random.random() * math.pi * 2

    def update(self, player):
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
# 地图与UI绘制等
# ==========================================
class Room:
    def __init__(self, x, y, w, h, is_start=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.cx, self.cy = x + w // 2, y + h // 2
        self.cleared = is_start
        self.gates_coords = []
        self.enemy_count = random.randint(6, 10) if not is_start else 0
        self.ranged_enemy_ratio = 0.3

    def is_player_inside(self, px, py):
        m = 40
        return self.x*TILE_SIZE+m < px < (self.x+self.w)*TILE_SIZE-m and self.y*TILE_SIZE+m < py < (self.y+self.h)*TILE_SIZE-m

def generate_map(floor):
    global game_map, room_list, explored_map
    game_map = [[0 for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    explored_map = [[False for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]
    room_list = []
    
    if floor % 5 == 0:
        w, h = 30, 30
        x, y = (MAP_COLS - w)//2, (MAP_ROWS - h)//2
        for r in range(y, y+h):
            for c in range(x, x+w): game_map[r][c] = 1
        room_list.append(Room(x, y, w, h, False))
        return room_list[0].cx * TILE_SIZE, (room_list[0].y + 2) * TILE_SIZE
        
    for _ in range(15):
        w, h = random.randint(10, 16), random.randint(10, 16)
        x, y = random.randint(2, MAP_COLS - w - 2), random.randint(2, MAP_ROWS - h - 2)
        if not any(not (x+w+3<r.x or x>r.x+r.w+3 or y+h+3<r.y or y>r.y+r.h+3) for r in room_list):
            for r_idx in range(y, y + h):
                for c_idx in range(x, x + w): game_map[r_idx][c_idx] = 1
            r = Room(x, y, w, h, len(room_list) == 0)
            r.ranged_enemy_ratio = min(0.7, 0.3 + floor * 0.05)
            room_list.append(r)

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
    screen.blit(font_title.render("绝 境 突 围", True, YELLOW), (SCREEN_WIDTH//2 - 120, 150))
    return (draw_button(screen, "开始游戏", SCREEN_WIDTH//2-100, 350, 200, 50, (50,150,50), (100,200,100), mx, my),
            draw_button(screen, "难度选择", SCREEN_WIDTH//2-100, 420, 200, 50, (150,100,50), (200,150,100), mx, my),
            draw_button(screen, "游戏介绍", SCREEN_WIDTH//2-100, 490, 200, 50, (50,100,150), (100,150,200), mx, my),
            draw_button(screen, "退出游戏", SCREEN_WIDTH//2-100, 560, 200, 50, (150,50,50), (200,100,100), mx, my))

def draw_shop(screen, player, coins, shop_items, mx, my, page):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(200); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
    pw, ph = 700, 500
    px, py = (SCREEN_WIDTH - pw)//2, (SCREEN_HEIGHT - ph)//2
    pygame.draw.rect(screen, (40,40,40), (px, py, pw, ph), border_radius=10)
    pygame.draw.rect(screen, YELLOW, (px, py, pw, ph), 3, border_radius=10)
    screen.blit(font_title.render("—— 神 秘 商 店 ——", True, YELLOW), (px+180, py+20))
    screen.blit(font_large.render(f"持有金币: {coins}", True, WHITE), (px+30, py+80))

    start_idx, end_idx = page * 4, min((page + 1) * 4, len(shop_items))
    buttons = []
    for i in range(start_idx, end_idx):
        item = shop_items[i]
        y = py + 130 + (i - start_idx)*60
        name_color = GRAY if item['level'] >= item['max'] else WHITE
        screen.blit(font_large.render(f"{item['name']} " + ("(Max)" if item['level'] >= item['max'] else f"(Lv.{item['level']})"), True, name_color), (px+40, y))
        btn_rect = pygame.Rect(px+pw-160, y-5, 120, 40)
        can_buy = coins >= item['cost'] and item['level'] < item['max']
        is_hover = can_buy and btn_rect.collidepoint(mx, my)
        pygame.draw.rect(screen, (100,200,100) if is_hover else (50,150,50) if can_buy else GRAY, btn_rect, border_radius=5)
        cost_txt = font_base.render(f"${item['cost']}", True, BLACK if is_hover else WHITE)
        screen.blit(cost_txt, (btn_rect.x+60-cost_txt.get_width()//2, btn_rect.y+10))
        buttons.append((btn_rect, item, can_buy))

    prev_hover = draw_button(screen, "上一页", px + 40, py + ph - 70, 100, 40, GRAY, WHITE, mx, my) if page > 0 else False
    next_hover = draw_button(screen, "下一页", px + pw - 140, py + ph - 70, 100, 40, GRAY, WHITE, mx, my) if end_idx < len(shop_items) else False
    screen.blit(font_base.render("按 TAB 键关闭 | 数字键1/2切换武器", True, GRAY), (px+200, py+ph-30))
    return buttons, prev_hover, next_hover

def draw_talent(screen, talents, mx, my, acquired_talents):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(230); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
    screen.blit(font_title.render("神 赐 天 赋 (三选一)", True, PURPLE), (SCREEN_WIDTH//2 - 200, 100))
    buttons = []
    for i, t in enumerate(talents):
        bx, by = SCREEN_WIDTH//2 - 150, 250 + i * 120
        if t['id'] in acquired_talents:
            pygame.draw.rect(screen, GRAY, (bx, by, 300, 80), border_radius=8)
            pygame.draw.rect(screen, WHITE, (bx, by, 300, 80), 2, border_radius=8)
            txt_surf = font_large.render(f"{t['name']} : {t['desc']} (已获取)", True, (150,150,150))
            screen.blit(txt_surf, (bx + 150 - txt_surf.get_width()//2, by + 40 - txt_surf.get_height()//2))
            buttons.append((False, t))
        else: buttons.append((draw_button(screen, f"{t['name']} : {t['desc']}", bx, by, 300, 80, (50,50,80), (80,80,120), mx, my), t))
    return buttons

def draw_weapon_bar(screen, player):
    bar_bg = pygame.Rect(50, SCREEN_HEIGHT - 80, SCREEN_WIDTH - 100, 60)
    pygame.draw.rect(screen, (30,30,30), bar_bg, border_radius=10)
    pygame.draw.rect(screen, GRAY, bar_bg, 2, border_radius=10)
    slot_width = (bar_bg.width - 40) // player.weapon_slots
    for i in range(player.weapon_slots):
        slot_rect = pygame.Rect(bar_bg.x + 20 + i * slot_width, bar_bg.y + 10, slot_width - 10, 40)
        pygame.draw.rect(screen, YELLOW if i == player.current_weapon else GRAY, slot_rect, 2, border_radius=5)
        if i < len(player.weapons):
            screen.blit(font_base.render(player.weapons[i]["name"], True, WHITE), (slot_rect.x + 5, slot_rect.y + 5))
            screen.blit(font_base.render(f"伤害: {player.weapons[i]['damage']}", True, WHITE), (slot_rect.x + 5, slot_rect.y + 25))

def draw_hud(screen, player):
    pygame.draw.rect(screen, GRAY, (20, 20, 150, 20))
    # 彻底修复：使用整数且确保即使血量是小数（盾牌扣除剩余后）也不会显示为0但不死。使用int强转。
    pygame.draw.rect(screen, RED, (20, 20, 150 * max(0, player.hp/player.max_hp), 20))
    screen.blit(font_base.render(f"HP: {int(max(0, player.hp))}/{player.max_hp}", True, WHITE), (30, 22))
    
    pygame.draw.rect(screen, GRAY, (20, 50, 150, 20))
    pygame.draw.rect(screen, BLUE, (20, 50, 150 * max(0, player.shield/player.max_shield), 20))
    screen.blit(font_base.render(f"护盾: {player.shield:.1f}/{player.max_shield}", True, WHITE), (30, 52))
    
    screen.blit(font_large.render(f"金币: {coins}", True, YELLOW), (20, 80))
    if debuffs["vision_reduce"] > 0:
        debuffs["vision_reduce"] -= 1
        screen.blit(font_base.render("视野减少！", True, ORANGE if debuffs["vision_reduce"] > 60 else RED), (SCREEN_WIDTH - 150, 220))
    if debuffs["buff_disable"] > 0:
        debuffs["buff_disable"] -= 1
        screen.blit(font_base.render("增益失效！", True, ORANGE if debuffs["buff_disable"] > 60 else RED), (SCREEN_WIDTH - 150, 250))

def draw_minimap(screen, player):
    map_w, map_h = MAP_COLS * 3, MAP_ROWS * 3
    start_x, start_y = SCREEN_WIDTH - map_w - 20, 20
    pygame.draw.rect(screen, (20, 20, 20, 180), (start_x, start_y, map_w, map_h))
    pygame.draw.rect(screen, GRAY, (start_x, start_y, map_w, map_h), 2)
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if explored_map[r][c]:
                if game_map[r][c] == 1: pygame.draw.rect(screen, (120, 120, 120), (start_x + c*3, start_y + r*3, 3, 3))
                elif game_map[r][c] == 2: pygame.draw.rect(screen, RED, (start_x + c*3, start_y + r*3, 3, 3))
    px, py = int(player.rect.centerx // TILE_SIZE), int(player.rect.centery // TILE_SIZE)
    if 0 <= px < MAP_COLS and 0 <= py < MAP_ROWS: pygame.draw.rect(screen, GREEN, (start_x + px*3, start_y + py*3, 4, 4))

# ==========================================
# 6. 主程序
# ==========================================
def main():
    global clock, wall_img, floor_img, coins, current_floor, camera_x, camera_y
    
    clock = pygame.time.Clock()
    wall_img = load_frames(["wall.png"], (20, 20, 25), (TILE_SIZE, TILE_SIZE), "rect")[0]
    floor_img = load_frames(["floor.png"], (40, 40, 45), (TILE_SIZE, TILE_SIZE), "rect")[0]

    game_state, coins, current_floor, difficulty_name, death_timer, acquired_talents, shop_page = "MENU", 0, 1, "普通", 0, [], 0
    
    shop_items = [
        {"id": "melee_range", "name": "提升近战范围", "cost": 20, "level": 0, "max": 5, "cost_up": 10},
        {"id": "ranged_dmg", "name": "提升远程伤害", "cost": 10, "level": 0, "max": 10, "cost_up": 5},
        {"id": "melee_dmg", "name": "提升近战伤害", "cost": 15, "level": 0, "max": 8, "cost_up": 8},
        {"id": "spd", "name": "提升移动速度", "cost": 15, "level": 0, "max": 5, "cost_up": 10},
        {"id": "fir", "name": "提升射速", "cost": 20, "level": 0, "max": 5, "cost_up": 10},
        {"id": "sct", "name": "多重射击", "cost": 30, "level": 0, "max": 2, "cost_up": 30},
        {"id": "hp", "name": "恢复1点生命", "cost": 10, "level": 0, "max": 999, "cost_up": 0},
        {"id": "shield_max", "name": "提升护盾上限", "cost": 50, "level": 0, "max": 5, "cost_up": 20},
        {"id": "explosion", "name": "提升爆炸伤害", "cost": 40, "level": 0, "max": 5, "cost_up": 20}
    ]
    
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
        # 生成箱子
        crates_group = pygame.sprite.Group()
        for r in room_list[1:]:
            for _ in range(random.randint(1, 3)):
                crates_group.add(Crate(random.randint(r.x+1, r.x+r.w-2)*TILE_SIZE + TILE_SIZE//2, random.randint(r.y+1, r.y+r.h-2)*TILE_SIZE + TILE_SIZE//2))
        return p, pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), [], False, pygame.sprite.Group(), crates_group, pygame.sprite.Group()

    player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned, effects, crates, items_group = reset_floor()
    is_battle_locked, current_room_index, spawn_pending = False, -1, False

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11: pygame.display.toggle_fullscreen()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "MENU":
                    if play_hover: 
                        coins, current_floor, acquired_talents = 0, 1, []
                        for item in shop_items: item['level'] = 0
                        player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned, effects, crates, items_group = reset_floor()
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
                    if prev_hover: shop_page -= 1; clicked = True
                    elif next_hover: shop_page += 1; clicked = True
                        
                    for btn_rect, item, can_buy in shop_btns:
                        if btn_rect.collidepoint(mx, my):
                            clicked = True
                            if can_buy:
                                coins -= item['cost']; item['level'] += 1; item['cost'] += item['cost_up']
                                if item['id'] == 'ranged_dmg':
                                    for w in player.weapons:
                                        if w["type"] == "pistol": w["damage"] += 5
                                elif item['id'] == 'melee_dmg':
                                    for w in player.weapons:
                                        if w["type"] == "melee": w["damage"] += 3
                                elif item['id'] == 'melee_range':
                                    for w in player.weapons:
                                        if w["type"] == "melee": w["range"] += 10
                                elif item['id'] == 'spd': player.speed += 1
                                elif item['id'] == 'fir':
                                    for w in player.weapons: w["cd"] = max(100, w["cd"] - 40)
                                elif item['id'] == 'sct':
                                    for w in player.weapons:
                                        if w["type"] == "pistol": w["scatter_level"] += 1
                                elif item['id'] == 'hp': 
                                    player.hp = min(player.max_hp, player.hp + 1); item['level'] -= 1
                                elif item['id'] == 'shield_max': player.max_shield += 1
                                elif item['id'] == 'explosion' and player.has_explosion: player.explosion_damage += 10
                    if not clicked and not pygame.Rect((SCREEN_WIDTH-700)//2, (SCREEN_HEIGHT-500)//2, 700, 500).collidepoint(mx, my): game_state = "PLAYING"
                elif game_state == "TALENT":
                    for is_hover, t in talent_btns:
                        if is_hover and t['id'] not in acquired_talents:
                            if t['id'] == 'bounce': player.has_bounce = True; acquired_talents.append('bounce')
                            elif t['id'] == 'hp_up': player.max_hp += 2; player.hp = player.max_hp
                            elif t['id'] == 'magnet': player.has_magnet = True
                            elif t['id'] == 'explosion': 
                                player.has_explosion = True
                                for item in shop_items:
                                    if item['id'] == 'explosion': item['max'] = 5
                            elif t['id'] == 'weapon_slot':
                                player.weapon_slots += 1
                                player.weapons.append({"type": "pistol", "name": "备用手枪", "damage": 25, "cd": 250, "scatter_level": 0})
                            acquired_talents.append(t['id']); game_state = "PLAYING"
                elif game_state == "GAMEOVER":
                    if btn_restart: game_state = "MENU"
                    elif btn_quit: running = False

            if event.type == pygame.KEYDOWN:
                if game_state in ["PLAYING", "SHOP"]:
                    if event.key == pygame.K_TAB: shop_page = 0; game_state = "SHOP" if game_state == "PLAYING" else "PLAYING"
                    elif event.key == pygame.K_1: player.switch_weapon(-1)
                    elif event.key == pygame.K_2: player.switch_weapon(1)
                    # === F键 拾取逻辑 ===
                    elif event.key == pygame.K_f and game_state == "PLAYING":
                        for item in items_group:
                            if math.hypot(player.rect.centerx - item.rect.centerx, player.rect.centery - item.rect.centery) < 60:
                                if item.item_type == "potion":
                                    player.hp = min(player.max_hp, player.hp + 2)
                                    effects.add(DamageText(player.rect.centerx, player.rect.top, 2, is_heal=True))
                                    item.kill()
                                elif item.item_type == "weapon":
                                    if len(player.weapons) < player.weapon_slots:
                                        player.weapons.append(item.weapon_data)
                                        player.current_weapon = len(player.weapons) - 1
                                    else:
                                        # 如果满了，丢弃当前手里的，换上地上的
                                        items_group.add(GroundItem(player.rect.centerx, player.rect.centery, "weapon", player.weapons[player.current_weapon]))
                                        player.weapons[player.current_weapon] = item.weapon_data
                                    item.kill()
                                break  # 一次只拾取一个

        pygame.mouse.set_visible(game_state != "PLAYING")
        
        if game_state == "MENU":
            play_hover, diff_hover, intro_hover, quit_hover = draw_menu(screen, mx, my)
            screen.blit(font_base.render(f"当前难度: {difficulty_name}", True, GRAY), (SCREEN_WIDTH//2 - 60, 630))
            pygame.display.flip(); clock.tick(FPS); continue
        elif game_state == "DIFF":
            screen.fill((20,20,30)); screen.blit(font_title.render("选 择 难 度", True, WHITE), (SCREEN_WIDTH//2-120, 150))
            btn_easy = draw_button(screen, "简单 (推荐新手)", SCREEN_WIDTH//2-150, 300, 300, 60, (50,150,50), (100,200,100), mx, my)
            btn_norm = draw_button(screen, "普通 (标准体验)", SCREEN_WIDTH//2-150, 400, 300, 60, (150,100,50), (200,150,100), mx, my)
            btn_hard = draw_button(screen, "困难 (硬核狂人)", SCREEN_WIDTH//2-150, 500, 300, 60, (150,50,50), (200,100,100), mx, my)
            pygame.display.flip(); clock.tick(FPS); continue
        elif game_state == "INTRO":
            screen.fill((20,20,30))
            for i, line in enumerate(["【绝境突围：无尽肉鸽】", "操作：WASD移动，左键射击，TAB商店，1/2切武器，F键拾取。", "机制：击败敌人掉落金币，用于强化；打碎白色箱子可获取新武器。", "      由于装备栏有限，拾取新武器会丢下旧武器。", "      每过3关可选择强力天赋。每过5关将遭遇强大BOSS！"]):
                screen.blit(font_large.render(line, True, YELLOW if i==0 else WHITE), (80, 150 + i*40))
            btn_back = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 600, 200, 50, GRAY, WHITE, mx, my)
            pygame.display.flip(); clock.tick(FPS); continue

        # =======================
        # 核心战斗与更新
        # =======================
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

            camera_x, camera_y = player.rect.centerx - SCREEN_WIDTH // 2, player.rect.centery - SCREEN_HEIGHT // 2
            vision_radius = 400 if debuffs["vision_reduce"] == 0 else 150
            
            vision_tiles = vision_radius // TILE_SIZE
            pr, pc = int(player.rect.centery // TILE_SIZE), int(player.rect.centerx // TILE_SIZE)
            for r in range(max(0, pr - vision_tiles), min(MAP_ROWS, pr + vision_tiles + 1)):
                for c in range(max(0, pc - vision_tiles), min(MAP_COLS, pc + vision_tiles + 1)):
                    if math.hypot(r - pr, c - pc) <= vision_tiles + 1: explored_map[r][c] = True

            if pygame.mouse.get_pressed()[0]:
                attack_rect = player.attack(mx, my, camera_x, camera_y, bullets, enemy_bullets, effects)
                if attack_rect:
                    dmg = player.weapons[player.current_weapon]["damage"]
                    # 刀砍敌人
                    for enemy in enemies:
                        if attack_rect.colliderect(enemy.rect):
                            enemy.hp -= dmg
                            effects.add(DamageText(enemy.rect.centerx, enemy.rect.top, dmg))
                            if enemy.hp <= 0:
                                enemy.explode(enemies, player, effects); enemy.kill()
                                coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    # 刀砍木箱
                    for crate in crates:
                        if attack_rect.colliderect(crate.rect):
                            crate.take_damage(dmg, items_group, effects)

            room_info_text, room_info_color = f"第 {current_floor} 层", GREEN
            for i, room in enumerate(room_list):
                if room.is_player_inside(player.rect.centerx, player.rect.centery) and not room.cleared and not is_battle_locked:
                    current_room_index, is_battle_locked, spawn_pending = i, True, True
                    toggle_room_gates(room, close=True)
                    if current_floor % 5 == 0:
                        room.enemy_count = 0; spawners.append(SpawnerWarning(room.cx*TILE_SIZE, room.cy*TILE_SIZE))
                    else:
                        room.enemy_count += current_floor * 2
                        for _ in range(room.enemy_count - int(room.enemy_count * room.ranged_enemy_ratio)):
                            rx, ry = random.randint(room.x+1, room.x+room.w-2)*TILE_SIZE + TILE_SIZE//2, random.randint(room.y+1, room.y+room.h-2)*TILE_SIZE + TILE_SIZE//2
                            if not is_wall(rx, ry) and math.hypot(rx-player.rect.centerx, ry-player.rect.centery) > 250: spawners.append(SpawnerWarning(rx, ry))
                        for _ in range(int(room.enemy_count * room.ranged_enemy_ratio)):
                            rx, ry = random.randint(room.x+1, room.x+room.w-2)*TILE_SIZE + TILE_SIZE//2, random.randint(room.y+1, room.y+room.h-2)*TILE_SIZE + TILE_SIZE//2
                            if not is_wall(rx, ry) and math.hypot(rx-player.rect.centerx, ry-player.rect.centery) > 300: spawners.append(SpawnerWarning(rx, ry))
                    break

            if is_battle_locked:
                room_info_text, room_info_color = ("敌人接近中！", ORANGE) if spawn_pending else ("战斗中！", RED)
                for s in spawners[:]:
                    s.timer -= 1
                    if s.timer <= 0:
                        if current_floor % 5 == 0: enemies.add(Boss(s.x, s.y, 200 + current_floor*80, current_floor))
                        else:
                            if random.random() < room_list[current_room_index].ranged_enemy_ratio: enemies.add(RangedEnemy(s.x, s.y, 30 + current_floor*15, current_floor))
                            else: enemies.add(Enemy(s.x, s.y, 30 + current_floor*20, current_floor))
                        spawners.remove(s)
                if not spawners: spawn_pending = False
                if not spawn_pending and not enemies:
                    room_list[current_room_index].cleared = True; is_battle_locked = False; toggle_room_gates(room_list[current_room_index], close=False)
                    
            if all(r.cleared for r in room_list) and not portal_spawned:
                portals.add(Portal(room_list[current_room_index].cx * TILE_SIZE, room_list[current_room_index].cy * TILE_SIZE))
                portal_spawned = True
            if portal_spawned: room_info_text, room_info_color = "寻找传送门", PURPLE

            bullets.update(); enemy_bullets.update(); effects.update()
            for b in enemy_bullets:
                if is_wall(b.rect.centerx, b.rect.centery): b.kill()
            for enemy in enemies:
                if isinstance(enemy, Boss): enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets, effects, player)
                elif isinstance(enemy, RangedEnemy): enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets)
                else: enemy.update(player.rect.centerx, player.rect.centery)
            coins_group.update(player); portals.update()

            # 子弹打怪
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for b in bullet_list:
                    enemy.hp -= b.damage
                    effects.add(DamageText(enemy.rect.centerx, enemy.rect.top, b.damage))
                if enemy.hp <= 0:
                    enemy.explode(enemies, player, effects); enemy.kill()
                    coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    if random.random() < 0.4: coins_group.add(Coin(enemy.rect.centerx+15, enemy.rect.centery))
                    if isinstance(enemy, Boss):
                        for _ in range(15): coins_group.add(Coin(enemy.rect.centerx+random.randint(-40,40), enemy.rect.centery+random.randint(-40,40)))
            
            # 子弹打箱子
            hits_crates = pygame.sprite.groupcollide(crates, bullets, False, True)
            for crate, bullet_list in hits_crates.items():
                for b in bullet_list:
                    crate.take_damage(b.damage, items_group, effects)
                    
            if player.invincible_timer <= 0:
                dmg_taken = sum(e.damage for e in pygame.sprite.spritecollide(player, enemies, False))
                dmg_taken += sum(b.damage for b in pygame.sprite.spritecollide(player, enemy_bullets, True))
                if dmg_taken > 0:
                    effects.add(DamageText(player.rect.centerx, player.rect.top, dmg_taken))
                    if player.take_damage(dmg_taken): game_state, death_timer = "GAMEOVER_ANIM", pygame.time.get_ticks()

            coins += len(pygame.sprite.spritecollide(player, coins_group, True))
                
            if pygame.sprite.spritecollide(player, portals, False):
                current_floor += 1
                player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned, effects, crates, items_group = reset_floor(player)
                is_battle_locked, current_room_index, spawn_pending = False, -1, False
                if (current_floor - 1) % 3 == 0:
                    available_talents = [t for t in all_talents if t['id'] not in acquired_talents or t['id'] not in ['bounce']]
                    current_talents = random.sample(available_talents, min(3, len(available_talents)))
                    game_state = "TALENT"

        # =======================
        # 屏幕渲染
        # =======================
        if game_state in ["PLAYING", "SHOP", "TALENT", "GAMEOVER_ANIM", "GAMEOVER"]:
            screen.fill(BLACK)
            
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

            if debuffs["vision_reduce"] > 0:
                vision_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                vision_surface.fill(BLACK)
                pygame.draw.circle(vision_surface, (0,0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), vision_radius)
                vision_surface.set_colorkey((0,0,0)); screen.blit(vision_surface, (0,0))

            for s in spawners: pygame.draw.circle(screen, RED, (s.x-camera_x, s.y-camera_y), 20, 2)
            
            # 渲染实体
            for e in list(portals)+list(items_group)+list(crates)+list(coins_group)+list(enemies)+list(bullets)+list(enemy_bullets):
                screen.blit(e.image, (e.rect.x-camera_x, e.rect.y-camera_y))
            for e in enemies: e.draw_hp(screen, camera_x, camera_y)
            
            # 渲染特效
            for effect in effects: effect.draw(screen, camera_x, camera_y)

            if game_state in ["GAMEOVER_ANIM", "GAMEOVER"]: player.update(0, 0, is_dead=True)
            screen.blit(player.image, (player.rect.x-camera_x, player.rect.y-camera_y))
            
            # 渲染F键拾取提示
            if game_state == "PLAYING":
                for item in items_group:
                    if math.hypot(player.rect.centerx - item.rect.centerx, player.rect.centery - item.rect.centery) < 60:
                        item.draw_prompt(screen, camera_x, camera_y)
            
            draw_hud(screen, player); draw_minimap(screen, player)
            screen.blit(font_large.render(room_info_text, True, room_info_color), (SCREEN_WIDTH//2 - 60, 20))
            draw_weapon_bar(screen, player)

            if game_state == "PLAYING":
                pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
                pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

            if game_state == "SHOP": shop_btns, prev_hover, next_hover = draw_shop(screen, player, coins, shop_items, mx, my, shop_page)
            elif game_state == "TALENT": talent_btns = draw_talent(screen, current_talents, mx, my, acquired_talents)
            elif game_state == "GAMEOVER_ANIM" and pygame.time.get_ticks() - death_timer > 3000: game_state = "GAMEOVER"
            elif game_state == "GAMEOVER":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(200); overlay.fill(BLACK); screen.blit(overlay, (0,0))
                screen.blit(font_title.render("你 死 了", True, RED), (SCREEN_WIDTH//2-90, 200))
                screen.blit(font_large.render(f"最终抵达层数: {current_floor} | 收集金币: {coins}", True, WHITE), (SCREEN_WIDTH//2 - 150, 300))
                btn_restart = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 400, 200, 50, GRAY, WHITE, mx, my)
                btn_quit = draw_button(screen, "退出游戏", SCREEN_WIDTH//2-100, 480, 200, 50, RED, (255,100,100), mx, my)

        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    main()