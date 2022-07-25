from cProfile import label
from gzip import READ
import tkinter
from tkinter import ttk
from turtle import bgcolor


monitor_flag = False

def click_monitor_btn():
    global monitor_flag

    if (monitor_flag == False):     #待機中->監視中へ
        monitor_btn['text'] = "監視中"
        monitor_btn.config(bg="RED")
        monitor_flag = True
    else:   #監視中->待機中へ
        monitor_btn["text"] = "待機中"
        monitor_btn.config(bg="GREEN")
        monitor_flag = False

def click_save_btn():
    pass

def click_reset_btn():
    pass



root = tkinter.Tk()
root.title("Folder Monitor")
root.geometry("600x400")

#Frame
frame = tkinter.Frame(root)
frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)

#部品
label = tkinter.Label(frame, text="監視フォルダ一覧", font=("System",12))
text  = tkinter.Text(root, height=16)
monitor_btn = tkinter.Button(root, text="待機中", font=("System",8), bg='GREEN', command=click_monitor_btn)
save_btn = tkinter.Button(root, text="保存", font=("System",8), command=click_save_btn)
reset_btn= tkinter.Button(root, text="取消", font=("System",8), command=click_reset_btn)

#配置
monitor_btn.grid(row=0, column=0, padx=12, pady=12 ,sticky=tkinter.S)
label.grid(row=1, column=0, padx=12, sticky=tkinter.W)
text.grid(row=2, column=0, padx=12, sticky=tkinter.W)
save_btn.grid(row=3, column=0, padx=12, pady=12, sticky=tkinter.W)
reset_btn.grid(row=3, column=0, padx=12, pady=12, sticky=tkinter.E)


root.mainloop()