import utime as time
import uasyncio as asyncio
from drivers.buzzer import Buzzer
from drivers.sh1107 import SH1107_I2C
from lib.buttons import get_arcadebuttons, get_controlpanel, COLORS
from app_sequence import app_sequence
from app_light_chaser import app_light_chaser
from app_light_chaser_1v1 import app_light_chaser_1v1
from app_buzzer import app_buzzer
from app_marcels_quest import app_marcels_quest
from app_marcels_frogs import app_marcels_frogs
from app_marcel_reflex import app_marcel_reflex
from app_symmetry import app_symmetry
from app_memory_sound import app_memory_sound
from app_whackamole import app_whackamole
from app_mirror_fight import app_mirror_fight
from app_mirror_sequence import app_mirror_sequence
from app_idle import app_idle

# BOARD
#  0  4  8 12
#  1  5  9 13
#  2  6 10 14
#  3  7 11 15
GAMES = [
    (app_light_chaser, {}),                    # 0
    (app_light_chaser, {'hardcore': True}),    # 1
    (app_sequence, {'sound_level': 0}),        # 2
    (app_sequence, {}),                        # 3
    (app_memory_sound, {}),                    # 4
    (app_whackamole, {}),                      # 5
    (app_light_chaser_1v1, {}),                # 6
    (app_mirror_fight, {}),                    # 7
    (app_marcels_quest, {}),                   # 8
    (app_marcels_frogs, {}),                   # 9
    (app_marcel_reflex, {}),                        # 10
    (app_symmetry, {}),                        # 11
    (app_buzzer, {}),                          # 12
    (app_mirror_sequence, {}),                 # 13
    (None, {}),                                # 14
    (app_idle, {}),                            # 15
]


def flash_start():
    arcade = get_arcadebuttons()
    arcade.on()
    time.sleep_ms(500)
    for color in COLORS:
        for _, led in arcade.items(color=color):
            led.off()
        time.sleep_ms(500)
    print(" >> Go Go Go! <<")


async def play(game):
    func, kwargs = GAMES[game]
    if func is None:
        return None

    flash_start()
    res = func(**kwargs)

    async def f(): pass
    print(type(f()))
    if isinstance(res, type(f())):
        print("XXX This game is async")
        await res


async def flash_all():
    arcade = get_arcadebuttons()
    for _ in range(2):
        arcade.off()
        await asyncio.sleep_ms(200)
        arcade.on()
        await asyncio.sleep_ms(200)
    arcade.off()
    for i, (func, _) in enumerate(GAMES):
        if func is not None:
            arcade.leds[i].on()


def oled_menu():
    oled = SH1107_I2C()
    oled.fill(0)
    oled.text(' -- Menu --', 0, 0, 1)
    oled.text('Select a Game', 10, 0, 1)
    oled.show()
    print(" > Main Menu")


async def app_menu():
    arcade = get_arcadebuttons()
    cp = get_controlpanel()

    while True:  # Global loop
        oled_menu()
        await flash_all()
        arcade.reset_flags()
        cp.reset_flags()

        while True:  # Single game loop
            if 'select' in cp.pressed:
                return

            if arcade.pressed:
                print("XXX playing", arcade.pressed[0])
                await play(arcade.pressed[0])
                print("XXX Done playing")
                cleanup()
                break
            
            await asyncio.sleep_ms(0)


def cleanup():
    Buzzer().end_tone()
    get_arcadebuttons().off()

if __name__ == '__main__':
    asyncio.run(app_menu())
