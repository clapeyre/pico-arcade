import utime as time
import uasyncio as asyncio
from lib.buttons import button_init, on, off, get_arcadebuttons, COLORS
from drivers.sh1107 import SH1107_I2C
from app_memory import app_memory
from app_light_chaser import app_light_chaser
from app_buzzer import app_buzzer
from app_marcels_quest import app_marcels_quest
from app_marcels_frogs import app_marcels_frogs
from app_faster_light import app_faster_light
from app_symmetry import app_symmetry
from app_memory_sound import app_memory_sound
from app_whackamole import app_whackamole


async def start_sequence():
    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.on()
    time.sleep_ms(500)
    for color in COLORS:
        for _, led in arcade.items(color=color):
            led.off()
        time.sleep_ms(500)
    print(" >> Go Go Go! <<")

async def app_menu():
    buttons, leds = button_init()
    oled = SH1107_I2C()

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
            asyncio.run(app_light_chaser(hardcore=True, nleds=3))
        elif not buttons[2].value():
            asyncio.run(start_sequence())
            app_memory(sound_level=0)
        elif not buttons[3].value():
            asyncio.run(start_sequence())
            app_memory()
        elif not buttons[4].value():
            asyncio.run(app_buzzer())
        elif not buttons[5].value():
            asyncio.run(start_sequence())
            asyncio.run(app_whackamole())
        elif not buttons[6].value():
            asyncio.run(start_sequence())
            asyncio.run(app_faster_light())
        elif not buttons[7].value():
            asyncio.run(app_symmetry())

        # Marcel's games
        elif not buttons[8].value():
            asyncio.run(app_marcels_quest())
        elif not buttons[9].value():
            asyncio.run(app_marcels_frogs())

        elif not buttons[12].value():
            asyncio.run(app_memory_sound())

        elif not buttons[15].value():
            list(map(off, leds))
            return

        oled.text_wrap("Touchez un bouton pour revenir au menu", 7)
        oled.show()
        while all([b.value() for b in buttons]):
            time.sleep(0.05)

if __name__ == '__main__':
    asyncio.run(app_menu())
