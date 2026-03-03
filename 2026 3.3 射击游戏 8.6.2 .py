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
DARK_GRAY = (80, 80, 80)
BOSS_COLOR = (139, 0, 0)
ORANGE = (255, 165, 0)
PALE_YELLOW = (255, 255, 150)

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
    def __init__(self, x, y, damage_val, is_heal=False, custom_color=None):
        super().__init__()
        self.x, self.y = x, y
        if custom_color:
            self.color = custom_color
        else:
            self.color = GREEN if is_heal else PALE_YELLOW
        self.text = f"+{int(damage_val)}" if is_heal else f"-{int(damage_val)}"
        self.lifetime = 60
        self.timer = 0

    def update(self):
        self.timer += 1
        self.y -= 1
        if self.timer >= self.lifetime: self.kill()

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
        self.current_radius, self.alpha, self.lifetime, self.timer = 0, 255, 30, 0

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

class MeleeSwingEffect(pygame.sprite.Sprite):
    """【重构】真正的武器挥砍与剑气特效"""
    def __init__(self, start_x, start_y, attack_range, angle, weapon_img, is_skill_active):
        super().__init__()
        self.x, self.y, self.range = start_x, start_y, attack_range
        self.lifetime, self.timer = 12, 0
        self.weapon_img = weapon_img
        self.is_skill = is_skill_active
        self.angle_left = angle - math.pi/3
        self.angle_right = angle + math.pi/3

    def update(self):
        self.timer += 1
        if self.timer >= self.lifetime: self.kill()

    def draw(self, surface, camera_x, camera_y):
        s = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        progress = self.timer / self.lifetime
        current_angle = self.angle_left + (self.angle_right - self.angle_left) * progress
        alpha = int(255 * (1 - progress))
        color = (200, 100, 255, alpha) if self.is_skill else (255, 255, 255, alpha)
        
        # 1. 绘制边缘处的“剑气”弧线（攻击范围越大，剑气越远）
        arc_points = []
        for a in range(int(math.degrees(self.angle_left)), int(math.degrees(self.angle_right)) + 1, 4):
            rad = math.radians(a)
            arc_points.append((self.range + math.cos(rad) * self.range, self.range + math.sin(rad) * self.range))
        if len(arc_points) >= 2:
            pygame.draw.lines(s, color, False, arc_points, max(2, int(self.range/20)))

        # 2. 绘制旋转挥砍的武器本体（武器尺寸固定，不随范围变大而变大）
        if self.weapon_img:
            degree = math.degrees(-current_angle)
            w_img = self.weapon_img
            # 翻转逻辑：防止向左挥砍时武器图片倒置
            if math.cos(current_angle) < 0:
                w_img = pygame.transform.flip(w_img, False, True)
            rotated_img = pygame.transform.rotate(w_img, degree)
            # 武器的前端向外，根部在玩家手心
            offset = w_img.get_width() / 2 + 10 
            w_rect = rotated_img.get_rect(center=(self.range + math.cos(current_angle)*offset, self.range + math.sin(current_angle)*offset))
            s.blit(rotated_img, w_rect)

        surface.blit(s, (self.x - self.range - camera_x, self.y - self.range - camera_y))

class FlameEffect(pygame.sprite.Sprite):
    """新增：火焰喷射特效"""
    def __init__(self, start_x, start_y, attack_range, angle):
        super().__init__()
        self.x, self.y, self.range = start_x, start_y, attack_range
        self.lifetime, self.timer = 15, 0 # 留存1/4秒
        self.angle_left = angle - math.pi/4
        self.angle_right = angle + math.pi/4
        
        # 👇 🖼️👉 【替换贴图：火焰枪喷射动画】
        # 这里你需要加入 4 张连续的扇形火焰贴图序列，如果没有则会显示为淡红色的扇形！
        self.frames = load_frames(["flame1.png", "flame2.png", "flame3.png", "flame4.png"], (255, 100, 100, 0), (self.range*2, self.range*2), "rect")

    def update(self):
        self.timer += 1
        if self.timer >= self.lifetime: self.kill()

    def draw(self, surface, camera_x, camera_y):
        s = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        
        # 先画淡红色的预设扇形区域
        points = [(self.range, self.range)]
        for a in range(int(math.degrees(self.angle_left)), int(math.degrees(self.angle_right)) + 1, 2):
            rad = math.radians(a)
            points.append((self.range + math.cos(rad) * self.range, self.range + math.sin(rad) * self.range))
        if len(points) > 2: pygame.draw.polygon(s, (255, 100, 100, 120), points)
        
        # 将序列帧覆盖上去
        if self.frames and self.frames[0].get_alpha() != 0:
            frame_idx = min(int((self.timer / self.lifetime) * len(self.frames)), len(self.frames)-1)
            # 因为序列图应该是朝右的(0度)，这里要把图旋转向鼠标方向
            angle_center = self.angle_left + (self.angle_right - self.angle_left)/2
            degree = math.degrees(-angle_center)
            rotated_img = pygame.transform.rotate(self.frames[frame_idx], degree)
            img_rect = rotated_img.get_rect(center=(self.range, self.range))
            s.blit(rotated_img, img_rect)

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
            pygame.draw.circle(s, (255, 0, 0, 80), (self.radius, self.radius), int(self.radius * (self.timer / self.lifetime)))
            pygame.draw.circle(s, (255, 0, 0, 200), (self.radius, self.radius), self.radius, 2)
        else:
            pygame.draw.circle(s, (255, 0, 0, int(255 * (1 - (self.timer - self.lifetime) / 15))), (self.radius, self.radius), self.radius)
        surface.blit(s, (draw_x - self.radius, draw_y - self.radius))

