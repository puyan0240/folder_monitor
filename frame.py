from dataclasses import dataclass
from http import client
import tkinter
from tkinter import E, ttk
import time
import threading
import socket
import select

monitor_flag = False
task_id = False


def monitor_task():

    server_socket =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 12345))

    try:
        readfs = set([server_socket])
        while True:
            ret, _, _ = select.select(readfs, [], [], 2)
            if len(ret) != 0:
                for sock in ret:
                    if sock == server_socket:
                        data,addr = server_socket.recvfrom(256)
                        msg = data.decode()
                        #print(msg+","+str(addr))
                        if msg == "start":
                            print("aaaaaaaaaaaa")
                        elif msg == "stop":
                            print("bbbbbbbbbbbb")
                        
            else:
                pass
                #print("a")

            #print("a")
    except Exception as e:
        print(e)


def send_cmd(msg):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = msg.encode()
    client_socket.sendto(data, ('127.0.0.1', 12345))



def click_monitor_btn():
    global monitor_flag,task_id #外部変数

    if monitor_flag == False:     #待機中->監視中へ
        monitor_btn['text'] = "監視中"  #ボタン文字変更
        monitor_btn.config(bg="RED")    #ボタン色変更
        monitor_flag = True
        send_cmd("start")

    else:   #監視中->待機中へ
        monitor_btn["text"] = "待機中"  #ボタン文字変更
        monitor_btn.config(bg="GREEN")  #ボタン色変更
        monitor_flag = False
        send_cmd("stop")

def click_save_btn():   #編集中テキストの保存
    with open('path.txt','a') as f:
        f.truncate(0)   #中身クリア
        input = text.get('1.0', tkinter.END)
        f.write(input)

def click_reset_btn():  #テキストの編集中止、保存テキストの復元
    text.delete('1.0', tkinter.END) #テキストBOXクリア
    with open('path.txt', "r+") as f:
        input = f.read()
        text.insert('1.0', input)   #テキストBOXへ書き込み


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
label.grid(row=0, column=0, padx=12, sticky=tkinter.W)
monitor_btn.grid(row=0, column=1, padx=12, sticky=tkinter.E)
text.grid(row=2, column=0, columnspan=2, padx=12, sticky=tkinter.W)
save_btn.grid(row=3, column=0, padx=12, pady=12, sticky=tkinter.W)
reset_btn.grid(row=3, column=1, padx=12, pady=12, sticky=tkinter.E)


#テキスト初期値設定:保存テキストの復元
try:
    with open('path.txt', "r") as f:
        input = f.read()
        text.insert('1.0', input)
except:
    pass    #ファイルが無い場合


#タスク生成
task_id = threading.Thread(target=monitor_task)
task_id.start() #開始


root.mainloop()