import utime as time
import uasyncio as asyncio
from lib.buttons import button_init, on, off, get_arcadebuttons, COLORS
from lib.sh1107 import get_oled
from app_memory import app_memory
from app_light_chaser import app_light_chaser
from app_buzzer import app_buzzer
from app_marcels_quest import app_marcels_quest


async def start_sequence():
    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.on()
    time.sleep_ms(500)
    for color in COLORS:
        for _, led in arcade.items(color=color):
            led.off()
        time.sleep_ms(500)
    print(" >> Go Go Go! <<")

async def main():
    buttons, leds = button_init()
    oled = get_oled()

    while True:
        oled.fill(0)
        oled.text('Menu', 0, 0, 1)
        oled.show()
        for _ in range(2):
            list(map(off, leds))
            time.sleep_ms(200)
            list(map(on, leds))
            time.sleep_ms(200)
        while all([b.value() for b in buttons]):
            time.sleep(0.01)
        if not buttons[0].value():
            asyncio.run(start_sequence())
            asyncio.run(app_light_chaser())
        elif not buttons[1].value():
            asyncio.run(start_sequence())
            asyncio.run(app_light_chaser(hardcore=True))
        elif not buttons[2].value():
            asyncio.run(start_sequence())
            app_memory(sound_level=0)
        elif not buttons[3].value():
            asyncio.run(start_sequence())
            app_memory()
        elif not buttons[4].value():
            asyncio.run(app_buzzer())
        elif not buttons[5].value():
            asyncio.run(app_marcels_quest())
        elif not buttons[15].value():
            list(map(off, leds))
            return

        oled.text_wrap("Touchez un bouton pour revenir au menu", 7)
        oled.show()
        while all([b.value() for b in buttons]):
            time.sleep(0.05)

if __name__ == '__main__':
    asyncio.run(main())
