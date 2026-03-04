import pygame
pygame.init()

W, H = 600, 400
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

player_x = 100
player_y = 200
player_speed = 200  # 每秒移动像素   按秒算，不是按帧

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. 计算dt（秒）
    dt_ms = clock.tick(60)  # 帧耗时（毫秒）
    dt = dt_ms / 1000  # 转换为秒（比如dt=0.0167秒≈1/60）

    # 2. 玩家移动（按秒算速度，不受FPS影响）
    keys = pygame.key.get_pressed()
    anjian = pygame.key.get_pressed()
    if anjian[pygame.K_w]:
        player_y += player_speed * dt
    if anjian[pygame.K_s]:
        player_y -= player_speed * dt    

    if keys[pygame.K_d]:
        player_x += player_speed * dt  # 速度×时间=移动距离
    if keys[pygame.K_a]:
        player_x -= player_speed * dt

    # 3. 绘制玩家 + FPS           #   绘制顺序：先填背景 → 再画玩家 → 最后画文字（避免被覆盖）
    screen.fill((20, 20, 25))
    pygame.draw.circle(screen, (0,200,255), (int(player_x), int(player_y)), 20)
  # pygame.draw.circle(画布  ,     颜色    ,               圆心           , 半径)
    
    # 显示FPS和移动距离
    font = pygame.font.SysFont(None, 30)
    fps_text = font.render(f"FPS：{1000/dt_ms:.0f} | 移动速度：{player_speed}像素/秒", True, (255,255,255))
    screen.blit(fps_text, (20, 20))

    pygame.display.flip()

pygame.quit()