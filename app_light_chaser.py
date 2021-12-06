import utime as time
import urandom as random
import uasyncio as asyncio
from lib.buttons import get_arcadebuttons
from lib.buzzer import get_buzzer
from lib.sh1107 import get_oled


async def app_light_chaser(hardcore=False, timer=20_000, nleds=3):
    oled = get_oled()
    print('Bienvenue dans le chasseur de lumière!')
    oled.fill(0)
    oled.text("Chasse", 0, 0, 1)
    oled.text("Lumiere", 0, 10, 1)
    if hardcore:
        print('Mode hardcore activé')
        oled.text("Hardcore", 0, 20, 1)
    oled.show()
    score = 0
    start = time.ticks_ms()
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

    for _ in range(nleds):
        light_random()

    while True:
        while not arcade.pressed and time.ticks_diff(time.ticks_ms(), start) < timer:
            await asyncio.sleep_ms(1)

        if time.ticks_diff(time.ticks_ms(), start) >= timer:
            break

        found = [i for i in arcade.pressed if arcade.leds[i]()]
        for _ in found:
            light_random()
        for idx in found:
            arcade.leds[idx].off()
        score += len(found)

        if hardcore:
            score -= (len(arcade.pressed) - len(found))
        
        arcade.reset_flags()

    arcade.off()
    print('\n >>> FINI <<<')
    print(f"\n Score: {score}")
    oled.fill(0)
    oled.text('Fini!', 0, 0, 1)
    oled.text('Score:', 0, 20, 1)
    oled.text(f'  {score}', 0, 40, 1)
    oled.show()

    buzzer = get_buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.5))
        time.sleep_ms(30)

    return

async def test():
    while True:
        asyncio.run(app_light_chaser(timer=1000))
        time.sleep(1)
        print('monitor restart')
        arcade = get_arcadebuttons(pressed_flag=True)
        arcade.reset_flags()
        while not arcade.pressed:
            await asyncio.sleep_ms(1)
        # print(arcade.pressed)

if __name__ == '__main__':
    asyncio.run(test())