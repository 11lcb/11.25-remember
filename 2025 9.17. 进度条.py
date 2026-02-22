import time
import sys
a="\033["

def loading(num_tasks):
    bar_width=51
    for i in range (1,num_tasks+1):
        for n in range(0, bar_width):
            filled=n
            bar= "s"*filled +"b"*(bar_width - filled)
            print(f'\r {a}K {i}/{num_tasks} [{bar}] {n:3d}%', end="", flush=True)
            time.sleep(0.07)
    p= bar_width+20   
    print(f"\r {a}k {' '*p} \r finished")    

if __name__== '__main__':
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    loading(m)                      