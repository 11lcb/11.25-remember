MAX_VOLUME = 4

items = {
    'a' : { 'price': 700, 'volume': 3},
    'b' : { 'price': 300, 'volume': 1},
    'c' : { 'price': 500, 'volume': 2},
    'd' : { 'price': 550, 'volume': 2},
}


def gen_table(items, max_volume=MAX_VOLUME):
    table = [[0 for c in range(max_volume)] for _ in range(len(items))]
    for i,(key,value) in enumerate(items.items()):
        price =  value['price']
        volume = value['volume']

        for limit_volume in range(1, max_volume+1):
            col = limit_volume - 1



        print("ok")

gen_table(items, max_volume=MAX_VOLUME)        