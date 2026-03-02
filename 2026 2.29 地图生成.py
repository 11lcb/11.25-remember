import random
import sys

# 定义颜色常量（用于终端输出美化）
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# 玩家类
class Player:
    def __init__(self):
        self.name = "冒险者"
        self.hp = 30  # 生命值
        self.attack = 5  # 攻击力
        self.max_hp = 30

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"{Colors.RED}你受到了 {damage} 点伤害！当前生命值: {self.hp}/{self.max_hp}{Colors.RESET}")

    def attack_enemy(self, enemy):
        damage = random.randint(1, self.attack)
        enemy.take_damage(damage)
        print(f"{Colors.GREEN}你对 {enemy.name} 造成了 {damage} 点伤害！{Colors.RESET}")

    def is_alive(self):
        return self.hp > 0

# 敌人类
class Enemy:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.max_hp = hp

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"{Colors.YELLOW}{self.name} 受到了 {damage} 点伤害！剩余生命值: {self.hp}/{self.max_hp}{Colors.RESET}")

    def attack_player(self, player):
        damage = random.randint(1, self.attack)
        player.take_damage(damage)
        print(f"{Colors.RED}{self.name} 对你造成了 {damage} 点伤害！{Colors.RESET}")

    def is_alive(self):
        return self.hp > 0

# 生成随机敌人
def generate_random_enemy():
    enemies = [
        ("哥布林", 8, 2),
        ("骷髅兵", 12, 3),
        ("史莱姆", 6, 1),
        ("兽人", 18, 4),
        ("蝙蝠", 5, 1)
    ]
    enemy_choice = random.choice(enemies)
    return Enemy(enemy_choice[0], enemy_choice[1], enemy_choice[2])

# 房间探索逻辑
def explore_room(player):
    # 随机生成房间事件
    event_type = random.choice(["enemy", "empty", "heal"])
    
    if event_type == "enemy":
        enemy = generate_random_enemy()
        print(f"\n{Colors.RED}⚠️  你遇到了 {enemy.name}！准备战斗！{Colors.RESET}")
        # 战斗循环
        while player.is_alive() and enemy.is_alive():
            print("\n--- 战斗回合 ---")
            print("1. 攻击")
            print("2. 逃跑（有概率失败）")
            choice = input("请选择行动: ")
            
            if choice == "1":
                player.attack_enemy(enemy)
                if enemy.is_alive():
                    enemy.attack_player(player)
            elif choice == "2":
                escape_chance = random.random()
                if escape_chance > 0.5:
                    print(f"{Colors.BLUE}✅ 你成功逃跑了！{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}❌ 逃跑失败！{enemy.name} 趁机攻击了你！{Colors.RESET}")
                    enemy.attack_player(player)
            else:
                print(f"{Colors.YELLOW}❓ 无效的选择，{enemy.name} 攻击了你！{Colors.RESET}")
                enemy.attack_player(player)
        
        if not enemy.is_alive():
            print(f"\n{Colors.GREEN}🎉 你击败了 {enemy.name}！{Colors.RESET}")
            # 随机获得少量生命恢复
            heal_amount = random.randint(1, 3)
            player.hp += heal_amount
            if player.hp > player.max_hp:
                player.hp = player.max_hp
            print(f"{Colors.GREEN}你恢复了 {heal_amount} 点生命值，当前生命值: {player.hp}/{player.max_hp}{Colors.RESET}")
    
    elif event_type == "empty":
        print(f"\n{Colors.BLUE}🟦 这个房间空空如也，你稍作休息后继续探索。{Colors.RESET}")
    
    elif event_type == "heal":
        heal_amount = random.randint(5, 10)
        player.hp += heal_amount
        if player.hp > player.max_hp:
            player.hp = player.max_hp
        print(f"\n{Colors.GREEN}💚 你发现了治疗泉水！恢复了 {heal_amount} 点生命值！当前生命值: {player.hp}/{player.max_hp}{Colors.RESET}")

# 游戏主循环
def main():
    print(f"{Colors.BLUE}===== 简易Roguelike游戏 ====={Colors.RESET}")
    print("欢迎来到地牢探险！你的目标是尽可能探索更多房间，活下去！\n")
    
    player = Player()
    room_count = 0
    
    while player.is_alive():
        room_count += 1
        print(f"\n===== 第 {room_count} 个房间 =====")
        explore_room(player)
        
        if player.is_alive():
            continue_choice = input("\n是否继续探索下一个房间？(y/n): ")
            if continue_choice.lower() != "y":
                print(f"\n{Colors.YELLOW}你结束了探险，共探索了 {room_count} 个房间。{Colors.RESET}")
                sys.exit()
    
    print(f"\n{Colors.RED}💀 你倒下了！探险结束！你总共探索了 {room_count} 个房间。{Colors.RESET}")

if __name__ == "__main__":
    main()