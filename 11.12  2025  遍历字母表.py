import random
def random_letter():   #遍历字母表[  ASCII码   ord()字符转数字   chr()数字转字符]
    letter=[]
    for i in range(ord('A'),ord('Z')+1):
        letters = chr(i)
        letter.append(letters)
    pick_letter= random.choice(letter)    
    return pick_letter 
  

def random_number():
    number = []
    for i in range(0,10):
        number.append(i)
    pick_number = random.choice(number)
    return pick_number

def password():
    pass_word = ""
    for i in range(3):
        asked_letter =random_letter()
        #pass_word.append(asked_letter)    #字符串不能append!
        pass_word += asked_letter
    asked_number = random_number()
    #pass_word.append(asked_number)
    pass_word += asked_number

    part = random.choice(pass_word)
    print(part)

password()