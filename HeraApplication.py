import os
import threading
from subprocess import Popen, PIPE
from tkinter import *
import tkinter.font as font
from tkinter import messagebox

from PIL import ImageTk, Image


class Color:
    BLARK = '#090b13'
    PRIMARY_RED = '#FF3D00'
    BASIC_WHITE = '#fff'
    REGULAR_GREEN = '#24d94c'


class Position:
    WINDOW_HEIGHT = 360
    WINDOW_WIDTH = 550
    PADDED_LEFT = 52


class Sys:
    PORT = 8000
    START_CMD = r'.\venv\Scripts\python.exe manage.py runserver {port}'.format(port=PORT)
    STOP_CMD = r"""for /f "tokens=5" %a in ('netstat -aon ^| find ":{port}" ^| find "LISTENING"') do taskkill /f /pid %a""".format(
        port=PORT or 8000
    )


def start_server():
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

    stop_server()
    thread = CmdThreadExe(Sys.START_CMD)
    thread.daemon = True
    thread.start()


def stop_server():
    current_dir = os.getcwd()
    ps = Popen(Sys.STOP_CMD, cwd=current_dir, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = ps.communicate()


def close():
    if messagebox.askokcancel("Quit", "Do you want to close Hera?"):
        stop_server()
        root.destroy()


root = Tk()
root.geometry("{width}x{height}".format(width=Position.WINDOW_WIDTH, height=Position.WINDOW_HEIGHT))
root.resizable(0, 0)
root.protocol("WM_DELETE_WINDOW", close)
root.title('HERA')
root.iconbitmap('./media/GUI/favicon.ico')

button_font = font.Font(family='Arial', size=8, weight='bold')
description_font = font.Font(family='Arial', size=7)
version_font = font.Font(family='Arial', size=5)


left = Label(bg=Color.BLARK)

my_img = ImageTk.PhotoImage(Image.open('./media/GUI/Path 34.png'))

right = Label(image=my_img, bg=Color.BLARK)

restart_button = Button(
    root,
    text="RESTART HERA",
    fg=Color.BASIC_WHITE,
    bg='#ff3d00',
    font=button_font,
    command=start_server
)
close_button = Button(
    root,
    text="CLOSE HERA",
    fg=Color.BLARK,
    bg=Color.BASIC_WHITE,
    font=button_font,
    command=close
)

logo_mark_image = ImageTk.PhotoImage(Image.open('./media/GUI/logo_mark.png'))
logo_mark = Label(
    image=logo_mark_image,
    bg=Color.BLARK
)

description = Label(
    text='HERA is a home media server used to organize your collection of movies and \n'
         'tv shows. You add the location of your library and Hera organizes your content \n'
         'automatically and makes them available to everyone in your network',
    font=description_font,
    fg=Color.BASIC_WHITE,
    bg=Color.BLARK,
    justify=LEFT,
)
version_text = Label(
    text='v0.2.285019a',
    font=version_font,
    fg=Color.BASIC_WHITE,
    bg=Color.PRIMARY_RED,
)

left.place(x=0, y=0, height=Position.WINDOW_HEIGHT, width=Position.WINDOW_WIDTH)
right.place(x=400, y=0, height=Position.WINDOW_HEIGHT, width=155)
restart_button.place(x=Position.PADDED_LEFT, y=243, height=30, width=130)
close_button.place(x=197, y=243, height=30, width=130)
logo_mark.place(x=Position.PADDED_LEFT, y=110, width=121, height=52)
description.place(x=Position.PADDED_LEFT - 7, y=175, width=350)
version_text.place(x=504, y=375, width=38, height=6)

start_server()

root.mainloop()