# ==========================================
# 3. 辅助函数：安全加载贴图
# ==========================================
def load_frames(image_paths, fallback_color, size, shape="rect"):
    frames = []
    for path in image_paths:
        if os.path.exists(path): frames.append(pygame.transform.scale(pygame.image.load(path).convert_alpha(), size))
    if not frames:
        s = pygame.Surface(size, pygame.SRCALPHA)
        if shape == "circle": pygame.draw.circle(s, fallback_color, (size[0]//2, size[1]//2), min(size)//2)
        else: pygame.draw.rect(s, fallback_color, (0,0, size[0], size[1]), border_radius=5)
        frames.append(s)
    return frames

# ==========================================
# 4. 游戏核心类
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 👇 🖼️👉 【替换贴图：玩家角色 - 站立、死亡】
        self.idle_frames = load_frames(["角色站立.png"], GREEN, (45, 45), "circle")
        self.death_frames = load_frames(["player_death.png"], GRAY, (40, 40), "rect")
        
        # 👇 🏃👉 【优化玩家跑动动画：如果你有更流畅的跑动序列图，加在这里】
        self.run_frames = load_frames(["角色跑步1.png","角色站立.png", "角色跑步2.png"], GREEN, (45, 45), "circle")
        
        self.frames, self.current_frame, self.image = self.idle_frames, 0, self.idle_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.facing_right = True
        
        self.max_hp, self.hp, self.invincible_timer, self.speed = 5, 5, 0, 6
        self.max_shield, self.shield, self.last_shield_damage = 2, 2, 0
        
        self.weapon_slots, self.current_weapon = 2, 0
        self.weapons = [
            {"type": "pistol", "name": "普通手枪", "damage": 25, "cd": 300},
            {"type": "melee", "name": "近战小刀", "damage": 30, "range": 50, "cd": 400}
        ]
        
        self.skill_duration_max = 7 * 60  
        self.skill_cd_max = 10 * 60       
        self.skill_timer = 0
        self.skill_cd = 0
        
        self.has_bounce, self.has_magnet, self.has_explosion = False, False, False
        self.explosion_damage, self.explosion_radius = 20, 50
        self.last_shoot_time = 0
        self.melee_swing_timer = 0  # 用于隐藏挥砍时手中的静态武器

    def update(self, is_dead=False, dx=0, dy=0):
        if is_dead: self.image = self.death_frames[0]; return
        
        if self.skill_timer > 0: self.skill_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        if self.melee_swing_timer > 0: self.melee_swing_timer -= 1

        if self.shield < self.max_shield and pygame.time.get_ticks() - self.last_shield_damage > 5000:
            self.shield = min(self.max_shield, self.shield + 0.2)
        if self.invincible_timer > 0: self.invincible_timer -= 1

        if dx != 0 or dy != 0:
            self.frames = self.run_frames
            self.current_frame = (self.current_frame + 0.2) % len(self.frames)
        else:
            self.frames = self.idle_frames
            self.current_frame = 0

        self.image = self.frames[int(self.current_frame)].copy()
        if self.skill_timer > 0: self.image.fill((100, 0, 150), special_flags=pygame.BLEND_RGB_ADD)
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0: self.image.set_alpha(100)
        
        if dx > 0: self.facing_right = True
        elif dx < 0: self.facing_right = False
        
        if not self.facing_right: self.image = pygame.transform.flip(self.image, True, False)

    def activate_skill(self):
        if self.skill_cd <= 0:
            self.skill_timer = self.skill_duration_max
            self.skill_cd = self.skill_cd_max

    def take_damage(self, damage):
        damage = int(damage)
        self.last_shield_damage = pygame.time.get_ticks()
        if self.shield > 0:
            dmg_taken = min(self.shield, damage)
            self.shield -= dmg_taken
            if damage - dmg_taken > 0: self.hp -= (damage - dmg_taken)
        else: self.hp -= damage
        self.invincible_timer = 60
        return self.hp <= 0

    def switch_weapon(self, direction):
        if len(self.weapons) > 0: self.current_weapon = (self.current_weapon + direction) % len(self.weapons)

    def attack(self, mx, my, camera_x, camera_y, bullets_group, enemy_bullets_group, effects_group, global_weapon_images):
        """核心攻击重构，返回结构化伤害数据交给主循环精准计算"""
        if not self.weapons: return None
        weapon = self.weapons[self.current_weapon]
        if pygame.time.get_ticks() - self.last_shoot_time < weapon["cd"]: return None
        self.last_shoot_time = pygame.time.get_ticks()
        
        target_x, target_y = mx + camera_x, my + camera_y
        angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
        
        # 武器前端位置
        weapon_offset = 20  
        shoot_x = self.rect.centerx + math.cos(angle) * weapon_offset
        shoot_y = self.rect.centery + math.sin(angle) * weapon_offset
        
        is_skill = self.skill_timer > 0
        
        if weapon["type"] == "pistol":
            bullets_group.add(Bullet(shoot_x, shoot_y, angle, weapon["damage"], self, is_skill))
            if is_skill:
                bullets_group.add(Bullet(shoot_x, shoot_y, angle - 0.2, weapon["damage"], self, is_skill))
                bullets_group.add(Bullet(shoot_x, shoot_y, angle + 0.2, weapon["damage"], self, is_skill))
            return None # 枪的伤害由实体子弹判断
            
        elif weapon["type"] == "melee":
            self.melee_swing_timer = 12 # 隐藏手中静态武器12帧
            effects_group.add(MeleeSwingEffect(shoot_x, shoot_y, weapon["range"], angle, global_weapon_images.get(weapon["name"]), is_skill))
            # 清理敌方子弹 (粗略Rect判断即可)
            attack_rect = pygame.Rect(shoot_x - weapon["range"], shoot_y - weapon["range"], weapon["range"] * 2, weapon["range"] * 2)
            for bullet in enemy_bullets_group:
                if attack_rect.colliderect(bullet.rect): bullet.kill()
            return ("melee", shoot_x, shoot_y, angle, weapon["range"])
            
        elif weapon["type"] == "flamethrower":
            effects_group.add(FlameEffect(shoot_x, shoot_y, weapon["range"], angle))
            return ("flame", shoot_x, shoot_y, angle, weapon["range"])
            
        return None

    def draw_weapon(self, surface, camera_x, camera_y, mx, my, global_weapon_images):
        if not self.weapons or self.melee_swing_timer > 0: return # 挥动时隐藏静态武器
        weapon_name = self.weapons[self.current_weapon]["name"]
        weapon_img = global_weapon_images.get(weapon_name)
        if not weapon_img: return
        
        wx, wy = self.rect.centerx, self.rect.centery
        target_x, target_y = mx + camera_x, my + camera_y
        angle = math.atan2(target_y - wy, target_x - wx)
        degree = math.degrees(-angle)
        
        if mx < SCREEN_WIDTH // 2: weapon_img = pygame.transform.flip(weapon_img, False, True)
            
        rotated_img = pygame.transform.rotate(weapon_img, degree)
        offset = 15
        w_rect = rotated_img.get_rect(center=(wx - camera_x + math.cos(angle)*offset, wy - camera_y + math.sin(angle)*offset))
        surface.blit(rotated_img, w_rect)

# ================= 物品与箱子系统 =================
class GroundItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, weapon_data=None):
        super().__init__()
        self.item_type, self.weapon_data = item_type, weapon_data
        
        if item_type == "potion":
            self.image = load_frames(["饮料瓶.png"], (255,105,180), (45,45), "circle")[0]
        else:
            self.image = load_frames(["weapon_drop.png"], GRAY, (25,25), "rect")[0]
            
        self.rect = self.image.get_rect(center=(x, y))

    def draw_prompt(self, surface, camera_x, camera_y):
        txt = f"按F拾取 [{self.weapon_data['name']}]" if self.item_type == "weapon" else "按F拾取 [恢复血瓶]"
        surf = font_base.render(txt, True, WHITE)
        surface.blit(surf, (self.rect.centerx - camera_x - surf.get_width()//2, self.rect.y - camera_y - 25))

class Crate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_frames(["crate.png"], (160, 100, 50), (45, 45), "rect")[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 30

    def take_damage(self, amount, items_group, effects_group):
        self.hp -= int(amount)
        effects_group.add(DamageText(self.rect.centerx, self.rect.top, amount))
        if self.hp <= 0:
            self.kill()
            rand = random.random()
            if rand < 0.35:  
                # 加入了火焰枪掉落
                w_type = random.choice([
                    {"type": "pistol", "name": "强力手枪", "damage": 35, "cd": 250},
                    {"type": "melee", "name": "近战小刀", "damage": 30, "range": 50, "cd": 400},
                    {"type": "melee", "name": "大刀", "damage": 40, "range": 100, "cd": 800},
                    {"type": "pistol", "name": "机关枪", "damage": 10, "cd": 80},
                    {"type": "flamethrower", "name": "火焰枪", "damage": 5, "range": 150, "cd": 120}
                ])
                items_group.add(GroundItem(self.rect.centerx, self.rect.centery, "weapon", w_type))
            elif rand < 0.65: items_group.add(GroundItem(self.rect.centerx, self.rect.centery, "potion"))

# ================= 敌人逻辑 =================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, floor):
        super().__init__()
        self.max_hp = hp * difficulty_mult["hp"] * (1 + floor * 0.15)
        self.hp = self.max_hp
        self.speed = 2.0 + (floor * 0.2) * difficulty_mult["spd"]
        self.damage = max(1, int(1 * difficulty_mult["dmg"] * (1 + floor * 0.1)))
        
        self.frames = load_frames(["enemy_run.png"], RED, (30, 30), "circle")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.is_exploded = False
        
        # 灼烧Debuff属性
        self.burn_duration = 0
        self.burn_timer = 0

    def update(self, px, py, crates_group=None):
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            vx, vy = (dx / dist) * self.speed, (dy / dist) * self.speed
            self.rect.centerx += vx
            if is_wall(self.rect.centerx + (15 if vx>0 else -15), self.rect.centery) or (crates_group and pygame.sprite.spritecollideany(self, crates_group)):
                self.rect.centerx -= vx
            self.rect.centery += vy
            if is_wall(self.rect.centerx, self.rect.centery + (15 if vy>0 else -15)) or (crates_group and pygame.sprite.spritecollideany(self, crates_group)):
                self.rect.centery -= vy

    def draw_hp(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, BLACK, (self.rect.x - camera_x, self.rect.y - camera_y - 10, 30, 5))
        pygame.draw.rect(surface, RED, (self.rect.x - camera_x, self.rect.y - camera_y - 10, 30 * max(0, self.hp / self.max_hp), 5))

    def explode(self, enemies_group, player, effects_group):
        if self.is_exploded or not player.has_explosion: return
        self.is_exploded = True
        effects_group.add(ExplosionEffect(self.rect.centerx, self.rect.centery, player.explosion_damage))
        rect = pygame.Rect(self.rect.centerx - player.explosion_radius, self.rect.centery - player.explosion_radius, player.explosion_radius * 2, player.explosion_radius * 2)
        for enemy in enemies_group:
            if enemy != self and rect.colliderect(enemy.rect):
                enemy.hp -= player.explosion_damage
                effects_group.add(DamageText(enemy.rect.centerx, enemy.rect.top, player.explosion_damage))

class RangedEnemy(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 0.6, floor)
        self.frames = load_frames(["ranged_enemy.png"], BLUE, (25, 25), "circle")
        self.image = self.frames[0]
        self.attack_range, self.attack_cd, self.attack_timer, self.is_attacking = 400, max(80, 150 - floor * 5), 0, False

    def update(self, px, py, enemy_bullets_group=None, crates_group=None):
        dist = math.hypot(px - self.rect.centerx, py - self.rect.centery)
        self.attack_timer += 1
        if dist < self.attack_range and self.attack_timer >= self.attack_cd:
            self.is_attacking = True; self.attack_timer = 0
            if enemy_bullets_group is not None:
                enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, math.atan2(py - self.rect.centery, px - self.rect.centerx), speed=5, damage=self.damage))
        else: self.is_attacking = False
            
        if not self.is_attacking and dist > 50:
            super().update(px, py, crates_group)

class Boss(Enemy):
    def __init__(self, x, y, hp, floor):
        super().__init__(x, y, hp * 5, floor)
        self.frames = load_frames(["boss.png"], BOSS_COLOR, (100, 100), "rect")
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.shoot_timer, self.shoot_cd = 0, max(40, 100 - floor * 5)
        self.skill_timer, self.skill_cd = 0, 300
        self.dash_distance, self.aoe_radius, self.aoe_damage = 200, 120, max(3, self.damage * 2)

    def update(self, px, py, enemy_bullets_group, effects_group, player, crates_group):
        super().update(px, py, crates_group)
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cd:
            self.shoot_timer = 0
            angle = math.atan2(py - self.rect.centery, px - self.rect.centerx)
            for i in range(-3, 4):
                if i % 2 == 0: enemy_bullets_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, angle + i * 0.15, speed=6, damage=self.damage))
        
        self.skill_timer += 1
        if self.skill_timer >= self.skill_cd:
            self.skill_timer = 0
            skill_type = random.choice(["dash", "aoe", "debuff"])
            if skill_type == "dash":
                dist = math.hypot(px - self.rect.centerx, py - self.rect.centery)
                if dist > 0:
                    nx, ny = self.rect.centerx + ((px - self.rect.centerx) / dist) * self.dash_distance, self.rect.centery + ((py - self.rect.centery) / dist) * self.dash_distance
                    if not is_wall(nx, ny): self.rect.centerx, self.rect.centery = nx, ny
            elif skill_type == "aoe": 
                effects_group.add(BossAoeEffect(player.rect.centerx, player.rect.centery, self.aoe_radius, self.aoe_damage, player))
            elif skill_type == "debuff":
                if random.choice(["vision", "buff"]) == "vision": debuffs["vision_reduce"] = 300
                else: debuffs["buff_disable"] = 300

    def draw_hp(self, surface, camera_x, camera_y):
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH//2 - 250, 20, 500, 25))
        pygame.draw.rect(surface, BOSS_COLOR, (SCREEN_WIDTH//2 - 250, 20, 500 * max(0, self.hp / self.max_hp), 25))
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - 250, 20, 500, 25), 3)
        txt = font_large.render(f"【 守 门 巨 兽 】 HP: {int(max(0, self.hp))}/{int(self.max_hp)}", True, WHITE)
        surface.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 22))

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (6, 6), 6); pygame.draw.circle(self.image, YELLOW, (6, 6), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed, self.damage = speed * difficulty_mult["spd"], int(damage)
        self.vx, self.vy = math.cos(angle) * self.speed, math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.vx; self.rect.y += self.vy

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage, player, is_skill=False):
        super().__init__()
        color = PURPLE if is_skill else WHITE
        self.frames = load_frames(["bullet.png"], color, (8, 8), "circle")
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
                self.rect.centerx += (dx / dist) * 8; self.rect.centery += (dy / dist) * 8
                return
        self.rect.centery = self.base_y + math.sin(pygame.time.get_ticks() / 150 + self.time_offset) * 5

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_base = load_frames(["portal.png"], PURPLE, (50, 50), "circle")[0]
        self.image, self.rect, self.angle = self.image_base, self.image_base.get_rect(center=(x, y)), 0
    def update(self):
        self.angle = (self.angle + 3) % 360
        self.image = pygame.transform.rotate(self.image_base, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class SpawnerWarning:
    def __init__(self, x, y): self.x, self.y, self.timer = x, y, 60

# ==========================================
# 地图与系统
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
            
            is_start = len(room_list) == 0
            r = Room(x, y, w, h, is_start)
            r.ranged_enemy_ratio = min(0.7, 0.3 + floor * 0.05)
            
            if not is_start:
                for _ in range(random.randint(2, 6)):
                    ox, oy = random.randint(r.x + 2, r.x + r.w - 3), random.randint(r.y + 2, r.y + r.h - 3)
                    game_map[oy][ox] = 3
                
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
    return game_map[r][c] in [0, 2, 3]

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

def draw_hud(screen, player, skill_icon_img):
    pygame.draw.rect(screen, GRAY, (20, 20, 150, 20))
    pygame.draw.rect(screen, RED, (20, 20, 150 * max(0, player.hp/player.max_hp), 20))
    screen.blit(font_base.render(f"HP: {int(max(0, player.hp))}/{player.max_hp}", True, WHITE), (30, 22))
    
    pygame.draw.rect(screen, GRAY, (20, 50, 150, 20))
    pygame.draw.rect(screen, BLUE, (20, 50, 150 * max(0, player.shield/player.max_shield), 20))
    screen.blit(font_base.render(f"护盾: {player.shield:.1f}/{player.max_shield}", True, WHITE), (30, 52))
    screen.blit(font_large.render(f"金币: {coins}", True, YELLOW), (20, 80))
    
    icon_size = 40
    icon_x, icon_y = 30, SCREEN_HEIGHT - 80 
    
    pygame.draw.rect(screen, GRAY, (icon_x-2, icon_y-2, icon_size+4, icon_size+4), border_radius=5)
    screen.blit(skill_icon_img, (icon_x, icon_y))
    
    liquid_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    
    if player.skill_timer > 0:
        ratio = player.skill_timer / player.skill_duration_max
        h = int(icon_size * ratio)
        pygame.draw.rect(liquid_surface, (100, 200, 255, 120), (0, icon_size - h, icon_size, h))
        skill_text, color = f"[空格] 生效中: {player.skill_timer//60}s", (100, 200, 255)
    elif player.skill_cd > 0:
        ratio = player.skill_cd / player.skill_cd_max
        h = int(icon_size * ratio)
        pygame.draw.rect(liquid_surface, (255, 255, 255, 150), (0, icon_size - h, icon_size, h))
        skill_text, color = f"冷却中: {player.skill_cd//60}s", GRAY
    else:
        skill_text, color = "[空格] 技能就绪", GREEN
        
    screen.blit(liquid_surface, (icon_x, icon_y))
    txt_surf = font_base.render(skill_text, True, color)
    screen.blit(txt_surf, (icon_x + icon_size + 10, icon_y + icon_size//2 - txt_surf.get_height()//2))

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
                elif game_map[r][c] == 3: pygame.draw.rect(screen, DARK_GRAY, (start_x + c*3, start_y + r*3, 3, 3))
    px, py = int(player.rect.centerx // TILE_SIZE), int(player.rect.centery // TILE_SIZE)
    if 0 <= px < MAP_COLS and 0 <= py < MAP_ROWS: pygame.draw.rect(screen, GREEN, (start_x + px*3, start_y + py*3, 4, 4))

# ==========================================
# 6. 主程序
# ==========================================
def main():
    global clock, wall_img, floor_img, wall_inner_img, coins, current_floor, camera_x, camera_y
    
    clock = pygame.time.Clock()
    
    wall_img = load_frames(["wall.png"], (20, 20, 25), (TILE_SIZE, TILE_SIZE), "rect")[0]
    floor_img = load_frames(["floor.png"], (40, 40, 45), (TILE_SIZE, TILE_SIZE), "rect")[0]
    wall_inner_img = load_frames(["wall_inner.png"], DARK_GRAY, (TILE_SIZE, TILE_SIZE), "rect")[0]
    skill_icon_img = load_frames(["skill_icon.png"], PURPLE, (40, 40), "rect")[0]
    teleport_bg = load_frames(["teleport_bg.png"], (20, 10, 40), (SCREEN_WIDTH, SCREEN_HEIGHT), "rect")[0]

    # 👇 🖼️👉 【替换贴图：玩家手持武器图。建议画的时候枪口/刀尖朝向正右方(0度)，背景透明】
    # 加入了火焰枪的图片注册
    global_weapon_images = {
        "普通手枪": load_frames(["pistol.png"], GRAY, (30, 10), "rect")[0],
        "强力手枪": load_frames(["heavy_pistol.png"], (100,100,100), (35, 12), "rect")[0],
        "近战小刀": load_frames(["knife.png"], WHITE, (25, 8), "rect")[0],
        "大刀": load_frames(["big_sword.png"], WHITE, (50, 15), "rect")[0],
        "机关枪": load_frames(["machine_gun.png"], (80,80,80), (45, 15), "rect")[0],
        "火焰枪": load_frames(["flamethrower.png"], (255,69,0), (40, 12), "rect")[0]
    }

    game_state, coins, current_floor, difficulty_name, death_timer, acquired_talents, shop_page = "MENU", 0, 1, "普通", 0, [], 0
    boss_alive = False
    teleport_timer = 0
    
    shop_items = [
        {"id": "melee_range", "name": "提升扇形范围", "cost": 20, "level": 0, "max": 5, "cost_up": 10}, # 影响近战和喷火
        {"id": "ranged_dmg", "name": "提升远程伤害", "cost": 10, "level": 0, "max": 10, "cost_up": 5},
        {"id": "melee_dmg", "name": "提升近战伤害", "cost": 15, "level": 0, "max": 8, "cost_up": 8},
        {"id": "spd", "name": "提升移动速度", "cost": 15, "level": 0, "max": 5, "cost_up": 10},
        {"id": "fir", "name": "提升射速", "cost": 20, "level": 0, "max": 5, "cost_up": 10},
        {"id": "hp", "name": "恢复1点生命", "cost": 10, "level": 0, "max": 999, "cost_up": 0},
        {"id": "shield_max", "name": "提升护盾上限", "cost": 50, "level": 0, "max": 5, "cost_up": 20},
        {"id": "explosion", "name": "提升爆炸伤害", "cost": 40, "level": 0, "max": 5, "cost_up": 20}
    ]
    
    all_talents = [
        {"id": "bounce", "name": "反弹墙壁", "desc": "子弹触墙可反弹1次（一次性）"},
        {"id": "hp_up", "name": "生命涌动", "desc": "生命上限+2并回满血"},
        {"id": "magnet", "name": "金币磁铁", "desc": "大范围自动吸附金币"},
        {"id": "explosion", "name": "敌人爆炸", "desc": "击败敌人有概率爆炸伤害周围敌人"},
        {"id": "weapon_slot", "name": "武器栏+1", "desc": "解锁额外武器栏位"},
        {"id": "skill_up", "name": "技能专精", "desc": "主动技能持续时间翻倍"}
    ]
    current_talents = []

    def reset_floor(player_instance=None):
        sx, sy = generate_map(current_floor)
        p = Player(sx, sy) if player_instance is None else player_instance
        p.rect.center = (sx, sy)
        crates_group = pygame.sprite.Group()
        
        for r in room_list[1:]:
            for _ in range(random.randint(1, 3)):
                attempts = 0
                cx, cy = random.randint(r.x+1, r.x+r.w-2), random.randint(r.y+1, r.y+r.h-2)
                while game_map[cy][cx] != 1 and attempts < 10:
                    cx, cy = random.randint(r.x+1, r.x+r.w-2), random.randint(r.y+1, r.y+r.h-2)
                    attempts += 1
                if game_map[cy][cx] == 1:
                    crates_group.add(Crate(cx*TILE_SIZE + TILE_SIZE//2, cy*TILE_SIZE + TILE_SIZE//2))
                    
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
                elif game_state == "PORTAL_CONFIRM":
                    if btn_confirm_yes:
                        game_state = "TELEPORTING"
                        teleport_timer = pygame.time.get_ticks()
                    elif btn_confirm_no:
                        game_state = "PLAYING"
                elif game_state == "SHOP":
                    clicked = False
                    if prev_hover: shop_page -= 1; clicked = True
                    elif next_hover: shop_page += 1; clicked = True
                    for btn_rect, item, can_buy in shop_btns:
                        if btn_rect.collidepoint(mx, my) and can_buy:
                            clicked = True; coins -= item['cost']; item['level'] += 1; item['cost'] += item['cost_up']
                            if item['id'] == 'ranged_dmg':
                                for w in player.weapons:
                                    if w["type"] in ["pistol", "flamethrower"]: w["damage"] += 5
                            elif item['id'] == 'melee_dmg':
                                for w in player.weapons:
                                    if w["type"] == "melee": w["damage"] += 3
                            elif item['id'] == 'melee_range':
                                # 让火焰枪也能吃范围加成
                                for w in player.weapons:
                                    if w["type"] in ["melee", "flamethrower"]: w["range"] =  w["range"]*1.2
                            elif item['id'] == 'spd': player.speed += 1
                            elif item['id'] == 'fir':
                                for w in player.weapons: w["cd"] = max(50, w["cd"] - 40)
                            elif item['id'] == 'hp': player.hp = min(player.max_hp, player.hp + 1); item['level'] -= 1
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
                                player.weapon_slots += 1; player.weapons.append({"type": "pistol", "name": "备用手枪", "damage": 25, "cd": 250})
                            elif t['id'] == 'skill_up':
                                player.skill_duration_max *= 2
                            acquired_talents.append(t['id']); game_state = "PLAYING"
                elif game_state == "GAMEOVER" and btn_restart: game_state = "MENU"
                elif game_state == "GAMEOVER" and btn_quit: running = False

            if event.type == pygame.KEYDOWN:
                if game_state in ["PLAYING", "SHOP"]:
                    if event.key == pygame.K_TAB: shop_page = 0; game_state = "SHOP" if game_state == "PLAYING" else "PLAYING"
                    elif event.key == pygame.K_1: player.switch_weapon(-1)
                    elif event.key == pygame.K_2: player.switch_weapon(1)
                    elif event.key == pygame.K_SPACE and game_state == "PLAYING": player.activate_skill()
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
                                        items_group.add(GroundItem(player.rect.centerx, player.rect.centery, "weapon", player.weapons[player.current_weapon]))
                                        player.weapons[player.current_weapon] = item.weapon_data
                                    item.kill()
                                break 

        pygame.mouse.set_visible(game_state != "PLAYING")
        
        if game_state == "MENU":
            screen.fill((20, 20, 30))
            screen.blit(font_title.render("绝 境 突 围", True, YELLOW), (SCREEN_WIDTH//2 - 120, 150))
            play_hover = draw_button(screen, "开始游戏", SCREEN_WIDTH//2-100, 350, 200, 50, (50,150,50), (100,200,100), mx, my)
            diff_hover = draw_button(screen, "难度选择", SCREEN_WIDTH//2-100, 420, 200, 50, (150,100,50), (200,150,100), mx, my)
            intro_hover = draw_button(screen, "游戏介绍", SCREEN_WIDTH//2-100, 490, 200, 50, (50,100,150), (100,150,200), mx, my)
            quit_hover = draw_button(screen, "退出游戏", SCREEN_WIDTH//2-100, 560, 200, 50, (150,50,50), (200,100,100), mx, my)
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
            for i, line in enumerate(["【绝境突围：无尽肉鸽】", "操作：WASD移动，左键射击，TAB商店，1/2切武器，F键拾取，空格键技能。", "机制：击败敌人掉落金币，用于强化；打碎木箱可获取新武器。", "      由于装备栏有限，拾取新武器会丢下旧武器。", "      每过3关可选择强力天赋。每过5关将遭遇强大BOSS！"]):
                screen.blit(font_large.render(line, True, YELLOW if i==0 else WHITE), (60, 150 + i*40))
            btn_back = draw_button(screen, "返回主菜单", SCREEN_WIDTH//2-100, 600, 200, 50, GRAY, WHITE, mx, my)
            pygame.display.flip(); clock.tick(FPS); continue

        # =======================
        # 传送特效时间逻辑
        # =======================
        elif game_state == "TELEPORTING":
            screen.blit(teleport_bg, (0, 0))
            txt = font_title.render("传 送 中 . . .", True, WHITE)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - txt.get_height()//2))
            
            if pygame.time.get_ticks() - teleport_timer > 2000:
                current_floor += 1
                player, bullets, enemy_bullets, enemies, coins_group, portals, spawners, portal_spawned, effects, crates, items_group = reset_floor(player)
                is_battle_locked, current_room_index, spawn_pending = False, -1, False
                if (current_floor - 1) % 3 == 0:
                    available_talents = [t for t in all_talents if t['id'] not in acquired_talents or t['id'] not in ['bounce']]
                    current_talents = random.sample(available_talents, min(3, len(available_talents)))
                    game_state = "TALENT"
                else:
                    game_state = "PLAYING"
            
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

            if dx != 0:
                player.rect.centerx += dx
                if is_wall(player.rect.centerx + (15 if dx>0 else -15), player.rect.centery) or pygame.sprite.spritecollideany(player, crates): player.rect.centerx -= dx
            if dy != 0:
                player.rect.centery += dy
                if is_wall(player.rect.centerx, player.rect.centery + (15 if dy>0 else -15)) or pygame.sprite.spritecollideany(player, crates): player.rect.centery -= dy
                
            player.update(dx=dx, dy=dy)

            camera_x, camera_y = player.rect.centerx - SCREEN_WIDTH // 2, player.rect.centery - SCREEN_HEIGHT // 2
            vision_radius = 400 if debuffs["vision_reduce"] == 0 else 150
            vision_tiles = vision_radius // TILE_SIZE
            pr, pc = int(player.rect.centery // TILE_SIZE), int(player.rect.centerx // TILE_SIZE)
            for r in range(max(0, pr - vision_tiles), min(MAP_ROWS, pr + vision_tiles + 1)):
                for c in range(max(0, pc - vision_tiles), min(MAP_COLS, pc + vision_tiles + 1)):
                    if math.hypot(r - pr, c - pc) <= vision_tiles + 1: explored_map[r][c] = True

            # 【新增：精准计算扇形命中判定】
            def hit_target(target, attack_data):
                atk_type, sx, sy, atk_angle, atk_range = attack_data
                dist = math.hypot(target.rect.centerx - sx, target.rect.centery - sy)
                if dist <= atk_range:
                    ang = math.atan2(target.rect.centery - sy, target.rect.centerx - sx)
                    diff = (ang - atk_angle + math.pi) % (2*math.pi) - math.pi
                    # 近战60度半角(总120度)，火焰枪45度半角(总90度)
                    angle_limit = math.pi/3 if atk_type == "melee" else math.pi/4
                    if abs(diff) <= angle_limit:
                        return True
                return False

            if pygame.mouse.get_pressed()[0]:
                attack_data = player.attack(mx, my, camera_x, camera_y, bullets, enemy_bullets, effects, global_weapon_images)
                if attack_data:
                    atk_type = attack_data[0]
                    dmg = player.weapons[player.current_weapon]["damage"]
                    if player.skill_timer > 0: dmg *= 2 
                    
                    for enemy in enemies:
                        if hit_target(enemy, attack_data):
                            enemy.hp -= dmg
                            # 附加灼烧状态
                            if atk_type == "flame":
                                enemy.burn_duration = 180 # 4秒
                                enemy.burn_timer = 30     # 每秒触发一次
                            
                            effects.add(DamageText(enemy.rect.centerx, enemy.rect.top, dmg))
                            if enemy.hp <= 0:
                                enemy.explode(enemies, player, effects); enemy.kill()
                                coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                                
                    for crate in crates:
                        if hit_target(crate, attack_data):
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
            
            for b in list(enemy_bullets) + list(bullets):
                if is_wall(b.rect.centerx, b.rect.centery):
                    if hasattr(b, "bounces") and b.bounces > 0: pass 
                    else: b.kill()
                    
            boss_alive = False
            for enemy in enemies:
                # 【新增：结算灼烧伤害】
                if enemy.burn_duration > 0:
                    enemy.burn_duration -= 1
                    enemy.burn_timer -= 1
                    if enemy.burn_timer <= 0:
                        enemy.hp -= 20
                        enemy.burn_timer = 60
                        effects.add(DamageText(enemy.rect.centerx, enemy.rect.top, 20, custom_color=(255, 100, 0))) # 灼烧为橘红色数字
                        if enemy.hp <= 0:
                            enemy.explode(enemies, player, effects); enemy.kill()
                            coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                            if isinstance(enemy, Boss):
                                for _ in range(15): coins_group.add(Coin(enemy.rect.centerx+random.randint(-40,40), enemy.rect.centery+random.randint(-40,40)))
                
                # 如果没被烧死，继续正常逻辑
                if enemy.alive():
                    if isinstance(enemy, Boss): 
                        enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets, effects, player, crates)
                        boss_alive = True
                    elif isinstance(enemy, RangedEnemy): enemy.update(player.rect.centerx, player.rect.centery, enemy_bullets, crates)
                    else: enemy.update(player.rect.centerx, player.rect.centery, crates)
                    
            coins_group.update(player); portals.update()

            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for b in bullet_list:
                    enemy.hp -= b.damage
                    effects.add(DamageText(enemy.rect.centerx, enemy.rect.top, b.damage))
                if enemy.hp <= 0:
                    enemy.explode(enemies, player, effects); enemy.kill()
                    coins_group.add(Coin(enemy.rect.centerx, enemy.rect.centery))
                    if isinstance(enemy, Boss):
                        for _ in range(15): coins_group.add(Coin(enemy.rect.centerx+random.randint(-40,40), enemy.rect.centery+random.randint(-40,40)))
            
            hits_crates = pygame.sprite.groupcollide(crates, bullets, False, True)
            for crate, bullet_list in hits_crates.items():
                for b in bullet_list: crate.take_damage(b.damage, items_group, effects)
                    
            if player.invincible_timer <= 0:
                dmg_taken = sum(e.damage for e in pygame.sprite.spritecollide(player, enemies, False))
                dmg_taken += sum(b.damage for b in pygame.sprite.spritecollide(player, enemy_bullets, True))
                if dmg_taken > 0:
                    effects.add(DamageText(player.rect.centerx, player.rect.top, dmg_taken))
                    if player.take_damage(dmg_taken): game_state, death_timer = "GAMEOVER_ANIM", pygame.time.get_ticks()

            coins += len(pygame.sprite.spritecollide(player, coins_group, True))
            
            if pygame.sprite.spritecollide(player, portals, False):
                game_state = "PORTAL_CONFIRM"
                player.rect.centerx -= 25

        # =======================
        # 屏幕公共渲染区域
        # =======================
        if game_state in ["PLAYING", "SHOP", "TALENT", "PORTAL_CONFIRM", "GAMEOVER_ANIM", "GAMEOVER"]:
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
                    elif val == 3: screen.blit(wall_inner_img, (draw_x, draw_y))

            if debuffs["vision_reduce"] > 0:
                vs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                vs.fill(BLACK); pygame.draw.circle(vs, (0,0,0,0), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), vision_radius)
                vs.set_colorkey((0,0,0)); screen.blit(vs, (0,0))

            for s in spawners: pygame.draw.circle(screen, RED, (s.x-camera_x, s.y-camera_y), 20, 2)
            
            for e in list(portals)+list(items_group)+list(crates)+list(coins_group)+list(enemies)+list(bullets)+list(enemy_bullets):
                screen.blit(e.image, (e.rect.x-camera_x, e.rect.y-camera_y))
                
            for e in enemies:
                if not isinstance(e, Boss): e.draw_hp(screen, camera_x, camera_y)
            
            for effect in effects: effect.draw(screen, camera_x, camera_y)

            if game_state in ["GAMEOVER_ANIM", "GAMEOVER"]: player.update(is_dead=True)
            screen.blit(player.image, (player.rect.x-camera_x, player.rect.y-camera_y))
            
            player.draw_weapon(screen, camera_x, camera_y, mx, my, global_weapon_images)
            
            if game_state == "PLAYING":
                for item in items_group:
                    if math.hypot(player.rect.centerx - item.rect.centerx, player.rect.centery - item.rect.centery) < 60:
                        item.draw_prompt(screen, camera_x, camera_y)
            
            draw_hud(screen, player, skill_icon_img)
            draw_minimap(screen, player)
            
            room_info_y = 60 if boss_alive else 20
            screen.blit(font_large.render(room_info_text, True, room_info_color), (SCREEN_WIDTH//2 - 60, room_info_y))
            
            for e in enemies:
                if isinstance(e, Boss): e.draw_hp(screen, camera_x, camera_y)

            bar_bg = pygame.Rect(320, SCREEN_HEIGHT - 80, SCREEN_WIDTH - 370, 60)
            pygame.draw.rect(screen, (30,30,30), bar_bg, border_radius=10)
            pygame.draw.rect(screen, GRAY, bar_bg, 2, border_radius=10)
            slot_width = (bar_bg.width - 40) // player.weapon_slots
            for i in range(player.weapon_slots):
                slot_rect = pygame.Rect(bar_bg.x + 20 + i * slot_width, bar_bg.y + 10, slot_width - 10, 40)
                pygame.draw.rect(screen, YELLOW if i == player.current_weapon else GRAY, slot_rect, 2, border_radius=5)
                if i < len(player.weapons):
                    screen.blit(font_base.render(player.weapons[i]["name"], True, WHITE), (slot_rect.x + 5, slot_rect.y + 5))
                    screen.blit(font_base.render(f"伤害: {player.weapons[i]['damage']}", True, WHITE), (slot_rect.x + 5, slot_rect.y + 25))

            if game_state in ["PLAYING", "PORTAL_CONFIRM"]:
                pygame.draw.line(screen, WHITE, (mx-10, my), (mx+10, my), 2)
                pygame.draw.line(screen, WHITE, (mx, my-10), (mx, my+10), 2)

            if game_state == "PORTAL_CONFIRM":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(150); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
                cw, ch = 400, 200
                cx, cy = SCREEN_WIDTH//2 - cw//2, SCREEN_HEIGHT//2 - ch//2
                pygame.draw.rect(screen, (40,40,40), (cx, cy, cw, ch), border_radius=10)
                pygame.draw.rect(screen, PURPLE, (cx, cy, cw, ch), 3, border_radius=10)
                
                txt = font_large.render("是否进入下一层？", True, WHITE)
                screen.blit(txt, (cx + cw//2 - txt.get_width()//2, cy + 40))
                
                btn_confirm_yes = draw_button(screen, "是 (传送)", cx + 40, cy + 110, 120, 50, (50,150,50), (100,200,100), mx, my)
                btn_confirm_no  = draw_button(screen, "否 (留下)", cx + 240, cy + 110, 120, 50, (150,50,50), (200,100,100), mx, my)

            elif game_state == "SHOP":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(200); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
                pw, ph = 700, 500
                px, py = (SCREEN_WIDTH - pw)//2, (SCREEN_HEIGHT - ph)//2
                pygame.draw.rect(screen, (40,40,40), (px, py, pw, ph), border_radius=10)
                pygame.draw.rect(screen, YELLOW, (px, py, pw, ph), 3, border_radius=10)
                screen.blit(font_title.render("—— 神 秘 商 店 ——", True, YELLOW), (px+180, py+20))
                screen.blit(font_large.render(f"持有金币: {coins}", True, WHITE), (px+30, py+80))
                start_idx, end_idx = shop_page * 4, min((shop_page + 1) * 4, len(shop_items))
                shop_btns = []
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
                    shop_btns.append((btn_rect, item, can_buy))
                prev_hover = draw_button(screen, "上一页", px + 40, py + ph - 70, 100, 40, GRAY, WHITE, mx, my) if shop_page > 0 else False
                next_hover = draw_button(screen, "下一页", px + pw - 140, py + ph - 70, 100, 40, GRAY, WHITE, mx, my) if end_idx < len(shop_items) else False
                screen.blit(font_base.render("按 TAB 键关闭", True, GRAY), (px+300, py+ph-30))

            elif game_state == "TALENT": 
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); overlay.set_alpha(230); overlay.fill(BLACK); screen.blit(overlay, (0, 0))
                screen.blit(font_title.render("神 赐 天 赋 (三选一)", True, PURPLE), (SCREEN_WIDTH//2 - 200, 100))
                talent_btns = []
                for i, t in enumerate(current_talents):
                    bx, by = SCREEN_WIDTH//2 - 150, 250 + i * 120
                    if t['id'] in acquired_talents:
                        pygame.draw.rect(screen, GRAY, (bx, by, 300, 80), border_radius=8)
                        pygame.draw.rect(screen, WHITE, (bx, by, 300, 80), 2, border_radius=8)
                        txt_surf = font_large.render(f"{t['name']} : {t['desc']} (已获取)", True, (150,150,150))
                        screen.blit(txt_surf, (bx + 150 - txt_surf.get_width()//2, by + 40 - txt_surf.get_height()//2))
                        talent_btns.append((False, t))
                    else: talent_btns.append((draw_button(screen, f"{t['name']} : {t['desc']}", bx, by, 300, 80, (50,50,80), (80,80,120), mx, my), t))
                    
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