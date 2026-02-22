
import os
if os.name =='nt':
    os.system('')

def draw_line(offset=0 , length= 1, color= 88) :
    line=" "*length
    print(f"{' ' * offset}\x1b[48;5;{color}m{line}\x1b[0m")

import time

def draw_pattern():
    changdu=input("height:  ")
    a= int(changdu)

    height=a
    offset = height//2
    length=height
    colors= [16,17,18,19,20,21,23,24,25,26,27]
    step = 1
    center = height//2
    while True:
        
        for color in colors:
            for line in range(height):
                
                draw_line(offset, length,color)
                if line< center:
                    offset += 1
                    length -= step*2
                else:
                    offset -=1
                    length += step*2
                time.sleep(0.05) 
            print(f"\x1b[{height+2}A")
            print(f'\x1b[{offset}D')     
            length = height
            offset = height //2
draw_pattern()                        

            

    


 
