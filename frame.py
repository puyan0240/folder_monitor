import tkinter
from tkinter import E, ttk, messagebox
import time
import threading
import socket
import select
#import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import subprocess

monitor_flag = False
task_id = False


class monitor_event_handker(LoggingEventHandler):   #フォルダ監視イベントハンドラー
    def monitor_event(self, event):
        print("編集:"+ event.src_path)
        with open('path.txt', "r") as f:
            path = f.read()
            path = path.replace('\n', '')   #改行コード削除
            send_cmd("stop")    #ポップアップ中の監視イベント発動停止
            if messagebox.askokcancel("Folder Monitor", "開きますか?"):
                subprocess.Popen(['explorer', path])
            send_cmd("start")   #監視再開

    def on_any_event(self, event):
        return
    def on_closed(self, event):
        return
    def on_created(self, event):
        self.monitor_event(event)
    def on_modified(self, event):
        return
    def on_moved(self, event):
        self.monitor_event(event)


def monitor_task():

    server_socket =socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDPソケット生成
    server_socket.bind(('127.0.0.1', 12345))

    try:
        readfs = set([server_socket])   #監視対象登録

        while True:
            ret, _, _ = select.select(readfs, [], [], 10)   #select監視、タイムアウト10sec
            if len(ret) != 0:   #受信あり??
                for sock in ret:
                    if sock == server_socket:
                        data,addr = server_socket.recvfrom(256) #データ受信
                        msg = data.decode() #byte->文字列変換

                        print("monitor_task() msg: "+msg)

                        if msg == "start":
                            with open('path.txt', "r") as f:
                                path = f.read()
                                path = path.replace('\n', '')   #改行コード削除
                                #logging.basicConfig(level=logging.INFO,
                                #                format='%(asctime)s - %(message)s',
                                #                datefmt='%Y-%m-%d %H:%M:%S')
                                event_handler = monitor_event_handker()
                                observer = Observer()
                                observer.schedule(event_handler, path, recursive=True)  #監視登録
                                observer.start()    #監視開始

                        elif msg == "stop":
                            observer.stop() #監視終了
                            observer.join()

                        elif msg == "end":  #タスク終了
                            if observer.is_alive() == True: #監視中??
                                observer.stop() #監視終了
                                observer.join()
                            return  #終了       
            else:
                pass
                #print("a")

            #print("a")
    except Exception as e:
        print(e)


def send_cmd(msg):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    #UDPソケット生成
    data = msg.encode() #文字列->byte変換
    client_socket.sendto(data, ('127.0.0.1', 12345))    #コマンド送信



def click_monitor_btn():
    global monitor_flag,task_id #外部変数

    if monitor_flag == False:     #待機中->監視中へ
        monitor_btn['text'] = "監視中"  #ボタン文字変更
        monitor_btn.config(bg="RED")    #ボタン色変更
        monitor_flag = True
        save_btn.config(state=tkinter.DISABLED)     #保存ボタン規制
        reset_btn.config(state=tkinter.DISABLED)    #取消ボタン規制
        text.config(state=tkinter.DISABLED) #テキストBOX規制
        send_cmd("start")

    else:   #監視中->待機中へ
        monitor_btn["text"] = "待機中"  #ボタン文字変更
        monitor_btn.config(bg="GREEN")  #ボタン色変更
        monitor_flag = False
        save_btn.config(state=tkinter.NORMAL)   #保存ボタン規制解除
        reset_btn.config(state=tkinter.NORMAL)  #取消ボタン規制解除
        text.config(state=tkinter.NORMAL)   #テキストBOX規制解除
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


def click_close():
    #if messagebox.askokcancel("確認", "閉じますか?"):
    #    root.destroy()
    send_cmd("end") #タスク終了
    task_id.join()  #タスク終了を待つ
    root.destroy()  #ウィンドウを破棄する


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

root.protocol("WM_DELETE_WINDOW", click_close)
root.mainloop()