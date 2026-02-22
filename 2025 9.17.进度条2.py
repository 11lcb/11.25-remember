import time
import sys

def loading_multiple(m):
    bar = 30
    for p in range(m):
        for i in range(1, bar + 1):
            time.sleep(0.05)  
            percent = i * 100 // bar
            b=" "
            L = b * i + "0" * (bar - i)
            sys.stdout.write(f'\rTask {p+1}/{m} [{L}] {percent:3d}%')
            sys.stdout.flush()
    
        sys.stdout.write('\r' + ' ' * (50 + bar) + '\r')
        sys.stdout.flush()
    print("ALL DONE")

loading_multiple(3)