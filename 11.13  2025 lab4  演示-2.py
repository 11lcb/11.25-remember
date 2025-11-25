import itertools

# 物品数据：名称、标识、占用空间、生存点数、是否为特殊物品(哮喘/感染时必带)
items = [
    {"name": "Винтовка", "id": "r", "space": 3, "points": 25, "special": None},
    {"name": "Пистолет", "id": "p", "space": 2, "points": 15, "special": None},
    {"name": "Боекомплект", "id": "a", "space": 2, "points": 15, "special": None},
    {"name": "Аптечка", "id": "m", "space": 2, "points": 20, "special": None},
    {"name": "Ингалятор", "id": "i", "space": 1, "points": 5, "special": "asthma"},
    {"name": "Нож", "id": "k", "space": 1, "points": 15, "special": None},
    {"name": "Топор", "id": "x", "space": 3, "points": 20, "special": None},
    {"name": "Оберег", "id": "t", "space": 1, "points": 25, "special": None},
    {"name": "Фляжка", "id": "f", "space": 1, "points": 15, "special": None},
    {"name": "Антидот", "id": "d", "space": 1, "points": 10, "special": "infected"},
    {"name": "Еда", "id": "s", "space": 2, "points": 20, "special": None},
    {"name": "Арбалет", "id": "c", "space": 2, "points": 20, "special": None}
]

# 变体参数
variants = [
    {"size": (2, 4), "disease": None, "initial_points": 15},   # 变体1
    {"size": (3, 3), "disease": "asthma", "initial_points": 10},  # 变体2
    {"size": (2, 4), "disease": "infected", "initial_points": 10}, # 变体3
    {"size": (3, 3), "disease": None, "initial_points": 15},   # 变体4
    {"size": (2, 4), "disease": "asthma", "initial_points": 20},  # 变体5
    {"size": (3, 3), "disease": "infected", "initial_points": 15}, # 变体6
    {"size": (2, 4), "disease": None, "initial_points": 15},   # 变体7
    {"size": (3, 3), "disease": "asthma", "initial_points": 15},  # 变体8
    {"size": (2, 4), "disease": "infected", "initial_points": 20}, # 变体9
    {"size": (3, 3), "disease": None, "initial_points": 10}    # 变体10
]

def calculate_total_points(selected_items, all_items, initial_points):
    """计算总生存点数"""
    total = initial_points
    
    # 所有物品的ID集合
    all_ids = {item["id"] for item in all_items}
    # 已选物品的ID集合
    selected_ids = {item["id"] for item in selected_items}
    
    # 计算总生存点数：已选物品加分，未选物品减分
    for item in all_items:
        if item["id"] in selected_ids:
            total += item["points"]
        else:
            total -= item["points"]
    
    return total

def find_best_combination(variant, items):
    """寻找最佳物品组合"""
    rows, cols = variant["size"]
    total_space = rows * cols
    disease = variant["disease"]
    initial_points = variant["initial_points"]
    
    # 必带物品
    required_items = []
    if disease == "asthma":
        # 哮喘必须带吸入器
        inhaler = next(item for item in items if item["id"] == "i")
        required_items.append(inhaler)
    elif disease == "infected":
        # 感染必须带解毒剂
        antidote = next(item for item in items if item["id"] == "d")
        required_items.append(antidote)
    
    # 必带物品占用的空间
    required_space = sum(item["space"] for item in required_items)
    
    # 剩余可用空间
    remaining_space = total_space - required_space
    if remaining_space < 0:
        return None, "无法满足必带物品的空间需求"
    
    # 可选物品（排除必带物品）
    optional_items = [item for item in items if item not in required_items]
    
    best_combination = None
    best_points = -float('inf')
    
    # 尝试不同数量的物品组合
    for k in range(0, len(optional_items) + 1):
        # 生成所有k个物品的组合
        for combo in itertools.combinations(optional_items, k):
            # 计算组合占用的空间
            combo_space = sum(item["space"] for item in combo)
            
            # 检查是否在剩余空间内
            if combo_space <= remaining_space:
                # 完整组合（必带物品+当前组合）
                full_combo = required_items + list(combo)
                
                # 计算总生存点数
                total_points = calculate_total_points(full_combo, items, initial_points)
                
                # 更新最佳组合
                if total_points > best_points and total_points > 0:
                    best_points = total_points
                    best_combination = full_combo
    
    if best_combination:
        return best_combination, best_points
    else:
        return None, "没有找到满足条件的物品组合"

def display_backpack(combination, variant, total_points):
    """以二维形式展示背包物品"""
    rows, cols = variant["size"]
    total_slots = rows * cols
    
    # 创建物品单元格列表
    item_cells = []
    for item in combination:
        # 为每个物品添加相应数量的单元格
        item_cells.extend([item["id"]] * item["space"])
    
    # 填充剩余空格
    while len(item_cells) < total_slots:
        item_cells.append(" ")
    
    # 打印背包
    print("背包内容:")
    for i in range(rows):
        start = i * cols
        end = start + cols
        row = item_cells[start:end]
        print("[{}]".format("],[".join(row)))
    
    # 打印总生存点数
    print(f"Итоговые очки выживания: {total_points}")

def solve_variant(variant_index):
    """解决指定变体的问题"""
    if 1 <= variant_index <= len(variants):
        variant = variants[variant_index - 1]
        print(f"\n=== 解决变体 {variant_index} ===")
        print(f"背包尺寸: {variant['size'][0]}x{variant['size'][1]} ({variant['size'][0]*variant['size'][1]}格)")
        print(f"健康状态: {'正常' if not variant['disease'] else '哮喘' if variant['disease'] == 'asthma' else '感染'}")
        print(f"初始生存点数: {variant['initial_points']}")
        
        combination, result = find_best_combination(variant, items)
        
        if combination:
            display_backpack(combination, variant, result)
        else:
            print(f"结果: {result}")
    else:
        print(f"无效的变体编号，请选择1到{len(variants)}之间的数字")

def solve_special_case():
    """解决附加任务：7个单元格的情况"""
    print("\n=== 解决附加任务：7个单元格的情况 ===")
    special_variant = {"size": (1, 7), "disease": None, "initial_points": 15}
    print(f"背包尺寸: 1x7 (7格)")
    print(f"健康状态: 正常")
    print(f"初始生存点数: 15")
    
    combination, result = find_best_combination(special_variant, items)
    
    if combination:
        display_backpack(combination, special_variant, result)
    else:
        print(f"结果: {result}，7个单元格可能没有可行方案")

if __name__ == "__main__":
    # 解决变体1作为示例
    solve_variant(1)
    
    # 解决附加任务
    solve_special_case()
    
    # 如需解决其他变体，可取消下面的注释
    # solve_variant(2)
    # solve_variant(3)
    # ... 以此类推