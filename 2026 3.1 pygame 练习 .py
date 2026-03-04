import pygame
import math

pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("精致武器攻击系统")
clock = pygame.time.Clock()

# 颜色
WHITE = (255,255,255)
BLACK = (0,0,0)
RED   = (255,50,50)
BLUE  = (50,120,255)
GOLD  = (255,200,0)
GRAY  = (100,100,100)
FLASH = (255,255,100)

# 玩家
class Player:
    def __init__(self):
        self.x = W//2
        self.y = H//2
        self.speed = 6
        self.radius = 22
        self.angle = 0

        # 攻击
        self.melee_cd = 0
        self.range_cd = 0
        self.melee_swing = 0   # 挥砍动画
        self.swing_speed = 0.3

        # 武器模式
        self.mode = "melee"  # melee / range

        # ====================== 你只需要改这里 ======================
        # 把下面两行换成你的图片即可
        self.melee_img = pygame.Surface((50,10), pygame.SRCALPHA)
        pygame.draw.rect(self.melee_img, GRAY, (0,0,50,10))
        
        self.range_img = pygame.Surface((35,8), pygame.SRCALPHA)
        pygame.draw.rect(self.range_img, GRAY, (0,0,35,8))
        # ===========================================================

    def update_angle(self):
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.x, my - self.y
        self.angle = math.atan2(dy, dx)

    def move(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0,0
        if keys[pygame.K_w]: dy -=1
        if keys[pygame.K_s]: dy +=1
        if keys[pygame.K_a]: dx -=1
        if keys[pygame.K_d]: dx +=1

        if dx !=0 or dy !=0:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed
            self.y += dy * self.speed

        self.x = max(self.radius, min(W-self.radius, self.x))
        self.y = max(self.radius, min(H-self.radius, self.y))

    def attack_melee(self):
        if self.melee_cd ==0:
            self.melee_cd = 12
            self.melee_swing = 1.0

    def attack_range(self):
        if self.range_cd ==0:
            self.range_cd = 20
            bx = self.x + math.cos(self.angle)*30
            by = self.y + math.sin(self.angle)*30
            bullets.append(Bullet(bx, by, self.angle))

    def update(self):
        self.move()
        self.update_angle()
        if self.melee_cd>0: self.melee_cd -=1
        if self.range_cd>0: self.range_cd -=1
        if self.melee_swing>0: self.melee_swing -= self.swing_speed

    def draw(self):
        # 身体
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius-6)

        # 近战挥砍扇形特效
        if self.melee_swing >0:
            surf = pygame.Surface((W,H), pygame.SRCALPHA)
            fan_angle = math.radians(80)
            a1 = self.angle - fan_angle/2 * self.melee_swing
            a2 = self.angle + fan_angle/2 * self.melee_swing
            r = 90
            points = [(self.x, self.y)]
            for i in range(12):
                a = a1 + (a2-a1)*(i/11)
                points.append((self.x+math.cos(a)*r, self.y+math.sin(a)*r))
            pygame.draw.polygon(surf, (255,220,80,80), points)
            screen.blit(surf, (0,0))

        # 画武器
        weapon = self.melee_img if self.mode=="melee" else self.range_img
        rotated = pygame.transform.rotate(weapon, -math.degrees(self.angle))
        w, h = rotated.get_size()
        ox = math.cos(self.angle) * 25
        oy = math.sin(self.angle) * 25
        screen.blit(rotated, (self.x+ox-w//2, self.y+oy-h//2))

# 子弹
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 14
        self.life = 50

    def update(self):
        self.x += math.cos(self.angle)*self.speed
        self.y += math.sin(self.angle)*self.speed
        self.life -=1

    def draw(self):
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), 5)

# 游戏初始化
player = Player()
bullets = []
running = True

while running:
    screen.fill((20,20,25))
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            if player.mode == "melee":
                player.attack_melee()
            else:
                player.attack_range()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_TAB:
                player.mode = "range" if player.mode=="melee" else "melee"

    # 更新
    player.update()
    for b in bullets[:]:
        b.update()
        if b.life<=0: bullets.remove(b)

    # 绘制
    player.draw()
    for b in bullets: b.draw()

    # 提示
    font = pygame.font.SysFont(None, 26)
    mode_txt = "近战(扇形挥砍)" if player.mode=="melee" else "远程射击"
    tip = font.render(f"模式: {mode_txt}   |   TAB切换   |   鼠标攻击", True, WHITE)
    screen.blit(tip, (20,20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()