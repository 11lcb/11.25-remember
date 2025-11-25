MAX_VOLUME = 4

items = {
    'a' : { 'price': 700, 'volume': 3},
    'b' : { 'price': 300, 'volume': 1},
    'c' : { 'price': 500, 'volume': 2},
    'd' : { 'price': 550, 'volume': 2},
}


def gen_table(items, max_volume=MAX_VOLUME):
    table = [[0 for c in range(max_volume)] for _ in range(len(items))]
    for i, (_, value) in enumerate(items.items()):
        price =  value['price']
        volume = value['volume']
        print("外层")
        #break
        for limit_volume in range(1, max_volume+1):
            col = limit_volume - 1
            print(i,"内层")
            #break
            if i == 0:
                table[i][col] =  0 if volume > limit_volume else price
                print(i,col,"一层")
                print(table)
                
            else:
                prev_price = table[i-1][col]
                if volume > limit_volume:
                    table[i][col] = prev_price
                    print("二层")
                    print(table)
                  
                else:

                    used =  0 if col < volume else table[i-1][col-volume]
                    #print(f'used {used} i {i} col{col} {volume} {col-volume}')
                    new_price = used + price

                    res = max(new_price, prev_price)
                    table[i][col] = res 

                    print(f' col {col}, i {i}, table {table}, prev {prev_price}, new_p {new_price} ')
                    print("二层")
       
    
    print(table)
                


if __name__ == '__main__':
    gen_table(items)