import tkinter as tk
import random
import PIL
from PIL import Image
from PIL import ImageTk

def word_solve():
    print()


def word_number():
    print()


def final_password():
    popup_1 = tk.Toplevel()
    popup_1.title('单词')
    popup_1 = tk.Label(popup_1,text='确定')
    print()


def wrong_situation():
    print()


root = tk.Tk()
root.title('password')
root.geometry('300x300')

root_label_1 = tk.Label(root,text="密钥生成模板:",fg='blue',font=("Arial",14,"bold"))
root_label_1.place(relx = 0.1, rely = 0.2)

root_label_2 = tk.Label(root,text="XXX————XXX",fg='blue',font=("Arial",13,"bold"))
root_label_2.place(relx = 0.2, rely = 0.3)

root_button_1 = tk.Button(root,text="输入单词",command = final_password,bg='blue',fg='white')
root_button_1.place(relx = 0.2, rely = 0.5)

root_button_1 = tk.Button(root,text="关闭",command = root.destroy,bg='blue',fg='white')
root_button_1.place(relx = 0.5, rely = 0.5)

root.mainloop()