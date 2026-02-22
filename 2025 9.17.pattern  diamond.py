import os
if os.name=='nt':
    os.system('')

def draw_line(offset=0, lenght=1, color=884):
    line = ' ' * lenght
    print(f'{" " * offset}\x1b[48;5;{color}m{line}\x1b[0m')

import time
def draw_diamond():
    height = 8
    center = height // 2
    offset = height // 2
    step = 1
    lenght = 1
    colors = [88, 157, 105,16,17,18,19,20,21,23,24,25,26,27]
    
    
    while True :
        
        for color in colors:
            for line in range(height):
                draw_line(offset, lenght, color)
                if line < center:
                    offset -= step
                    lenght += step * 2
                else:
                    offset += step
                    lenght -= step * 2
            print(f'\x1b[{height+2}A')
            print(f'\x1b[{offset}D')
            
            lenght = 1
            offset = height//2
            time.sleep(0.1)
           
      
draw_diamond()
