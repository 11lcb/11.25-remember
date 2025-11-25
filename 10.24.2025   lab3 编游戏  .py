import tkinter as tk
from tkinter import messagebox
import random

 

def close():
    window.destroy()

def turns_countdown():
    global turns
    turns -=  1
    return turns

def judge():
    global word_guessed
    global used_letters
    global word_to_show

    letter = letter_entry.get()
    if len(letter) >1 or letter.isalpha() == False:
        messagebox.showwarning('look!','u need to give me a letter instead of anything else :)')
        return 0
    
    letter = letter.upper()
    letter_entry.delete(0,tk.END)

    turns_countdown()

    turns_label.configure(text=f'you have {turns} chances')
    used_letters += f'{letter}'
    used_letters_label.configure(text=f'you have used {used_letters}')

    if letter in word_guessed:
        word_buf = word_to_show
        word_to_show = ''
        for i in range(5):
            if word_guessed[i] == letter:
                word_to_show += letter
            else:
                word_to_show += word_buf[i] 
        word_label.configure(text=word_to_show) 

    if word_to_show == word_guessed:
        messagebox.showinfo("congratulations! you win!")
        window.destroy()
    if turns ==0  and word_guessed!=word_to_show:
        word_label.configure(text = word_guessed)
        messagebox.showerror("failed, lets try it again!")
        window.destroy()


def word_choose():
    with open('words.txt','r') as words_choose:
        words = []
        for i in words_choose:
            words.append(i)
        wordchosen = random.choice(words)
        return wordchosen
    

word_guessed = word_choose()[:5]
word_to_show = '*****'
turns = 35
used_letters = ''


window = tk.Tk()
window.title('My app')
window.geometry('500x350')
bg_img = tk.PhotoImage(file='bg_pic.png')

label_bg = tk.Label(window, image=bg_img)
label_bg.place(x=0, y=0, relwidth=1, relheight=1)

word_label = tk.Label(window, text='*****', font=('Consolas', 50), 
                      bg='blue', fg='white')
word_label.place(x=0, y=0, relwidth=1)

letter_label = tk.Label(window, text='your letter: ', font=('Verdana', 14))
letter_label.place(relx=0.07, rely=0.35)
letter_entry = tk.Entry(window, width=5, font=('Verdana', 16))
letter_entry.insert(0, 'a')
letter_entry.place(relx=0.7, rely=0.35)

turns_label = tk.Label(window, text=f'you have {turns} chances', font=('Verdana', 14))
turns_label.place(relx=0.07, rely=0.5)

btn_guess = tk.Button(window, text='OK', width=15, command=judge)
btn_guess.place(relx=0.07, rely=0.7)
btn_cancel = tk.Button(window, text='Cancel', width=15, command=close)
btn_cancel.place(relx=0.55, rely=0.7)

used_letters_label = tk.Label(window, text='Log:')
used_letters_label.place(relx=0.5, rely=0.9, anchor='center')

window.mainloop()
