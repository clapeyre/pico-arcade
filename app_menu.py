import utime
import uasyncio
from lib.buttons import button_init, on, off
from lib.sh1107 import get_oled
from app_memory import app_memory
from app_light_chaser import app_light_chaser
from app_buzzer import app_buzzer


def start_sequence():
    _, leds = button_init()
    list(map(on, leds))
    for led in leds:
        utime.sleep(0.5)
        off(led)
    list(map(on, leds))
    utime.sleep(0.5)
    print(" >> Go Go Go! <<")
    list(map(off, leds))

def main():
    buttons, leds = button_init()
    b1, b2, b3, b4 = buttons
    oled = get_oled()

    while True:
        oled.fill(0)
        oled.text('Menu', 0, 0, 1)
        oled.show()
        for _ in range(2):
            list(map(off, leds))
            utime.sleep_ms(200)
            list(map(on, leds))
            utime.sleep_ms(200)
        while all([b.value() for b in buttons]):
            utime.sleep(0.01)
        if not b1.value():
            start_sequence()
            app_light_chaser()
        elif not b2.value():
            start_sequence()
            app_light_chaser(hardcore=True)
        elif not b3.value():
            start_sequence()
            app_memory(sound_level=0)
        #elif not allb[-1].value():
        #    uasyncio.run(app_buzzer())
        else:
            start_sequence()
            app_memory()

        utime.sleep(1)
        oled.text("Touchez un", 0, 70, 1)
        oled.text("bouton", 0, 80, 1)
        oled.text("pour", 0, 90, 1)
        oled.text("revenir", 0, 100, 1)
        oled.text("au menu", 0, 110, 1)
        oled.show()
        while all([b.value() for b in buttons]):
            utime.sleep(0.05)

if __name__ == '__main__':
    main()       