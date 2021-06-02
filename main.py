from tkinter import messagebox
import os
import socket
from pathlib import Path


from Hera.GUI import HeraGUI
import tkinter as tk

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    LOCAL_IP = get_ip()
    
    BASE_DIR = Path(os.getcwd())

    FRONT_PORT = 3000
    BACK_PORT = 8000
    print(Path(BASE_DIR / '.env').exists() ,  Path(BASE_DIR / 'back\.env').exists(), Path(BASE_DIR / 'front\.env').exists())
    if not(Path(BASE_DIR / '.env').exists() and Path(BASE_DIR / 'back\.env').exists() and Path(BASE_DIR / 'front\.env').exists()):
        with open (BASE_DIR / '.env', 'w', encoding='utf-8') as f:
            f.write('PORT={back_port}\nIP={local_ip}'.format(back_port=BACK_PORT, local_ip=LOCAL_IP))
        with open (BASE_DIR / 'back\.env', 'w', encoding='utf-8') as f:
            f.write('BACK_PORT={back_port}\nFRONT_PORT={front_port}'.format(back_port=BACK_PORT, front_port=FRONT_PORT))
        with open (BASE_DIR / 'front\.env', 'w', encoding='utf-8') as f:
            f.write(
                'API={local_ip}:{back_port}/api/v1'.format(local_ip=LOCAL_IP, back_port=BACK_PORT) + '\n' +
                'BACKEND={local_ip}:{back_port}'.format(local_ip=LOCAL_IP, back_port=BACK_PORT) + '\n' +
                'PORT={front_port}'.format(front_port=FRONT_PORT)
            )

    
    window = tk.Tk()
    heraGUI = HeraGUI(window, 'media/')
    heraGUI.start_app()
