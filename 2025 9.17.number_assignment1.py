file =open("sequence.txt","r")
asked_number_a = []
asked_number_b = []
numbers=[]

for i in file:
    numbers.append(float(i))

length = len(numbers)
print(length)


for number in range(length):

    if number %2 ==0 :
       
        asked_number_a.append(abs(float(numbers[int(number)])))
    else:
        asked_number_b.append(abs(float(numbers[int(number)])))  
sum_a=sum(asked_number_a)
sum_b=sum(asked_number_b)

print(f'   odd:\n    {sum_a}' )
print(f'   even:\n    {sum_b}')
    

