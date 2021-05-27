import logging
import os
import subprocess
import threading
from subprocess import Popen, PIPE
from tkinter import *
import tkinter.font as font
from tkinter import messagebox
from PIL import ImageTk, Image

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


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


class HeraGUI(Frame):

    def __init__(self, instance, media_url=None):
        super().__init__(instance)
        logging.info('Starting App')
        self.root = instance
        self.MEDIA_URL = media_url
        self.__configure_window()
        self.__load_components()
        self.__start_server()

    def __configure_window(self):
        self.root.geometry("{width}x{height}".format(width=Position.WINDOW_WIDTH, height=Position.WINDOW_HEIGHT))
        self.root.resizable(0, 0)
        self.root.protocol("WM_DELETE_WINDOW", self.__close)
        try:
            self.root.iconbitmap(self.MEDIA_URL + 'favicon.ico')
            self.root.title('HERA')
        except Exception as ex:
            self.root.title('Error in iconbitmap')

    def __load_components(self):
        button_font = font.Font(family='Arial', size=8, weight='bold')
        description_font = font.Font(family='Arial', size=7)
        version_font = font.Font(family='Arial', size=5)

        self.left = Label(self.root, bg=Color.BLARK)
        try:
            self.__right_img = ImageTk.PhotoImage(Image.open(self.MEDIA_URL + 'Path 34.png'))
            self.right = Label(self.root, image=self.__right_img, bg=Color.BLARK)
        except Exception as ex:
            self.right = Label(self.root, text='Error in Right Image Area', bg=Color.BLARK)

        self.restart_button = Button(
            self.root,
            text="RESTART HERA",
            fg=Color.BASIC_WHITE,
            bg='#ff3d00',
            font=button_font,
            command=self.__start_server
        )
        self.close_button = Button(
            self.root,
            text="CLOSE HERA",
            fg=Color.BLARK,
            bg=Color.BASIC_WHITE,
            font=button_font,
            command=self.__close
        )

        try:
            self.__logo_mark_image = ImageTk.PhotoImage(Image.open(self.MEDIA_URL + 'logo_mark.png'))
            self.logo_mark = Label(self.root, image=self.__logo_mark_image, bg=Color.BLARK)
        except Exception as ex:
            self.logo_mark = Label(self.root, text='Error in logo_mark area', bg=Color.BLARK)

        self.description = Label(
            self.root,
            text='HERA is a home media server used to organize your collection of movies and \n'
                 'tv shows. You add the location of your library and Hera organizes your content \n'
                 'automatically and makes them available to everyone in your network',
            font=description_font,
            fg=Color.BASIC_WHITE,
            bg=Color.BLARK,
            justify=LEFT,
        )
        self.version_text = Label(
            self.root,
            text='v0.2.285019a',
            font=version_font,
            fg=Color.BASIC_WHITE,
            bg=Color.PRIMARY_RED,
        )

        self.left.place(x=0, y=0, height=Position.WINDOW_HEIGHT, width=Position.WINDOW_WIDTH)
        self.right.place(x=400, y=0, height=Position.WINDOW_HEIGHT, width=155)
        self.restart_button.place(x=Position.PADDED_LEFT, y=243, height=30, width=130)
        self.close_button.place(x=197, y=243, height=30, width=130)
        self.logo_mark.place(x=Position.PADDED_LEFT, y=110, width=121, height=52)
        self.description.place(x=Position.PADDED_LEFT - 7, y=175, width=350)
        self.version_text.place(x=504, y=375, width=38, height=6)

    def __start_server(self):
        class CmdThreadExe(threading.Thread):
            def __init__(self, cmd):
                super().__init__()
                self.__cmd = cmd
                self.__pid = self.__out = self.__err = None

            def run(self):
                logging.info('Threading')
                current_dir = os.getcwd()
                try:
                    ps = Popen(self.__cmd, cwd=current_dir, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    self.__pid = ps.pid
                    logging.info(self.__pid)
                    self.__out, self.__err = ps.communicate()
                except Exception as ex:
                    logging.error('Error in Run Server\n')
                    logging.error(ex)
                logging.info(self.__out, self.__err)

        self.__stop_server()
        logging.info('Starting...')
        thread = CmdThreadExe(Sys.START_CMD)
        thread.daemon = True
        thread.start()
        logging.info('Started')

    def __stop_server(self):
        logging.info('Stopping Server')
        current_dir = os.getcwd()
        try:
            ps = subprocess.Popen(Sys.STOP_CMD, cwd=current_dir, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            ps.communicate()
        except Exception as ex:
            logging.error('Error in Stop server')
            logging.error(ex)

    def __close(self):
        if messagebox.askokcancel("Quit", "Do you want to close Hera?"):
            self.root.destroy()
            self.__stop_server()

    def start_app(self):
        self.mainloop()
