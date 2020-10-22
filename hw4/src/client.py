#!/usr/bin/python
# coding: utf-8



import os
import sys
import json
import socket
import random
import threading
import time
import tkinter
import operator

from mylog import *
import tkinter.filedialog
import tkinter.messagebox
import importlib






class TkGUI:
    def __init__(self, root):
        self.L = threading.Lock()
        self.root = root
        root.title("客户端 第四次作业 高钰洋2120190419")
        root.configure(background="CadetBlue")
        self.skinIdx = 0
        self.skin_list = ["CadetBlue", "Turquoise", "lightBlue", "lightgreen", "lightyellow", "Pink", "lightCyan",
                          "Goldenrod", "Tan", "Gainsboro"
            , "PeachPuff", "Lavender"]
        self.__gui_init()
        self.button_logout.config(state="disabled")
        self.login_flag = False
        self.sendFile=False


    def server_cmd(self, cmd):
        login_str = '$!' + self.me.name + '!' + cmd + '!$'
        self.me.sock.sendto(login_str.encode('utf-8'), (self.me.server_ip, self.me.server_port))
        return True


    def login_click(self):
        self.login_th = threading.Thread(target=self.login)
        self.login_th.setDaemon(True)
        self.login_th.start()

    def login(self):
        def restore_state():
            self.L.acquire()
            self.entry_name.config(state="normal")
            self.entry_server_port.config(state="normal")
            self.entry_server_ip.config(state="normal")
            self.button_login.config(text="登录")
            self.button_login.config(state="normal")
            self.button_reg.config(state="normal")
            self.L.release()

        self.L.acquire()
        self.entry_name.config(state="disabled")
        self.entry_server_port.config(state="disabled")
        self.entry_server_ip.config(state="disabled")
        self.button_login.config(text="登录中")
        self.button_login.config(state="disabled")
        self.button_reg.config(state="disabled")
        self.L.release()
        name = self.entry_name.get()
        if len(name) == 0 or '!' in name:
            tkinter.messagebox.showwarning("警告","用户名不合法")
            restore_state()
            return
        self.log_fd = init_logfile('CLIENT_' + name + '.log')
        self.me = User(name, self.log_fd)
        self.me.server_ip = self.entry_server_ip.get()
        try:
            self.me.server_port = int(self.entry_server_port.get())
        except:
            tkinter.messagebox.showwarning("警告","端口不合法")
            return
        self.me.sock_listen()
        pwd = self.entry_pass.get()
        send_str = pwd+'!login'
        try:
            self.server_cmd(send_str)
        except:
            restore_state()
            print_log(self.log_fd, '[Login Failed  ] User: %s\tServer: %s:%s' % (
            self.me.name, self.me.server_ip, self.me.server_port))
            return
        start_t = time.time()
        loginok = False
        while time.time() - start_t < 5:
            if self.me.loginok == True:
                loginok = True
                self.L.acquire()
                self.button_login.config(text="已登录")
                self.button_logout.config(state="normal")
                tkinter.messagebox.showinfo("成功","登陆成功，按住ctrl可以多选，选择多个可以一对多群发消息")
                self.L.release()
                print_log(self.log_fd, '[Login Succeed ] User: %s\tServer: %s:%s' % (
                self.me.name, self.me.server_ip, self.me.server_port))
                break
        if loginok == False:
            print_log(self.log_fd, '[Login Failed  ] User: %s\tServer: %s:%s' % (
            self.me.name, self.me.server_ip, self.me.server_port))
            restore_state()
            return
        print_log(self.log_fd,
                  '[Logging in ...] User: %s\tServer: %s:%s' % (self.me.name, self.me.server_ip, self.me.server_port))
        
        self.login_flag = True
        self.th = threading.Thread(target=self.send_keepalive)
        self.th.setDaemon(True)
        self.th.start()

        self.th2 = threading.Thread(target=self.refresh_lists)
        self.th2.setDaemon(True)
        self.th2.start()

    def change_skin_click(self):
        self.skinIdx += 1
        if self.skinIdx >= len(self.skin_list):
            self.skinIdx = 0
        self.root.configure(background=self.skin_list[self.skinIdx])
        if self.login_flag:
            self.refresh_colors()
    def refresh_colors(self):
        s = self.listbox_msg.size()
        s1 = self.listbox_usr.size()
        self.L.acquire()
        for i in range(1,s):
            if i%2 == 0:
                self.listbox_msg.itemconfig(i, fg="black")
                self.listbox_msg.itemconfig(i, bg=self.skin_list[self.skinIdx])
            else:
                self.listbox_msg.itemconfig(i, fg="black")
                self.listbox_msg.itemconfig(i, bg="white")
        self.L.release()
        self.L.acquire()
        for i in range(1, s1):
            if i % 2 == 0:
                self.listbox_usr.itemconfig(i, fg="black")
                self.listbox_usr.itemconfig(i, bg=self.skin_list[self.skinIdx])
            else:
                self.listbox_usr.itemconfig(i, fg="black")
                self.listbox_usr.itemconfig(i, bg="white")
        self.L.release()

        print(list)

    
    def logout_click(self):
        self.me.userlist = {}
        self.me.refresh_usrlist_flag = True
        self.login_flag = False

    def logout(self):
        self.server_cmd('logout')
        self.L.acquire()
        self.button_login.config(state="normal")
        self.button_login.config(text="登录")
        self.button_logout.config(state="disabled")
        self.entry_name.config(state="normal")
        self.entry_server_port.config(state="normal")
        self.entry_server_ip.config(state="normal")
        self.L.release()
        tkinter.messagebox.showinfo("登出","登出成功")
        print_log(self.log_fd,
                  '[Logged out ...] User: %s\tServer: %s:%s' % (self.me.name, self.me.server_ip, self.me.server_port))

    def reg_click(self):
        self.send_th = threading.Thread(target=self.reg)
        self.send_th.setDaemon(True)
        self.send_th.start()

    def reg(self):
        name = self.entry_name.get()
        pwd = self.entry_pass.get()
        send_str = pwd+'!reg'
        if (len(name) == 0 or '!' in name) or (len(pwd) == 0 or '!' in pwd):
            tkinter.messagebox.showwarning("警告","用户名不合法")
            return
        self.log_fd = init_logfile('CLIENT_' + name + '.log')
        self.me = User(name, self.log_fd)
        self.me.server_ip = self.entry_server_ip.get()
        try:
            self.me.server_port = int(self.entry_server_port.get())
        except:
            tkinter.messagebox.showwarning("警告","端口不合法")
            return
        self.me.sock_listen()
        try:
            self.server_cmd(send_str)
        except:
            tkinter.messagebox.showwarning("警告", "登录失败")


    
    def send_click(self):
        self.send_th = threading.Thread(target=self.send)
        self.send_th.setDaemon(True)
        self.send_th.start()

    def send(self):
        to_user_name=''
        for i in self.listbox_usr.curselection():
            to_user_index = i - 1
            to_user_name = self.userlist_list[to_user_index]
            ip = self.me.userlist[to_user_name]["ip"]
            port = int(self.me.userlist[to_user_name]["port"])

            chat_str = self.text_input.get(1.0, tkinter.END).splitlines()
            print(chat_str)
            for chat_line in chat_str:
                currenTime=time.strftime("%H:%M:%S", time.localtime())
                chat_line1="["+currenTime+"]"+chat_line
                chat_line=chat_line+"["+currenTime+"]"
                send_str = '$!' + self.me.name + '!' + chat_line + '!msg!$'
                self.me.sock.sendto(send_str.encode('utf-8'), (ip, port))
                print_log(self.log_fd, '|to ' + to_user_name + '(' + ip + ':' + str(port) + '): ' + chat_line, ' ' * 8)
                if not self.sendFile:
                    to_add_str = chat_line1 + ' : ' + to_user_name + '<== ME           '
                    self.listbox_msg.insert(tkinter.END, '%80s' % to_add_str)
                index = self.listbox_msg.size()

                if not index % 2:
                    self.listbox_msg.itemconfig(index - 1, bg="white")
                else:
                    self.listbox_msg.itemconfig(index - 1, bg=self.skin_list[self.skinIdx])
        if self.sendFile:
            self.text_input.delete(1.0, tkinter.END)
            to_add_str = "SEND FILE" + ' : ' + to_user_name + '<== ME           '
            self.listbox_msg.insert(tkinter.END, '%80s' % to_add_str)
            index = self.listbox_msg.size()

            if not index % 2:
                self.listbox_msg.itemconfig(index - 1, bg="white")
            else:
                self.listbox_msg.itemconfig(index - 1, bg=self.skin_list[self.skinIdx])
        else:
            self.text_input.delete(1.0, tkinter.END)
        self.sendFile=False

    def txtfile(self):
        text_file = tkinter.filedialog.askopenfilename()
        print(text_file)
        fd = open(text_file, 'r')
        fname = os.path.split(text_file)[-1]
        str_txt = fd.read()
        print ("DEBUG: txt file:", str_txt)
        self.sendFile=True
        self.text_input.insert(tkinter.END, "Start Sending File!"+fname+'\n')
        self.text_input.insert(tkinter.END, str_txt)
        self.text_input.insert(tkinter.END, "\nSending Completed!")
        self.send_click()

    
    def send_keepalive(self):
        while self.login_flag == True and self.me.server_down == False:
            self.server_cmd('keepalive')
            time.sleep(2)

        if self.me.server_down == True:
            self.me.userlist = {}
            self.me.refresh_usrlist_flag = True
            self.login_flag = False

    
    def refresh_lists(self):
        while self.login_flag == True or self.me.refresh_usrlist_flag == True:
            self.me.buf_L.acquire()
            
            for i in self.me.recv_buf:
                self.listbox_msg.insert(tkinter.END, i)
                index = self.listbox_msg.size()
                if not index % 2:
                    self.listbox_msg.itemconfig(index - 1, bg="white")
                else:
                    self.listbox_msg.itemconfig(index - 1, bg=self.skin_list[self.skinIdx])
            self.me.recv_buf = []
            self.me.buf_L.release()
            
            if self.me.refresh_usrlist_flag == True:
                self.L.acquire()
                self.userlist_list = []
                self.listbox_usr.delete(1, tkinter.END)
                d = self.me.userlist
                for i in d:
                    self.userlist_list.append(i)
                    i = d[i]
                    to_add_str = "  %-12s%-15s%-5s" % (i['name'], i['ip'], i['port'])
                    self.listbox_usr.insert(tkinter.END, to_add_str)
                for i in range(len(d)):
                    if not i % 2:
                        self.listbox_usr.itemconfig(i + 1, bg="white")
                    else:
                        self.listbox_usr.itemconfig(i + 1, bg=self.skin_list[self.skinIdx])
                self.L.release()
                self.me.refresh_usrlist_flag = False
            time.sleep(0.1)
        self.logout()
        self.me.sock.close()

    
    def __gui_init(self):
        self.button_txtfile = tkinter.Button(self.root, text="发送文件", command=self.txtfile, height=1,
                                             width=0)
        self.button_txtfile.config(font=('MS Serif', '13', 'bold'))
        self.button_txtfile.grid(row=6, column=6, rowspan=2, padx=5, pady=5,
                                 sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_send = tkinter.Button(self.root, text="发送", command=self.send_click, height=1, width=0)
        self.button_send.config(font=('MS Serif', '16', 'bold'))
        self.button_send.grid(row=6, column=5, rowspan=2, padx=5, pady=5,
                              sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_login = tkinter.Button(self.root, text="登录", command=self.login_click, height=1, width=0)
        self.button_login.config(font=('MS Serif', '16', 'bold'))
        self.button_login.grid(row=4, column=0, columnspan=4, padx=3, pady=3,
                               sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_reg = tkinter.Button(self.root, text="注册", command=self.reg_click, height=1, width=0)
        self.button_reg.config(font=('MS Serif', '16', 'bold'))
        self.button_reg.grid(row=5, column=0, columnspan=4, padx=3, pady=3,
                               sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_logout = tkinter.Button(self.root, text="登出", command=self.logout_click, height=1, width=0)
        self.button_logout.config(font=('MS Serif', '16', 'bold'))
        self.button_logout.grid(row=6, column=0, columnspan=4, padx=3, pady=3,
                                sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)

        self.button_change_skin = tkinter.Button(self.root, text="一键换肤", command=self.change_skin_click, height=1,
                                                 width=0)
        self.button_change_skin.config(font=('MS Serif', '16', 'bold'))
        self.button_change_skin.grid(row=7, column=0, columnspan=4, padx=3, pady=3,
                                     sticky=tkinter.W + tkinter.E + tkinter.S + tkinter.N)
        
        self.scrollbar_msg = tkinter.Scrollbar(self.root)
        self.listbox_msg = tkinter.Listbox(self.root, height=20, width=70, yscrollcommand=self.scrollbar_msg.set)
        self.listbox_msg.grid(row=0, column=4, rowspan=6, columnspan=3, padx=15, pady=3,
                              sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)
        self.listbox_msg.config(font=('', '10'))
        self.scrollbar_msg.grid(row=0, column=6, rowspan=4, padx=0, pady=3, sticky=tkinter.N + tkinter.S + tkinter.E)
        self.scrollbar_msg.config(command=self.listbox_msg.yview)
        header = "   Messages...   "
        self.listbox_msg.insert(tkinter.END, header)
        self.listbox_msg.itemconfig(0, fg="white")
        self.listbox_msg.itemconfig(0, bg="black")

        self.scrollbar_usr = tkinter.Scrollbar(self.root)
        self.listbox_usr = tkinter.Listbox(self.root, height=20, width=33, yscrollcommand=self.scrollbar_usr.set,
                                           selectmode=tkinter.EXTENDED)
        self.listbox_usr.grid(row=0, column=0, rowspan=1, columnspan=4, padx=15, pady=3,
                              sticky=tkinter.W + tkinter.E + tkinter.N + tkinter.S)
        self.listbox_usr.config(font=('Courier New', '10'))
        self.scrollbar_usr.grid(row=0, column=3, rowspan=1, padx=0, pady=3, sticky=tkinter.N + tkinter.S + tkinter.E)
        self.scrollbar_usr.config(command=self.listbox_usr.yview)
        header = " Online Users     IP        Port"
        self.listbox_usr.insert(tkinter.END, header)
        self.listbox_usr.itemconfig(0, fg="white")
        self.listbox_usr.itemconfig(0, bg="black")

        
        self.label_server = tkinter.Label(self.root, text="地址:")
        self.label_name = tkinter.Label(self.root, text="用户名:")
        self.label_colon = tkinter.Label(self.root, text="端口")
        self.label_pass = tkinter.Label(self.root, text="密码")
        self.entry_server_ip = tkinter.Entry(self.root, width=18)
        self.entry_server_port = tkinter.Entry(self.root, width=6)
        self.entry_name = tkinter.Entry(self.root, width=25)
        self.entry_pass = tkinter.Entry(self.root, width=25)

        self.label_server.grid(row=1, column=0, ipady=3, pady=5, padx=5, sticky=tkinter.W)
        self.entry_server_ip.grid(row=1, column=1, columnspan=1, ipady=3, pady=5, sticky=tkinter.E + tkinter.W)
        self.label_colon.grid(row=1, column=2, ipady=3, pady=5, padx=0, sticky=tkinter.W + tkinter.E)
        self.entry_server_port.grid(row=1, column=3, columnspan=1, ipady=3, pady=5, sticky=tkinter.E + tkinter.W)

        self.label_name.grid(row=2, column=0, ipady=3, pady=5, padx=5, sticky=tkinter.W)
        self.entry_name.grid(row=2, column=1, columnspan=3, ipady=3, pady=5, sticky=tkinter.E + tkinter.W)
        self.label_pass.grid(row=3, column=0, ipady=3, pady=5, padx=5, sticky=tkinter.W)
        self.entry_pass.grid(row=3, column=1, columnspan=3, ipady=3, pady=5, sticky=tkinter.E + tkinter.W)

        
        self.text_input = tkinter.Text(self.root, height=5, width=40)
        self.text_input.grid(row=6, column=4, rowspan=2, ipadx=5, ipady=5, padx=5, pady=5, sticky=tkinter.W + tkinter.E)
        self.text_input.config(font=('', '12', ''))




class User:
    def __init__(self, name, log_fd):
        self.name = name
        self.server_ip = ''
        self.server_port = 0
        self.port_sel()
        self.recv_buf = []
        self.buf_L = threading.Lock()
        self.userlist = {}
        self.loginok = False
        self.refresh_usrlist_flag = False
        self.server_down = False
        self.log_fd = log_fd
        self.isFile = False
        self.savedFileName = ''

    def port_sel(self):
        while True:
            port_candidate = 1000 + int(random.random() * 8000)
            if self.port_isopen('127.0.0.1', port_candidate):
                continue
            else:
                self.port = port_candidate
                return


    def port_isopen(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, int(port)))
            s.shutdown(2)
        except:
            return False
        return True

    def sock_listen(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('', self.port))
        except:
            print("socket create failed")
        else:
            self.th = threading.Thread(target=self.listening_worker)
            self.th.setDaemon(True)
            self.th.start()

    def listening_worker(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            ip = addr[0]
            port = addr[1]
            data = data.decode('utf-8')

            l = data.split('!')
            
            if l[0] == '>' and l[-1] == '<':
                if l[-2] == 'quit':
                    
                    self.server_down = True
                    print_log(self.log_fd, "[Server Message] Server will down, must log out")
                    return
                elif l[-2] == 'loginok':
                    self.loginok = True
                elif l[-2] == "loginnouser":
                    self.loginok=False
                    tkinter.messagebox.showwarning("警告","用户名不存在，请注册")
                elif l[-2] == "loginnopass":
                    self.loginok=False
                    tkinter.messagebox.showwarning("警告","密码错误")
                elif l[-2] == "regok":
                    tkinter.messagebox.showinfo("成功","注册成功，请登录")

                elif l[-2] == "haveuser":
                    tkinter.messagebox.showinfo("失败","用户名已存在，请更换用户名重新注册")
                elif l[-2] == 'userlist':
                    
                    newlist = json.loads(l[1])
                    print (newlist)
                    print (self.userlist)
                    if operator.ne(self.userlist, newlist):
                        self.userlist = newlist
                        self.refresh_usrlist_flag = True
                        print ("Online User |       IP      |     Port   ")
                        print ("-----------------------------------------")
                        for i in self.userlist:
                            print ("  %-10s|   %-12s|    %-8s" % (
                            self.userlist[i]['name'], self.userlist[i]['ip'], self.userlist[i]['port']))
                        print ("-----------------------------------------")



            elif l[0] == '$' and l[-1] == '$':
                
                if l[-2] == 'msg':
                    name = l[1]
                    char_str = '!'.join(l[2:-2])
                    print_log(self.log_fd, '|from ' + name + '(' + ip + ':' + str(port) + '): ' + char_str, ' ' * 8)

                    recved_msg = name +" ==> ME"+ ' : ' + char_str

                    char_str=char_str.split('[')[0]
                    print(char_str)

                    if char_str == "Sending Completed!":
                        self.isFile = False
                        file_msg = name +" ==> ME"+ ' : ' + "SEND A FILE NAMED "+self.savedFileName
                        self.buf_L.acquire()
                        self.recv_buf.append(file_msg)
                        self.buf_L.release()
                        return
                    if self.isFile:
                        print("正在写文件！！！！！！！")
                        print(self.savedFileName)
                        output=open(self.savedFileName,'a+')
                        output.write(char_str+"\n")
                        output.close()
                    if char_str.startswith( "Start Sending File"):
                        print("is File")
                        fname = char_str.split('!')[-1]
                        self.savedFileName=fname
                        self.isFile = True
                    if not self.isFile:
                        self.buf_L.acquire()
                        self.recv_buf.append(recved_msg)
                        self.buf_L.release()


def main():
    root = tkinter.Tk()
    window = TkGUI(root)
    window.root.mainloop()


if __name__ == "__main__":
    main()
