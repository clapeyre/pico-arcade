import asyncio
import urandom as random
from drivers.buzzer import Buzzer
from lib.oled import get_oled
from lib.buttons import get_arcadebuttons, get_controlpanel


async def buzz(color):
    tunes = {"white": [220, 220*1.414, 440, 440*1.414, 880],
             "blue": [220, 220*1.414, 440, 440*1.414, 880][::-1],
             "red": [220, 220*1.414, 220, 440, 220, 440*1.414],
             "yellow": [220, 220*1.414, 220, 440, 220, 440*1.414][::-1],
             }
    buzzer = Buzzer()
    for tone in tunes[color]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.1))


async def _main():
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.on()
    ready = True
    while True:
        if arcade.pressed:
            if ready:
                arcade.off()
                choice = 0
                if len(arcade.pressed) > 1:
                    # 2 presses detected. Choose at random.
                    choice = random.randint(0, len(arcade.pressed)-1)
                idx = arcade.pressed[choice]
                await asyncio.gather(
                    buzz(arcade.color[idx]),
                    arcade.leds[idx].blink(100, 100, 3))
                arcade.leds[idx].on()
                await asyncio.sleep_ms(1000)
                arcade.reset_flags()
                ready = False
            else:
                for _ in range(2):
                    arcade.off()
                    await asyncio.sleep_ms(100)
                    arcade.on()
                    await asyncio.sleep_ms(100)
                arcade.reset_flags()
                ready = True
        await asyncio.sleep(0)
        

async def app_buzzer():
    print('  >>>  Welcome to the buzzer!  <<<')

    oled = get_oled()
    print("  >>>  Ready to buzz?  <<<")
    oled.clear_screen()
    oled.draw_centered_text("Buzz!", 0)
    oled.show()

    main = asyncio.create_task(_main())

    cp = get_controlpanel()
    cp.reset_flags()

    while True:
        if 'select' in cp.pressed:
            main.cancel()
            return
        await asyncio.sleep_ms(0)

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_buzzer)