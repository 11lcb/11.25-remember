
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PIL + tkinter 图片显示")
        
        # 使用PIL打开图片
        self.image = Image.open("a.jpg")  # 替换为你的图片路径
        
        # 调整图片大小（可选）
        self.image = self.image.resize((400, 300), Image.Resampling.LANCZOS)
        
        # 转换为tkinter可用的PhotoImage
        self.photo = ImageTk.PhotoImage(self.image)
        
        # 创建标签显示图片
        self.label = ttk.Label(root, image=self.photo)
        self.label.pack(padx=10, pady=10)
        
        # 添加按钮示例
        self.button = ttk.Button(root, text="关闭", command=root.quit)
        self.button.pack(pady=5)


root = tk.Tk()
app = ImageViewer(root)
root.mainloop()


      