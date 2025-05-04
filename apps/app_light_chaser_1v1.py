import utime as time
import urandom as random
import asyncio
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, COLORS, get_controlpanel
from lib.score import DigitalScorer


class Board:
    def __init__(self, buttons):
        self.buttons = buttons
        arcade = get_arcadebuttons()
        self.leds = [led for i, led in enumerate(arcade.leds)
                     if i in buttons]
        self.score = 0
        self.start_time = time.ticks_ms()

    def light_random(self):
        """Light a random LED that is off"""
        random.choice([led for led in self.leds if not led()]).on()

    def blink(self):
        """Blink all the half-board leds (e.g. when you win)"""
        return asyncio.gather(
            *[led.blink(300, 300, 3) for led in self.leds])


async def buzz():
    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await buzzer.tone(int(tone), 60, 0.5)
        await asyncio.sleep_ms(30)


async def app_light_chaser_1v1(time_limit=20_000, nleds=3, error_prob=0.5):
    print('Bienvenue dans le chasseur de lumière!')
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()
    
    p1 = Board([i for i, c in enumerate(arcade.color)
                if c in ("white", "blue")])
    p2 = Board([i for i, c in enumerate(arcade.color)
                if c in ("red", "yellow")])

    for _ in range(nleds):
        p1.light_random()
        p2.light_random()

    printed = 0
    print()
    while True:
        # Abort
        if 'select' in cp.pressed:
            await asyncio.sleep_ms(1)
            return

        # Finish
        if time.ticks_diff(time.ticks_ms(), p1.start_time) >= time_limit:
            break

        # Print time left
        if time.ticks_diff(time.ticks_ms(), p1.start_time) > (printed + 1) * 1000:
            printed += 1
            print(int(time_limit / 1000 - printed), end=' ')

        for board in (p1, p2):
            found = [i for i in arcade.pressed
                     if i in board.buttons and arcade.leds[i]()]
            errors = [i for i in arcade.pressed
                      if i in board.buttons and not arcade.leds[i]()]
            for _ in found:
                board.light_random()
            for idx in found:
                arcade.leds[idx].off()
            board.score += len(found)
            for _ in errors:
                if random.uniform(0, 1) < error_prob:
                    print("removing 1 point")
                    board.score -= 1
                    
        arcade.reset_flags()
        await asyncio.sleep_ms(1)

    arcade.off()
    print('\n >>> DONE <<<')
    print(f"\n Scores:")
    print(f"\t White/Blue: {p1.score}")
    print(f"\t Red/Yellow: {p2.score}")
    tasks = [buzz()]
    if p1.score > p2.score:
        tasks.append(p1.blink())
        win = (p1,)
    elif p2.score > p1.score:
        tasks.append(p2.blink())
        win = (p2,)
    else:
        tasks += [p1.blink(), p2.blink()]
        win = (p1, p2)
    await asyncio.gather(*tasks)

    # Show fixed on leds for winner
    for board in win:
        for led in board.leds:
            led.on()

    arcade.reset_flags()
    while True:
        if arcade.pressed:
            arcade.reset_flags()
            arcade.off()
            return
        await asyncio.sleep_ms(1)

def menu_light_chaser():
    asyncio.run(app_light_chaser_1v1())

async def test():
    while True:
        asyncio.run(app_light_chaser_1v1(time_limit=1000))
        time.sleep(1)
        print('monitor restart')
        arcade = get_arcadebuttons()
        arcade.reset_flags()
        while not arcade.pressed:
            await asyncio.sleep_ms(1)
        # print(arcade.pressed)

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_light_chaser_1v1)