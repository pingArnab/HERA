import threading
from subprocess import Popen, PIPE, call
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext


class HeraApplication(tk.Frame):
    def __init__(self, master=None, port=None):
        master.geometry("720x300")
        master.resizable(0, 0)
        master.protocol("WM_DELETE_WINDOW", self.__close)
        master.title("Hera")
        super().__init__(master)
        self.__port = port
        self.__start_cmd = r'.\venv\Scripts\python.exe manage.py runserver {port}'.format(port=port)
        self.__stop_cmd = r"""for /f "tokens=5" %a in ('netstat -aon ^| find ":{port}" ^| find "LISTENING"') do taskkill /f /pid %a""".format(
            port=port or 8000
        )

        self.label = tk.Label(master, text="Fact of the Day")
        self.startServer = tk.Button(self, height=1, width=6)
        self.stopServer = tk.Button(self, height=1, width=6)
        # self.output = tk.Text(root, bg="light cyan")
        self.output = scrolledtext.ScrolledText(
            self
        )

        self.__port = port
        self.master = master
        self.pack()
        self.create_widgets()
        self.__start_server()

    def __start_server(self):
        class CmdThreadExe(threading.Thread):
            def __init__(self, cmd):
                super().__init__()
                self.__cmd = cmd
                self.__pid = self.__out = self.__err = None

            def run(self):
                current_dir = os.getcwd()
                ps = Popen(self.__cmd, cwd=current_dir, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                self.__pid = ps.pid
                self.__out, self.__err = ps.communicate()

        self.__stop_server()
        thread = CmdThreadExe(self.__start_cmd)
        thread.daemon = True
        thread.start()
        self.startServer["text"] = "Restart"
        self.output.insert(tk.END, '\n\nServer running at port: {port}'.format(port=self.__port))

    def __stop_server(self):
        current_dir = os.getcwd()
        ps = Popen(self.__stop_cmd, cwd=current_dir, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = ps.communicate()
        self.startServer["text"] = "Start"
        if err:
            self.output.insert(tk.END, err)
        if out:
            self.output.insert(tk.END, '\n\n')
            self.output.insert(tk.END, out)
            self.output.insert(tk.END, 'Server Stopped')

    def __close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.__stop_server()
            self.master.destroy()

    def create_widgets(self):
        self.label.config(font=("Courier", 14))

        self.startServer["text"] = "Start"
        self.startServer["command"] = self.__start_server
        self.startServer.pack(side="top")

        self.stopServer["text"] = "Stop"
        self.stopServer["command"] = self.__stop_server
        self.stopServer.pack(side="top")

        self.output.focus()
        self.output.pack(side="bottom")

        # self.pack(side="bottom")


if __name__ == '__main__':
    root = tk.Tk()
    app = HeraApplication(master=root, port=8000)

    app.mainloop()
