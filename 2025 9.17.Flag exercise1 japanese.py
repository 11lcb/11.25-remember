a='\u001b[47m'
b='\u001b[41m'
END='\u001b[0m'

line=' '*4
length=9
height=length
print(f'{a}{line*(length*2-2)}{END}')
for i in range(1,height):
    if i<=height//2:
        print(f'{a}{line*(height-i)}{b}{line*(i-1)}{b}{line*(i-1)}{a}{line*(height-i)}{END}')

    else:
        print(f'{a}{line*(i-1)}{b}{line*(height-i)}{b}{line*(height-i)}{a}{line*(i-1)}{END}')    

print(f'{a}{line*(length*2-2)}{END}'"\n"*2)
print("alright!!")

