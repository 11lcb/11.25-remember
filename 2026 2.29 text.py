import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("随机地图 + WASD移动")
clock = pygame.time.Clock()

TILE = 40
FPS = 60

# 颜色
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (120,180,120)
RED = (255,60,60)

# 生成简单地图
def generate_map(w, h):
    map_data = [[1 for _ in range(w)] for _ in range(h)]
    for y in range(2, h-2):
        for x in range(2, w-2):
            map_data[y][x] = 0
    return map_data

map_w = WIDTH // TILE
map_h = HEIGHT // TILE
map_data = generate_map(map_w, map_h)

# 玩家
player_x = TILE * 2
player_y = TILE * 2
player_size = TILE - 8
speed = 5

# 主循环
running = True
while running:
    screen.fill(WHITE)

    # 按键移动
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]: dy = -1
    if keys[pygame.K_s]: dy = 1
    if keys[pygame.K_a]: dx = -1
    if keys[pygame.K_d]: dx = 1

    # 移动
    player_x += dx * speed
    player_y += dy * speed

    # 边界
    player_x = max(0, min(player_x, WIDTH - player_size))
    player_y = max(0, min(player_y, HEIGHT - player_size))

    # 事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 画地图
    for y in range(map_h):
        for x in range(map_w):
            rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
            if map_data[y][x] == 1:
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
            else:
                pygame.draw.rect(screen, GREEN, rect)

    # 画玩家
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.rect(screen, RED, player_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()