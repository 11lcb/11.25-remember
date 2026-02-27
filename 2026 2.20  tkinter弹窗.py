import tkinter as tk

root = tk.Tk()
root.withdraw()

score = 120

popup = tk.Toplevel(root)
popup_width = 400
popup_height = 300
p1 = (root.winfo_screenwidth()-popup_width)//2-50
p2 = (root.winfo_screenheight()-popup_height)//2-100
popup.geometry(f'{popup_width}x{popup_height}+{p1}+{p2}')
label = tk.Label(popup,text="可惜，你还得练！",bg="pink",
                     fg='black',font=("Arial",30,"bold"))
label.place(relx=0.075,rely=0.35)

label_1 = tk.Label(popup,text=f"你的得分是： {score}",bg="pink",
                     fg='black',font=("Arial",25,"bold"))
label_1.place(relx=0.075,rely=0.15)

button = tk.Button(popup,text="关闭",command = root.destroy,width= 15,bg="pink"
                ,fg="black",font=("Arial",10))   
button.place(relx=0.59, rely=0.7)

root.mainloop()