RED=  '\033[41m'
BLUE= '\033[44m'
WHITE='\033[47m'
END='\033[0m'


line= ' '*4
length= 10
height=length

for i in range (height):
    if i <height//2:
        print(f'{BLUE}{line*(i+1)}{WHITE}{line*(length-i)}{END}')
    else:
        print(f'{BLUE}{line*(length-i)}{RED}{line*(i+1)}{END}')

#5 6 7 8  9 ->5  4 3 2 1             

