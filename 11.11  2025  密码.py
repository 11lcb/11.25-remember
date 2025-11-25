import tkinter as tk
import random
from PIL import Image
from PIL import ImageTk

def random_number():
    number = []
    for i in range(0,10):
        number.append(i)
    pick_number = random.choice(number) 
    return pick_number

def random_letter():
    letter=[]
    for i in range(ord('A'),ord('Z')+1):
        letters = chr(i)
        letter.append(letters)
    pick_letter= random.choice(letter)        
    return pick_letter

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
    return final_password    

def surprise():
    popup_2 = tk.Toplevel(root)
    class ImageViewer:
        popup_2.title("彩蛋")   
        image=Image.open('a.jpg')
        photo_1= ImageTk.PhotoImage(image)
        popup_bg = tk.Label(popup_2, image=photo_1)
        popup_bg.place(x=0, y=0, relwidth=1, relheight=1)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    b = 400 
    c = 400
    x= random.randint(0,screen_width - b)
    y= random.randint(0,screen_height - c)
    popup_2.geometry(f'{b}x{c}+{x}+{y}')    
    popup_2.after(100,surprise)
    popup_2.after(2000,popup_2.destroy)

    
def four_parts():
    final = []
    for i in range(4):
        get_part=password() 
        final.append(get_part)
    result = '-'.join(final)         
    popup = tk.Toplevel(root)
    class ImageViewer:
        
        popup.geometry('300x300')
        popup.title("密钥")
    
        image=Image.open('b.jpg')
        photo_1= ImageTk.PhotoImage(image)
        popup_bg = tk.Label(popup, image=photo_1)
        popup_bg.place(x=0, y=0, relwidth=1, relheight=1)

    
   
        popup_label = tk.Label(popup,text='密钥是：',fg='black',font=("Arial",16,"bold"))
        popup_label.place(relx=0.1, rely=0.2)

        popup_label_password = tk.Label(popup,text=f'{result}',bg='pink',fg='blue',font=("Arial",
                                                                          16,"bold"))
        popup_label_password.place(relx=0.1, rely=0.4)

        popup_button_1 = tk.Button(popup,text="嘿嘿",command=surprise,fg='black',
                                font=("Arial",12,"bold"))
        popup_button_1.place(relx=0.1, rely=0.78)

        popup_button_2 = tk.Button(popup,text="关闭",command=popup.destroy,fg='black',
                                font=("Arial",12,"bold"))
        popup_button_2.place(relx=0.7, rely=0.78)
        
    
    


root=tk.Tk()
root.title('password')
root.geometry('400x360')

photo= tk.PhotoImage(file='bg_pic.png')
label_bg = tk.Label(root, image=photo)
label_bg.place(x=0, y=0, relwidth=1, relheight=1)

label= tk.Label(root,text="密钥生成器",fg='black',font=("Arial",14,"bold"))
label.pack(pady=3)

label_1= tk.Label(root,text="密钥格式：",fg='black',font=("Arial",14,"bold"))
label_1.place(relx=0.1, rely=0.2)
label_2= tk.Label(root,text="XXXX-XXXX-XXXX-XXXX",fg='black',font=("Arial",14,"bold"))
label_2.place(relx=0.1, rely=0.35)

button = tk.Button(root,text="获取密钥",command=four_parts,fg='black',font=("Arial",14,
                                                                      "bold"))
button.place(relx=0.37, rely=0.5)

button_2 = tk.Button(root,text='关闭',command=root.destroy,fg='black',font=("Arial",10,
                                                                          "bold"))
button_2.place(relx=0.7, rely=0.7)


root.mainloop()
