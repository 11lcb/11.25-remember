MAX_WEIGHT = 4

items = {
    'a': {'price': 700, 'weight': 3},
    'b': {'price': 700, 'weight': 3},
    'c': {'price': 500, 'weight': 2},
    'd': {'price': 550, 'weight': 2}
}

def gen_table(items, max_weight=MAX_WEIGHT):
    # 正确初始化DP表：物品数 x (容量+1)
    n = len(items)
    table = [[0 for _ in range(max_weight + 1)] for _ in range(n)]

    # 遍历每个物品
    for i, (item_name, item_info) in enumerate(items.items()):
        price = item_info['price']
        weight = item_info['weight']
        
        # 遍历每种背包容量（从1到max_weight）
        for w in range(1, max_weight + 1):
            if i == 0:  # 第一个物品
                if weight <= w:
                    table[i][w] = price
                else:
                    table[i][w] = 0
            else: # 非第一个物品
                # 不拿当前物品
                value_not_take = table[i-1][w]
                # 拿当前物品（如果能装下）
                if weight <= w:
                    value_take = price + table[i-1][w - weight]
                    table[i][w] = max(value_not_take, value_take)
                else:
                    table[i][w] = value_not_take
    return table

if __name__ == '__main__':
    dp_table = gen_table(items, MAX_WEIGHT)
    print("动态规划表 (dp[i][w])：")
    for i, row in enumerate(dp_table):
        print(f"考虑前{i+1}个物品: {row}")
    
    max_val = dp_table[-1][-1]
    print(f"\n最大价值为：{max_val}")