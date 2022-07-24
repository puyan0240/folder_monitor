from cProfile import label
import tkinter
from tkinter import ttk


def click_save_btn():
    pass

root = tkinter.Tk()
root.title("Folder Monitor")
root.geometry("600x400")

#Frame
frame = tkinter.Frame(root)
frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)

#部品
label = tkinter.Label(frame, text="監視するフォルダ", font=("System",12))
text  = tkinter.Text(root, height=16)
save_btn = tkinter.Button(root, text="保存", font=("System",8), command=click_save_btn)

#配置
label.grid(row=0, column=0)
text.grid(row=1, column=0)
save_btn.grid(row=2, column=0)


root.mainloop()