import random, tkinter as tk, time

root = tk.Tk()
root.title("射击游戏")

main_frame = tk.Frame(root)
main_frame.pack()

control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

close_button = tk.Button(control_frame, text="关闭游戏", command=root.destroy, 
                         bg="red", fg="white", width=10)
close_button.pack(side=tk.RIGHT, padx=5, pady=2)

score_label = tk.Label(control_frame, text="得分: 0", font=("Arial", 12))
score_label.pack(side=tk.LEFT, padx=5)

c = tk.Canvas(main_frame, width=600, height=400, bg='black')
c.pack()

p = c.create_rectangle(280, 350, 320, 370, fill='green')
e = []; b = []; score = 0

def move(event):
    if event.keysym == 'Left' and c.coords(p)[0] > 0: 
        c.move(p, -10, 0)
    elif event.keysym == 'Right' and c.coords(p)[2] < 600: 
        c.move(p, 10, 0)
    elif event.keysym == 'space': 
        b.append(c.create_rectangle(c.coords(p)[0]+15, 350, c.coords(p)[0]+25, 345, fill='white'))


root.bind('<Key>', move)

while True:
    if random.random() < 0.02: 
        e.append(c.create_rectangle(random.randint(0,570), 0, random.randint(30,600), 30, fill='red'))
    
    for enemy in e[:]:
        c.move(enemy, 0, 2)
        if c.coords(enemy)[1] > 400: 
            c.delete(enemy); e.remove(enemy)
    
    for bullet in b[:]:
        c.move(bullet, 0, -5)
        if c.coords(bullet)[1] < 0: 
            c.delete(bullet); b.remove(bullet)
        for enemy in e[:]:
            if (c.coords(bullet)[0] < c.coords(enemy)[2] and 
                c.coords(bullet)[2] > c.coords(enemy)[0] and
                c.coords(bullet)[1] < c.coords(enemy)[3] and 
                c.coords(bullet)[3] > c.coords(enemy)[1]):
                c.delete(enemy); e.remove(enemy)
                c.delete(bullet); b.remove(bullet)
                score += 1
                score_label.config(text=f"得分: {score}")
    
    root.update()
    time.sleep(0.02)


