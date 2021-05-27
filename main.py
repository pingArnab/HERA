from tkinter import messagebox

from Hera.GUI import HeraGUI
import tkinter as tk


if __name__ == '__main__':
    window = tk.Tk()
    heraGUI = HeraGUI(window, 'media/')
    heraGUI.start_app()
