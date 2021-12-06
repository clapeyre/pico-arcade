import uasyncio as asyncio
import urandom as random
from lib.buzzer import get_buzzer
from lib.buttons import get_arcadebuttons, get_controlpanel
from lib.sh1107 import get_oled


async def buzz(color):
    tunes = {"white": [220, 220*1.414, 440, 440*1.414, 880],
             "blue": [220, 220*1.414, 440, 440*1.414, 880][::-1],
             "red": [220, 220*1.414, 220, 440, 220, 440*1.414],
             "yellow": [220, 220*1.414, 220, 440, 220, 440*1.414][::-1],
             }
    buzzer = get_buzzer()
    for tone in tunes[color]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.1))


async def app_buzzer():
    print('  >>>  Bienvenue dans le buzzer!  <<<')

    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.reset_flags()
    arcade.on()
    cp = get_controlpanel(pressed_flag=True)
    cp.reset_flags()

    oled = get_oled()
    print("  >>>  Ready to buzz?  <<<")
    oled.fill(0)
    oled.text("Buzz!", 0, 0, 1)
    oled.show()

    while 'select' not in cp.pressed:
        while not arcade.pressed:
            await asyncio.sleep_ms(1)

        if arcade.pressed:
            arcade.off()
            choice = 0
            if len(arcade.pressed) > 1:
                # This shouldn't happen...
                oled.text('E ' + str(arcade.pressed), 0, 120, 1)
                oled.show()
                choice = random.randint(0, len(arcade.pressed)-1)
            idx = arcade.pressed[choice]
            await asyncio.gather(
                buzz(arcade.color[idx]),
                arcade.leds[idx].blink(100, 100, 3))
            arcade.leds[idx].on()
            await asyncio.sleep_ms(200)
            arcade.reset_flags()
        
            while not arcade.pressed:
                if 'select' in cp.pressed:
                    return
                await asyncio.sleep_ms(20)
            await asyncio.sleep_ms(500)
            for _ in range(2):
                arcade.off()
                await asyncio.sleep_ms(100)
                arcade.on()
                await asyncio.sleep_ms(100)
            arcade.reset_flags()
    arcade.off()

if __name__ == '__main__':
    asyncio.run(app_buzzer())