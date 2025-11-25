import tkinter as tk
import random
from tkinter import simpledialog

current_word = ""

def oka():  
    global current_word        #确定输入的单词，传输至函数处理
    word = simpledialog.askstring("check", "输入一个6个字母的单词:", 
                                 initialvalue="******")  
    if word and len(word)==6:
        current_word = word

        print(word) # 将单词转换为字母列表
       # return alright(word)
    else:
        print("六个字母的单词！！！！！！")
    
def alright(word=None):
    
    if word is None:
        word = current_word
    if not word or len(word) != 6:
        print('六个字母啊大哥！')
        return    
    
    
    # 第1块：随机3个字母
    block1 = ''.join(random.sample(word, 3))
    
    # 第2块：字母序号（个位数）
    used_letters = list(block1)
    remaining = [c for c in word if c not in used_letters]
    
    # 如果剩余字母不够3个，重新处理
    if len(remaining) < 3:
        return alright(word)  # 重新随机
    
    block3 = ''.join(remaining[3:]) if len(remaining) > 3 else ''.join(remaining)

    word_1= f'{block1}{block3}'
    A_FULE= list(word_1)

    block2_digits = [str((ord(a_fule) - 64) % 10)for a_fule in A_FULE]
    block2 = ''.join(block2_digits)


   
    
    result = f"{block1} {block2} {block3}"

    popup = tk.Toplevel(root)
    popup.title("密钥")
    popup2 = tk.Label(popup,text=f"密钥是：{result}",fg='blue',
                      font=("Arial",14,"bold"))
    popup2.pack(pady = 20) 

    popup3 = tk.Button(popup,text="close",command=popup.destroy)
    popup3.pack(pady=10)
    popup.geometry('200,300')

root= tk.Tk()
root.title("生成密钥")
root.geometry('300x300')


#bg_img = tk.PhotoImage(file='bg_pic.png')

#label_bg = tk.Label(window, image=bg_img)
#label_bg.place(x=0, y=0, relwidth=1, relheight=1)
label = tk.Label(root,text=f"单词：",fg='black',font=("Arial",14,"bold"))
label.pack(pady=3)

give_label = tk.Label(root,text=f"password:",fg='blue',
                      font=("Arial",14,"bold"))
give_label.pack(pady =1)

ok = tk.Button(root,text="输入单词",command=oka,width=10,font=("Arial",10))
ok.place(relx=0.2, rely=0.7)

final = tk.Button(root,text="生成随机密钥",command=lambda : alright(current_word),fg='blue',
                      font=("Arial",14,"bold"))
final.pack(pady =1)

button = tk.Button(root,text="done",command = root.destroy,width= 10,bg="white"
                ,fg="black",font=("Arial",10))
button.pack (pady = 30)    
button.place(relx=0.6, rely=0.7)

root.mainloop()
