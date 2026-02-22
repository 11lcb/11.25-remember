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
    final_password = ""
    pass_word = []
    for i in range(3):
        asked_letter = random_letter()
        pass_word += f'{asked_letter}'
    asked_number = random_number()
    pass_word += f'{asked_number}'

    for a in range(4):
        part = random.choice(pass_word)
        pass_word.remove(part)
        final_password += f'{part}'
    print(final_password)

password()
