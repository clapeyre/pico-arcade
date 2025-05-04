import utime as time
import urandom as random
import asyncio

from drivers.buzzer import Buzzer
from lib.oled import get_oled
from lib.buttons import get_arcadebuttons

async def app_faster_light(start_time=2000, accel=0.9):
    oled = get_oled()
    print('Bienvenue dans le chasseur de lumière!')
    oled.clear_screen()
    oled.draw_centered_text("Chasse", 0)
    oled.draw_centered_text("Lumiere", 10)
    oled.show()

    score = 0
    arcade = get_arcadebuttons()
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
    oled.clear_screen()
    oled.draw_centered_text('Fini!', 0)
    oled.draw_centered_text('Score:', 20)
    oled.draw_centered_text(f'{score}', 40)
    oled.show()

    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.5))
        time.sleep_ms(30)

    return

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_faster_light)
