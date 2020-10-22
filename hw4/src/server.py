#!/usr/bin/python
# coding: utf-8

'''
1.实现网络社交程序，基于UDP协议，图形用户界面
2.服务器端保存用户信息（用户名与IP地址），客户端之间直接实现交流（聊天信息与文本文件），支持多种交流模式（一对一与一对多），保存日志信息
3.在Windows平台上实现；编程语言不限制；撰写说明文档，包括编程环境、关键问题、程序流程、测试截图等；提交程序源码、可执行文件与说明文档
'''

import os
import sys
import socket
import threading
import json
import time
import tkinter
from mylog import *
import pickle

import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk



log_fd = init_logfile('SERVER.log')

class TkGUI:
    def __init__(self, root,loged_user):

        self.root = root
        root.title("服务器 网络第四次作业 高钰洋 2120190419")
        self.loged_user = loged_user
        self.__gui_init()
        self.button_close.config(state='disabled')
        self.start_flag = False
    
    def start(self):
        self.button_start.config(state='disabled')
        try:
            port = int(self.entry_port.get())
        except:
            tkinter.messagebox.showwarning("警告","端口不合法")
            self.button_start.config(state='normal')
            return
        if port_isopen('127.0.0.1', port):

            tkinter.messagebox.showwarning("警告","端口已被占用")
            self.button_start.config(state='normal')
            return
        try:
            self.s = server(port,self.loged_user)
            self.s.sock_listen()
        except:

            tkinter.messagebox.showwarning("警告", "端口已被占用")
            self.button_start.config(state='normal')
            return
        self.button_close.config(state='normal')
        print_log(log_fd, '[Server started] IP: %s Port: %s ' % (self.s.ip,port))
        tkinter.messagebox.showinfo("成功", "服务器成功启动 ip: %s port: %s"%(self.s.ip,port))
        self.start_flag = True
        self.th = threading.Thread(target = self.update_online_list)
        self.th.setDaemon(True)
        self.th.start()


    def close(self):
        self.button_close.config(state='disabled')
        self.s.broadcast_cmd('>!' + '!quit!<')
        self.start_flag = False
        self.userlist = {}
        self.listbox_usr.delete(1, tkinter.END)
        self.s.sock_flag = False
        self.button_start.config(state='normal')
        print_log(log_fd, '[Server closed ] IP: %s Port: %s ' % (self.s.ip,self.s.port))

    def export(self):
        fname = tkinter.simpledialog.askstring("文件名","清输入导出文件名：",initialvalue='USER.JSON')
        with open(fname, "w") as f:
            f.write(json.dumps(self.loged_user,indent=4))




    def update_online_list(self):
        def refresh_usrlist():
            self.userlist_list = []
            self.listbox_usr.delete(1, tkinter.END)
            d = self.s.userlist
            self.s.userlist_L.acquire()
            for i in d:
                self.userlist_list.append(i)
                i = d[i]
                to_add_str = "  %-15s%-18s%-6s" % (i['name'], i['ip'], i['port'])
                self.listbox_usr.insert(tkinter.END, to_add_str)
            self.s.userlist_L.release()
            for i in range(len(d)):
                if not i % 2:
                    self.listbox_usr.itemconfig(i+1, bg="white")
                else:
                    self.listbox_usr.itemconfig(i+1, bg="#BFEFFF")
        while self.start_flag == True:
            refresh_usrlist()
            time.sleep(3)


    def __gui_init(self):
        # buttons
        self.button_start = tkinter.Button(self.root, text="Start", command=self.start, height=1, width=0)
        self.button_start.config(font=('MS Serif', '16', 'bold'))
        self.button_start.grid(row=1, column=0, columnspan=3, padx=3, pady=3,
                               sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_close = tkinter.Button(self.root, text="Close", command=self.close, height=1, width=0)
        self.button_close.config(font=('MS Serif', '16', 'bold'))
        self.button_close.grid(row=2, column=0, columnspan=3, padx=3, pady=3,
                               sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_export= tkinter.Button(self.root, text="Export", command=self.export, height=1, width=0)
        self.button_export.config(font=('MS Serif', '16', 'bold'))
        self.button_export.grid(row=3, column=0, columnspan=3, padx=3, pady=3,
                               sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)



        
        self.scrollbar_usr = tkinter.Scrollbar(self.root)
        self.listbox_usr = tkinter.Listbox(self.root, height=20, width=60, yscrollcommand=self.scrollbar_usr.set)
        self.listbox_usr.grid(row=0, column=3, rowspan=4, padx=15, pady=3,
                              sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)
        self.listbox_usr.config(font=('Courier New', '12'))
        self.scrollbar_usr.grid(row=0, column=3, rowspan=4, padx=0, pady=3, sticky=tkinter.N + tkinter.S + tkinter.E)
        self.scrollbar_usr.config(command=self.listbox_usr.yview)
        header = "Users            IP                Port"
        self.listbox_usr.insert(tkinter.END, header)
        self.listbox_usr.itemconfig(0, fg="white")
        self.listbox_usr.itemconfig(0, bg="black")

        
        self.label_server = tkinter.Label(self.root, text="Port:")
        self.label_server.grid(row=0, column=0, columnspan=1, ipady=3, pady=5, padx=5, sticky=tkinter.W)

        self.entry_port = tkinter.Entry(self.root, width=6)
        self.entry_port.grid(row=0, column=1, columnspan=2, ipady=3, pady=5, sticky=tkinter.E + tkinter.W)



class server:
    def __init__(self, port,loged_user):
        self.ip = get_host_ip()
        self.port = port
        self.userlist = {}
        self.userlist_L = threading.Lock()
        self.loged_user = loged_user
        self.sock_flag = False

    def sock_listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.sock_flag = True
        self.th = threading.Thread(target = self.worker)
        self.th.setDaemon(True)
        self.th.start()

    def broadcast_cmd(self, cmd):
        for i in self.userlist:
            ip = self.userlist[i]['ip']
            port = self.userlist[i]['port']
            self.sock.sendto(cmd.encode('utf-8'), (ip, int(port)))

    def send_cmd(self,cmd,ip,port):
        self.sock.sendto(cmd.encode('utf-8'), (ip, int(port)))

    def worker(self):
        while self.sock_flag == True:
            data, addr = self.sock.recvfrom(1024)
            #print "the addr:", addr
            ip = addr[0]
            port = addr[1]
            data = data.decode('utf-8')
            print(data)
            if ip == '127.0.0.1':
                ip = self.ip
            l = data.split('!')
            
            if l[0] == '$' and l[-1] == '$':
                if l[-2] == 'login':
                    if l[1]  in self.loged_user.keys() :
                        if l[2] == self.loged_user[l[1]]['pass']:
                            self.loged_user[l[1]]['ip']=ip
                            self.loged_user[l[1]]['port']=int(port)
                            newuser = {'name': l[1], 'ip': ip, 'port': int(port)}
                            self.userlist_L.acquire()
                            self.userlist[newuser['name']] = newuser
                            self.userlist_L.release()

                            print_log(log_fd, '[  User login  ] %s (%s:%s)' % (l[1], ip, port))
                            cmd_str = '>!' + newuser['name'] + '!loginok!<'
                            self.send_cmd(cmd_str, ip, int(port))
                            self.broadcast_cmd('>!' + json.dumps(self.userlist)+'!userlist!<')
                            with open(r"Logeduser.txt", "wb") as f:
                                pickle.dump(self.loged_user, f)
                        else:
                            cmd_str = '>!loginnopass!<'
                            self.send_cmd(cmd_str, ip, int(port))
                    else:
                        cmd_str = '>!loginnouser!<'
                        self.send_cmd(cmd_str, ip, int(port))
                elif l[-2] == 'reg':
                    if l[1] in self.loged_user.keys():
                        cmd_str = '>!haveuser!<'
                        self.send_cmd(cmd_str, ip, int(port))
                    else:
                        user = {'name': l[1], 'pass': l[2]}
                        print(user)
                        self.loged_user[l[1]]=user
                        with open(r"Logeduser.txt", "wb") as f:
                            pickle.dump(self.loged_user,f,protocol=0)
                        cmd_str = '>!'+user['name']+'!regok!<'
                        self.send_cmd(cmd_str, ip, int(port))
                elif l[-2] == 'keepalive':
                    user = {'name': l[1], 'ip': ip, 'port': int(port)}
                    if user['name'] not in self.userlist or self.userlist[user['name']]['ip'] != user['ip'] or self.userlist[user['name']]['port'] != user['port']:
                        self.userlist_L.acquire()
                        self.userlist[user['name']] = user
                        self.userlist_L.release()
                        print_log(log_fd, '[  User ReLogin ] %s (%s:%s)' % (l[1], ip, port))
                        print("DEBUG: %s change ip or port: (%s : %s)" % (user['name'], user['ip'], user['port']))
                        self.broadcast_cmd('>!' + json.dumps(self.userlist)+'!userlist!<')
                elif l[-2] == 'logout':
                    if l[1] in self.userlist:

                        print_log(log_fd, '[  User logout ] %s (%s:%s)' % (self.userlist[l[1]]['name'],ip, port))
                        self.userlist_L.acquire()
                        del self.userlist[l[1]]
                        self.userlist_L.release()
                        self.broadcast_cmd('>!' + json.dumps(self.userlist)+'!userlist!<')

        
        self.sock.close()

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def port_isopen(ip, port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def main():
    # with open(r"Logeduser.txt", "wb") as f:
    #     pickle.dump(dict(),f)
    # # loged_user  = None
    with open(r"Logeduser.txt", "rb") as f:
        loged_user = pickle.load(f)
        print(loged_user)
        print_log(log_fd,"[GET LOGED USER] size = %d" % len(loged_user))
    root = tkinter.Tk()
    window = TkGUI(root,loged_user)
    window.root.mainloop()

if __name__=="__main__":
    main()
