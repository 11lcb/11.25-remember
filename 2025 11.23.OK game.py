import random
import tkinter as tk
from tkinter import messagebox, simpledialog

def solve_password():
    number = []
    word_slove = simpledialog.askstring("密码", "输入6个字母:", initialvalue="")
    if len(word_slove) == 6 and word_slove.isalpha():
        word = word_slove.upper()
        for i in word:
            a = ord(i) % 10
            number.append(str(a))
    
        word_list = []
        for i in word:
            word_list.append(i)        
        part_1 = []
        part_3 = []
        for i in range(3):
            pick = random.choice(word_list)
            part_1.append(pick)
            word_list.remove(pick)
        password_1 = ''.join(part_1)
        for d in word_list:
            part_3.append(d)    
        password_3 = ''.join(part_3)
        password_2 = ''.join(number)   
    
        parts = f'{password_1} {password_2} {password_3}'
        result = ''.join(parts)
        #print(result)
        
        popup = tk.Toplevel(root)
        popup.title("密钥")
        popup2 = tk.Label(
            popup, 
            text=f"密钥是：{result}",
            fg='blue', 
            font=("Arial", 14, "bold")
            )
        popup2.pack(pady=20) 

        popup3 = tk.Button(popup, text="close", command=popup.destroy)
        popup3.pack(pady=10)
        popup.geometry('200,300')
    else:
        messagebox.showwarning('warn!!','请输入六个字母的单词~~')
      
        



root = tk.Tk() 
root.title("钥匙")
root.geometry('300x300')

photo = tk.PhotoImage(file='bg_pic.png')
label_bg = tk.Label(root, image=photo)
label_bg.place(x=0, y=0, relwidth=1, relheight=1)

root_label = tk.Label(root,text='密码处理,请输入六个字母', bg='pink', 
                      font=("Arial", 16, "bold"))
root_label.place(relx = 0.04, rely = 0.15)

letter_entry = tk.Entry(root, width=5, font=('Verdana', 16))
letter_entry.insert(0, 'a')

root_button = tk.Button(root,text='输入字母',command=solve_password,bg='pink',
                                                        font=("Arial",14,"bold"))
root_button.place(relx=0.35, rely=0.4)

root_button = tk.Button(root,text='关闭', command=root.destroy, bg='pink', font=("Arial", 11, "bold"))
root_button.place(relx=0.7, rely=0.8)

root.mainloop()     