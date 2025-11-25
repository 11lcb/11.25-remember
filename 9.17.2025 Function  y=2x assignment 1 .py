height = 21
width = 21
import time

def draw_function():
    width_a = 21
    height_a = 21
    x_min , x_max = -10 , 10
    y_min , y_max = -10, 10

    
    for screen_y in range(height_a):
        line = ""
        math_y = y_max - (screen_y * (y_max - y_min))//(height_a-1)
        

        for screen_x in range(width_a):
            math_x = x_min +(screen_x * (x_max - x_min))//(width_a -1)

            y = math_x *2
 
            if abs(y - math_y)<1:
                
                line += "*"
            else :
              
                line += " "
        print(line)
        time.sleep(0.01)
        
       
   
if __name__ == "__main__":
    draw_function()
