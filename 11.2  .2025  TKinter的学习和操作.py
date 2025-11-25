import tkinter as tk
import random
import time



    
def colorful_popup():
    colors=[ '#FFB6C1','#87CEEB','#98FB98','#DDA0DD'
            ,'#FFD700','#F0E68C','#E6E6FA','#B0E0E6']
    
    
    popup = tk.Toplevel(root)
    popup.title("温馨提示")
    popup.geometry("300x150")

    bg_color = random.choice(colors)
    popup.configure(bg=bg_color)

    popup.transient(root)
    popup.grab_set()

    a = "a","s","c","f","l"
    select_char = random.choice(a)

    label = tk.Label(popup,text=f"随机内容：{select_char}",bg=bg_color,
                     fg='black',font=("Arial",14,"bold"))
    label.pack(pady=30)

    button = tk.Button(popup,text="谢谢你",command = popup.destroy,bg="white"
                       ,fg="black",font=("Arial",10))
    button.pack(pady=10)

    popup.after(3000,popup.destroy)
root = tk.Tk()
root.withdraw()

def many_windows():
    for i in range(10):
        if i < 10 :
            colorful_popup()
            root.update()
            time.sleep(0.5)
            i -=1    
        
many_windows() 

root.after(100000,root.destroy)
root.mainloop()