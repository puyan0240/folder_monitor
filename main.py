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
import os

PATH_FILE = 'path.txt'

monitor_flag = False
task_id = False


class monitor_event_handker(LoggingEventHandler):   #フォルダ監視イベントハンドラー
    def monitor_event(self, event):
        event_path = str(event.src_path)
        #print("編集:"+ event_path)
        with open(PATH_FILE, "r") as f:
            path_list = f.read()
            path_list = path_list.splitlines()
            #print(path_list)

            for path in path_list:
                hit_count=0
                path_part = path.split('\\')
                event_path_part = event_path.split('\\')

                for i in range(len(path_part)):
                    if path_part[i] == event_path_part[i]:
                        hit_count += 1
                    else:
                        break

                #print("hit_count:"+str(hit_count))
                if hit_count == len(path_part):
                    title = path_part[len(path_part) -1]    #直上のフォルダ名をTITL表示
                    send_cmd("stop", path)  #ポップアップ中の監視イベント発動停止

                    root.attributes("-topmost", True)   #これをするとメッセージBOXが強制前面にくる
                    if messagebox.askokcancel(title, "開きますか?"):
                        subprocess.Popen(['explorer', path])
                    send_cmd("start", path)   #監視再開
                    

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
    observer_tbl = {}

    try:
        readfs = set([server_socket])   #監視対象登録

        while True:
            ret, _, _ = select.select(readfs, [], [], 10)   #select監視、タイムアウト10sec
            if len(ret) != 0:   #受信あり??
                for sock in ret:
                    if sock == server_socket:
                        data,addr = server_socket.recvfrom(256) #データ受信
                        data = data.decode() #byte->文字列変換
                        data = data.splitlines()
                        cmd  = data[0]
                        #print("monitor_task() cmd: "+cmd)
                        if len(data) > 1:
                            path = data[1]
                            #print("monitor_task() path: "+path)
                        else:
                            path = ""

                        if cmd == "start":
                            with open(PATH_FILE, "r") as f:
                                path_list = f.read()
                                path_list = path_list.splitlines()
                                #print(path_list)

                                for path in path_list:  #登録分だけ監視設定をする
                                    path = path.replace('\n', '')   #改行コード削除
                                    #print("path:"+path)

                                    if path != "":  #設定がある場合に限り監視する
                                        try:
                                            event_handler = monitor_event_handker()
                                            observer_tbl[path] = Observer()
                                            observer_tbl[path].schedule(event_handler, path, recursive=True)  #監視登録
                                            observer_tbl[path].start()    #監視開始
                                        except:
                                            pass
                                            

                        elif cmd == "stop":
                            if path == "":
                                for observer in observer_tbl.values():
                                    observer.stop() #監視終了
                                    observer.join()
                            else:
                                observer = observer_tbl[path]
                                observer.stop() #監視終了
                                observer.join()

                        elif cmd == "end":  #タスク終了
                            for observer in observer_tbl.values():
                                if observer.is_alive() == True: #監視中??
                                    observer.stop() #監視終了
                                    observer.join()
                            return  #終了       
            else:
                pass

    except Exception as e:
        print(e)


def send_cmd(cmd, path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    #UDPソケット生成
    data = (cmd+'\n'+path).encode() #文字列->byte変換
    client_socket.sendto(data, ('127.0.0.1', 12345))    #コマンド送信
    client_socket.close()


def click_monitor_btn():
    global monitor_flag,task_id #外部変数

    if monitor_flag == False:     #待機中->監視中へ
        moni_path_write()   #テキストBOXとファイル内容を同期させる

        monitor_btn['text'] = "監視中"  #ボタン文字変更
        monitor_btn.config(bg="RED")    #ボタン色変更
        monitor_flag = True
        save_btn.config(state=tkinter.DISABLED)     #保存ボタン規制
        reset_btn.config(state=tkinter.DISABLED)    #取消ボタン規制
        text.config(state=tkinter.DISABLED) #テキストBOX規制
        send_cmd("start", "")

    else:   #監視中->待機中へ
        monitor_btn["text"] = "待機中"  #ボタン文字変更
        monitor_btn.config(bg="GREEN")  #ボタン色変更
        monitor_flag = False
        save_btn.config(state=tkinter.NORMAL)   #保存ボタン規制解除
        reset_btn.config(state=tkinter.NORMAL)  #取消ボタン規制解除
        text.config(state=tkinter.NORMAL)   #テキストBOX規制解除
        send_cmd("stop", "")


#テキストBOXとファイル内容を同期させる
def moni_path_write():

    #テキストBOXとファイル内容を取得
    if os.path.isfile(PATH_FILE) == True:  #ファイル有無を確認
        with open(PATH_FILE,'r') as f:
            input_file = f.read()
    else:
        input_file = ""
    input_text = text.get('1.0', tkinter.END+'-1c') #最後の改行コードは対象外
   
    #テキストBOXとファイル内容を比較
    if input_file != input_text:
        with open(PATH_FILE,'a') as f:
            f.truncate(0)   #ファイルの中身をクリア
            input_text = input_text.replace('/', '\\')    #文字置換(Unix系のフォルダ区切り文字'/'をwindows型に変換)
            f.write(input_text)

            #テキストBOXの内容を更新
            text.delete('1.0', tkinter.END) #テキストBOXクリア
            text.insert('1.0', input_text)   #テキストBOXへ書き込み


def click_save_btn():   #編集中テキストの保存
    moni_path_write()   #ファイルへ書き込む


def click_reset_btn():  #テキストの編集中止、保存テキストの復元
    text.delete('1.0', tkinter.END) #テキストBOXクリア
    if os.path.isfile(PATH_FILE) == True:  #ファイル有無を確認
        with open(PATH_FILE, "r+") as f:
            input = f.read()
            text.insert('1.0', input)   #テキストBOXへ書き込み


def click_close():
    #if messagebox.askokcancel("確認", "閉じますか?"):
    #    root.destroy()
    send_cmd("end", "") #タスク終了
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
    with open(PATH_FILE, "r") as f:
        input = f.read()
        text.insert('1.0', input)
except:
    pass    #ファイルが無い場合


#タスク生成
task_id = threading.Thread(target=monitor_task)
task_id.start() #開始

root.protocol("WM_DELETE_WINDOW", click_close)
root.mainloop()