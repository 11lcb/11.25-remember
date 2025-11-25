


red='\u001b[41m'
white='\u001b[47m'
blue='\u001b[44m'
a='\u001b[0m'

NUMBER=input("\n  how long about the flag :")
n=int(NUMBER)

line=' '*4
length=n
c=length%3
height= length - c

if length%3 ==0:
    print("first condition")
    for i in range(1,height+1):
        if i <= length//3:    
            print(f'{red}{line*length}{a}')
        elif length//3 < i <=(length*2)//3:
            print(f'{white}{line*length}{a}')
        elif i> (length*2)//3:
            print(f'{blue}{line*length}{a}')

else:
    print("second condition")
    for i in range(1,height+1): 
        if i <= height//3:    
            print(f'{red}{line*length}{a}')
        elif height//3 < i <=(height*2)//3:
            print(f'{white}{line*length}{a}')
        elif i> (height*2)//3:
            print(f'{blue}{line*length}{a}') 