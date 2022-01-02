import utime as time
import urandom as random
import uasyncio as asyncio

from drivers.buzzer import Buzzer
from drivers.sh1107 import SH1107_I2C
from lib.buttons import get_arcadebuttons

async def app_faster_light(start_time=2000, accel=0.9):
    oled = SH1107_I2C()
    print('Bienvenue dans le chasseur de lumière!')
    oled.fill(0)
    oled.text("Chasse", 0, 0, 1)
    oled.text("Lumiere", 0, 10, 1)
    oled.show()

    score = 0
    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.reset_flags()
    arcade.off()

    def light_random(forbidden=None):
        """Light a random LED that is off (not in forbidden)"""
        if not forbidden:
            forbidden = []
        while True:
            rnd = random.randint(0, arcade.size - 1)
            if not arcade.leds[rnd].value() and rnd not in forbidden:
                break
            # time.sleep_ms(1)
        arcade.leds[rnd].on()
        return rnd

    timer = start_time
    while True:
        led_on = light_random()
        start = time.ticks_ms()
        arcade.reset_flags()
        while led_on not in arcade.pressed and time.ticks_diff(time.ticks_ms(), start) < timer:
            await asyncio.sleep_ms(1)

        if time.ticks_diff(time.ticks_ms(), start) > timer:
            break

        score += 1
        timer *= accel
        arcade.leds[led_on].off()

    arcade.off()
    print('\n >>> FINI <<<')
    print(f"\n Score: {score}")
    oled.fill(0)
    oled.text('Fini!', 0, 0, 1)
    oled.text('Score:', 0, 20, 1)
    oled.text(f'  {score}', 0, 40, 1)
    oled.show()

    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.5))
        time.sleep_ms(30)

    return
