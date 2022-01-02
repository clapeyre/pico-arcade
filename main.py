import uasyncio as asyncio
from app_menu import app_menu
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons

def main():
    try:
        asyncio.run(app_menu())
    finally:
        Buzzer().end_tone()
        get_arcadebuttons().off()
        print('Mainloop killed. Ctrl+D to restart')

main()