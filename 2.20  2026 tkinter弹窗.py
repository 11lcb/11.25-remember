import tkinter as tk

root = tk.Tk()
root.withdraw()


popup = tk.Toplevel(root)
popup_width = 400
popup_height = 200
p1 = (root.winfo_screenwidth()-popup_width)//2-50
p2 = (root.winfo_screenheight()-popup_height)//2-100
popup.geometry(f'{popup_width}x{popup_height}+{p1}+{p2}')
label = tk.Label(popup,text="你个菜福！",bg="red",
                     fg='black',font=("Arial",50,"bold"))
label.place(relx=0.075,rely=0.25)

button = tk.Button(popup,text="关闭",command = root.destroy,width= 15,bg="white"
                ,fg="black",font=("Arial",10))   
button.place(relx=0.59, rely=0.7)

root.mainloop()