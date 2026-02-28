import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40  # 每个地图格子的像素大小
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WALL_COLOR = (70, 70, 70)       # 墙壁颜色
ROOM_COLOR = (150, 200, 150)    # 房间颜色
PATH_COLOR = (200, 200, 150)    # 通道颜色
GROUND_COLOR = (139, 69, 19)    # 地面颜色
PLATFORM_COLOR = (160, 82, 45)  # 平台颜色
PLAYER_COLOR = (255, 0, 0)      # 角色颜色
COIN_COLOR = (255, 215, 0)      # 金币颜色

# ====================== 地图生成器 ======================
class TopDownMapGenerator:
    """平面地图生成器（元气骑士风格）"""
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.WALL = 0
        self.ROOM = 1
        self.PATH = 2
        self.map_grid = [[self.WALL for _ in range(width)] for _ in range(height)]
        self.rooms = []

    def _create_room(self, x, y, w, h):
        if x + w >= self.width or y + h >= self.height or x < 1 or y < 1:
            return False
        for (rx, ry, rw, rh) in self.rooms:
            if (x < rx + rw and x + w > rx and y < ry + rh and y + h > ry):
                return False
        for i in range(y, y + h):
            for j in range(x, x + w):
                self.map_grid[i][j] = self.ROOM
        self.rooms.append((x, y, w, h))
        return True

    def _create_path(self, x1, y1, x2, y2):
        start_x, end_x = min(x1, x2), max(x1, x2)
        for x in range(start_x, end_x + 1):
            if 0 <= y1 < self.height and 0 <= x < self.width:
                self.map_grid[y1][x] = self.PATH
        start_y, end_y = min(y1, y2), max(y1, y2)
        for y in range(start_y, end_y + 1):
            if 0 <= y < self.height and 0 <= x2 < self.width:
                self.map_grid[y][x2] = self.PATH

    def generate(self):
        # 生成8-12个随机房间
        room_num = random.randint(8, 12)
        for _ in range(room_num):
            room_w = random.choice([3, 5, 7])
            room_h = random.choice([3, 5, 7])
            x = random.randint(1, self.width - room_w - 1)
            y = random.randint(1, self.height - room_h - 1)
            x = x if x % 2 == 1 else x + 1 if x + 1 < self.width - room_w else x - 1
            y = y if y % 2 == 1 else y + 1 if y + 1 < self.height - room_h else y - 1
            self._create_room(x, y, room_w, room_h)
        
        # 连接房间
        if len(self.rooms) > 1:
            for i in range(len(self.rooms) - 1):
                x1, y1, w1, h1 = self.rooms[i]
                cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
                x2, y2, w2, h2 = self.rooms[i + 1]
                cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
                self._create_path(cx1, cy1, cx2, cy2)
        return self.map_grid

class PlatformerMapGenerator:
    """横板地图生成器（马里奥风格）"""
    def __init__(self, length=40, height=15):
        self.length = length
        self.height = height
        self.AIR = 0
        self.BRICK = 1
        self.GROUND = 2
        self.COIN = 3
        self.map_grid = [[self.AIR for _ in range(length)] for _ in range(height)]

    def _create_ground(self):
        ground_y = self.height - 1
        for x in range(self.length):
            self.map_grid[ground_y][x] = self.GROUND
        
        # 随机斜坡
        slope_start = random.randint(5, self.length - 15)
        slope_height = random.randint(2, 4)
        for i in range(slope_height):
            for x in range(slope_start, slope_start + slope_height - i):
                if 0 <= ground_y - i < self.height and x < self.length:
                    self.map_grid[ground_y - i][x] = self.GROUND

    def _create_platforms(self):
        platform_num = random.randint(8, 12)
        for _ in range(platform_num):
            platform_len = random.randint(2, 6)
            platform_y = random.randint(self.height - 10, self.height - 3)
            platform_x = random.randint(0, self.length - platform_len - 1)
            
            for x in range(platform_x, platform_x + platform_len):
                self.map_grid[platform_y][x] = self.BRICK
            
            # 随机金币
            if random.random() < 0.3:
                coin_x = random.randint(platform_x, platform_x + platform_len - 1)
                if platform_y - 1 >= 0:
                    self.map_grid[platform_y - 1][coin_x] = self.COIN

    def _add_obstacles(self):
        obstacle_num = random.randint(5, 8)
        for _ in range(obstacle_num):
            obs_x = random.randint(0, self.length - 1)
            obs_y_start = random.randint(self.height - 5, self.height - 2)
            obs_height = random.randint(1, 3)
            
            for i in range(obs_height):
                if obs_y_start - i >= 0:
                    self.map_grid[obs_y_start - i][obs_x] = self.BRICK

    def generate(self):
        self._create_ground()
        self._create_platforms()
        self._add_obstacles()
        return self.map_grid

