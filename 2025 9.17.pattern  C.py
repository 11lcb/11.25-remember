
import time
import sys

def draw_line(offset=3, color=16,long=5,long_2=0):

    black  = "\x1b[48;5;"
    nothing = "\x1b[0m"
    d= " "*2
   
    a = "  "*offset
    b= "  "* long
    c= "  "* long_2
    flush  =True
    time.sleep(0.2)
    print(f'{nothing}{a}{black}{color}m{d}{nothing}{b}{black}{color}m{d}{nothing}{c}{black}{color}m{d}{nothing}{b}{black}{color}m{d}{nothing}{a}')


def draw_pattern():
    
    print("\x1b[48;5;56m give me the length about the pattern\x1b[0m ")
    given_height=input("                                      :")
    height=int(given_height)
    
    color =16
    offset = 0
    
    long_2 =0
    
    if height%2 != 0:
        long = height-1
        for zong in range(height):
            draw_line(offset,color,long,long_2)
      
            if zong< height//2:
                offset +=1
                long -=2
                long_2 +=2
            else:
                offset -=1
                long +=2
                long_2 -=2    
    else:
        long=height
        for zong in range(height+1):
            draw_line(offset,color,long,long_2)
      
            if zong< (height+1)//2:
                offset +=1
                long -=2
                long_2 +=2
            else:
                offset -=1
                long +=2
                long_2 -=2             



if __name__ == "__main__":
    draw_pattern()