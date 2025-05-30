import asyncio
import utime as time
import urandom as random
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, get_controlpanel


class Song:
    def __init__(self, max_len=6):
        self.tunes = (220, 220*1.414, 440, 440*1.414, 880)
        self.seq = []
        self.max_len = max_len
        self.buzzer = Buzzer()

    def incr(self):
        if len(self.seq) < 2 * self.max_len:
            self.seq += [(random.choice(self.tunes), 1), (100, 0)]

    async def play(self):
        for tone, level in self.seq:
            await self.buzzer.tone(int(tone), 100, level)


async def app_marcels_quest():
    print("  >>>  Bienvenue dans Marcel's Quest!  <<<")

    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    song = Song()

    last = -1
    while 'select' not in cp.pressed:
        while True:
            rnd = random.randint(0, len(arcade.leds) - 1)
            if not arcade.leds[rnd].value() and not arcade[rnd] and rnd != last:
                break
            await asyncio.sleep_ms(1)

        last = rnd
        arcade.leds[rnd].on()
        song.incr()

        while rnd not in arcade.pressed and 'select' not in cp.pressed:
            await asyncio.sleep_ms(1)
        if 'select' in cp.pressed:
            return
        await asyncio.create_task(song.play())
        arcade.leds[rnd].off()
        arcade.reset_flags()

def menu_marcels_quest():
    asyncio.run(app_marcels_quest())
            

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_marcels_quest)