# ====================== 游戏角色 ======================
class Player:
    """游戏角色（WASD控制）"""
    def __init__(self, x, y):
        self.x = x  # 像素坐标
        self.y = y  # 像素坐标
        self.size = TILE_SIZE - 4  # 角色大小（比格子略小）
        self.speed = 5  # 移动速度
            # 按键移动
        keys = pygame.key.get_pressed()
        self.x, self.y = 0, 0
        if keys[pygame.K_w]: self.y = -1
        if keys[pygame.K_s]: self.y = 1
        if keys[pygame.K_a]: self.x = -1
        if keys[pygame.K_d]: self.x = 1

    def move(self, dx, dy, map_type, map_grid=None):
        """移动角色，带简单碰撞检测"""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # 边界检测（防止移出屏幕）
        new_x = max(0, min(new_x, SCREEN_WIDTH - self.size))
        new_y = max(0, min(new_y, SCREEN_HEIGHT - self.size))

        # 简单碰撞检测（只检测角色所在格子是否是可通行区域）
        if map_grid is not None:
            # 计算角色所在的地图格子坐标
            tile_x = int(new_x // TILE_SIZE)
            tile_y = int(new_y // TILE_SIZE)
            
            if map_type == "topdown":
                # 平面地图：墙壁不可通行
                if tile_y < len(map_grid) and tile_x < len(map_grid[0]):
                    tile_type = map_grid[tile_y][tile_x]
                    if tile_type == 0:  # 墙壁
                        return  # 不移动
            elif map_type == "platformer":
                # 横板地图：空气可通行，砖块/地面不可穿过（简单版）
                if tile_y < len(map_grid) and tile_x < len(map_grid[0]):
                    tile_type = map_grid[tile_y][tile_x]
                    if tile_type in [1, 2]:  # 砖块/地面
                        return  # 不移动

        self.x = new_x
        self.y = new_y

# ====================== 游戏主类 ======================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("随机地图 + WASD角色控制")
        self.clock = pygame.time.Clock()
        self.running = True

        # 初始化地图和角色
        self.map_mode = "topdown"  # 默认平面地图模式
        self.topdown_generator = TopDownMapGenerator(
            width=SCREEN_WIDTH//TILE_SIZE,
            height=SCREEN_HEIGHT//TILE_SIZE
        )
        self.platform_generator = PlatformerMapGenerator(
            length=SCREEN_WIDTH//TILE_SIZE,
            height=SCREEN_HEIGHT//TILE_SIZE
        )
        self.current_map = self.topdown_generator.generate()
        self.player = Player(TILE_SIZE * 2, TILE_SIZE * 2)  # 初始位置

    def draw_topdown_map(self):
        """绘制平面地图"""
        for y in range(len(self.current_map)):
            for x in range(len(self.current_map[0])):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.current_map[y][x] == 0:  # 墙壁
                    pygame.draw.rect(self.screen, WALL_COLOR, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)  # 边框
                elif self.current_map[y][x] == 1:  # 房间
                    pygame.draw.rect(self.screen, ROOM_COLOR, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
                elif self.current_map[y][x] == 2:  # 通道
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_platform_map(self):
        """绘制横板地图"""
        for y in range(len(self.current_map)):
            for x in range(len(self.current_map[0])):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.current_map[y][x] == 0:  # 空气
                    continue
                elif self.current_map[y][x] == 1:  # 砖块/平台
                    pygame.draw.rect(self.screen, PLATFORM_COLOR, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
                elif self.current_map[y][x] == 2:  # 地面
                    pygame.draw.rect(self.screen, GROUND_COLOR, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
                elif self.current_map[y][x] == 3:  # 金币
                    pygame.draw.circle(self.screen, COIN_COLOR, 
                                     (x*TILE_SIZE + TILE_SIZE//2, y*TILE_SIZE + TILE_SIZE//2), 
                                     TILE_SIZE//4)

    def draw_player(self):
        """绘制角色"""
        player_rect = pygame.Rect(
            self.player.x, self.player.y,
            self.player.size, self.player.size
        )
        pygame.draw.rect(self.screen, PLAYER_COLOR, player_rect)
        # 绘制角色中心点（方便观察）
        pygame.draw.circle(self.screen, BLACK, 
                         (int(self.player.x + self.player.size//2), 
                          int(self.player.y + self.player.size//2)), 
                         3)

    def handle_events(self):
        """处理键盘和窗口事件"""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # WASD移动
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        
        # 移动角色
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.map_mode, self.current_map)

        # 事件循环
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # 按1切换到平面地图，按2切换到横板地图
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.map_mode = "topdown"
                    self.current_map = self.topdown_generator.generate()
                    self.player = Player(TILE_SIZE * 2, TILE_SIZE * 2)  # 重置角色位置
                if event.key == pygame.K_2:
                    self.map_mode = "platformer"
                    self.current_map = self.platform_generator.generate()
                    self.player = Player(TILE_SIZE * 2, TILE_SIZE * 2)  # 重置角色位置

    def run(self):
        """游戏主循环"""
        while self.running:
            # 处理事件
            self.handle_events()

            # 绘制背景
            self.screen.fill(WHITE)

            # 绘制地图
            if self.map_mode == "topdown":
                self.draw_topdown_map()
            else:
                self.draw_platform_map()

            # 绘制角色
            self.draw_player()

            # 更新屏幕
            pygame.display.flip()
            self.clock.tick(FPS)

        # 退出游戏
        pygame.quit()
        sys.exit()

# ====================== 运行游戏 ======================
if __name__ == "__main__":
    game = Game()
    game.run()