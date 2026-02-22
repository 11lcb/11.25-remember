import tkinter as tk
import random
from PIL import Image
from PIL import ImageTk
from tkinter import simpledialog

word = ""
def punish():
    popup_3 = tk.Toplevel(root)
    class ImageViewer:
        popup_3.title("惩罚！")   
        image=Image.open('c.jpg')
        photo_1= ImageTk.PhotoImage(image)
        popup_bg = tk.Label(popup_3, image=photo_1)
        popup_bg.place(x=0, y=0, relwidth=0.95, relheight=0.95)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    b = 400 
    c = 400
    x= random.randint(0,screen_width - b)
    y= random.randint(0,screen_height - c)
    popup_3.geometry(f'{b}x{c}+{x}+{y}')    
    popup_3.after(100,punish)
    popup_3.after(2000,popup_3.destroy)

def warn():
    popup_1 = tk.Toplevel()
    class ImageViewer:
        popup_1.title("!!!")   
        image=Image.open('a.jpg')
        photo_1= ImageTk.PhotoImage(image)
        popup_bg = tk.Label(popup_1, image=photo_1)
        popup_bg.place(x=0, y=0, relwidth=1, relheight=1)
    popup_1.geometry('350x350')
    popup_label= tk.Label(popup_1,text='输入5个字母,你故意找茬是不是？',font=("Arial",14,"bold"),)
    popup_label.place(relx = 0.1 , rely = 0.22)
    
    popup_button_2 = tk.Button(popup_1,text='错了哥，我错了',command = popup_1.destroy,
                                                                font=("Arial",11,"bold"))
    popup_button_2.place(relx = 0.3, rely = 0.6)

    popup_button_2 = tk.Button(popup_1,text='错了我也不改，嘿嘿！',command = punish,
                                                                font=("Arial",10,"bold"))
    popup_button_2.place(relx = 0.27, rely = 0.8)

def change_letter(): 
    word_slove = simpledialog.askstring("密码", "输入5个字母:", 
                                 initialvalue="")
    
    if word_slove.isalpha() and len(word_slove)==5:
        word = word_slove.upper()
        part_2 = ''
        for i in word:
            letters_1 = chr(ord(i)+3)
            part_2 += letters_1 
        part_3 = ''
        for i in word:
            if ord(i) <70:
                letter_2 = chr(ord(i)+21)
                part_3 += letter_2
            else:
                letters_2 = chr(ord(i)-5)
                part_3 += letters_2 

        result = f'{word}-{part_2}-{part_3}'
        
        popup_2 = tk.Toplevel()
        class ImageViewer:
            popup_2.title("密码")   
            image=Image.open('b.jpg')
            photo_1= ImageTk.PhotoImage(image)
            popup_bg = tk.Label(popup_2, image=photo_1)
            popup_bg.place(x=0, y=0, relwidth=1, relheight=1)
        popup_2.geometry('300x300')

        popup_label_1= tk.Label(popup_2,text='结果密码：',bg='pink',font=("Arial",14,"bold"),)
        popup_label_1.place(relx = 0.1 , rely = 0.22)

        popup_label_2= tk.Label(popup_2,text=result,bg='pink',font=("Arial",14,"bold"),)
        popup_label_2.place(relx = 0.1 , rely = 0.4)
        
        popup_button = tk.Button(popup_2,text='关闭',command = popup_2.destroy,bg='pink',
                                                                font=("Arial",11,"bold"))
        popup_button.place(relx = 0.7, rely = 0.8)
        
    else:
        warn()
        print("好小子！")    
     

root= tk.Tk() 
root.title("钥匙")
root.geometry('300x300')

photo= tk.PhotoImage(file='gradient.png')
label_bg = tk.Label(root, image=photo)
label_bg.place(x=0, y=0, relwidth=1, relheight=1)

root_label = tk.Label(root,text = '密码处理,请输入五个字母', bg='pink',font=("Arial",
                                                            16,"bold"))
root_label.place(relx = 0.04, rely = 0.15)

letter_entry = tk.Entry(root, width=5, font=('Verdana', 16))
letter_entry.insert(0, 'a')

root_button = tk.Button(root,text='输入字母',command = change_letter,bg='pink',
                                                        font=("Arial",14,"bold"))
root_button.place(relx = 0.35, rely = 0.4)

root_button = tk.Button(root,text='关闭',command = root.destroy,bg='pink',font=("Arial",
                                                                11,"bold"))
root_button.place(relx = 0.7, rely = 0.8)

root.mainloop()

