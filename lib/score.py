import utime as time
import uasyncio as asyncio
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel


def binary_score(score):
    arcade = get_arcadebuttons()
    arcade.off()

    leds = [arcade.leds[i]
            for i in (0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15)]
    for led, v in zip(leds, f'{score:016b}'):
        led.output(val=int(v)) 


class DigitalScorer:
    """Show digits on 4x3 leds"""
    digits = """\
OOO  ..O  OOO  OOO  O..  OOO  .OO  OOO  OOO  OOO
O.O  .OO  ..O  .OO  O.O  OO.  O..  ..O  OOO  OOO
O.O  ..O  .O.  ..O  OOO  ..O  OOO  ..O  O.O  ..O
OOO  ..O  OOO  OOO  ..O  OO.  OOO  ..O  OOO  .O."""

    def _pattern(self, digit):
        return "".join("".join(col)
                       for col in zip(*self.digits.split('\n'))).split()[digit]

    def show_digit(self, digit):
        arcade = get_arcadebuttons()
        for led, flag in zip(arcade.leds[:12], self._pattern(digit)):
            if {'.': False, 'O': True}[flag]:
                led.on()
    
    async def display_score(self, score, interval=800):
        arcade = get_arcadebuttons()
        arcade.off()
        for digit in str(score):
            digit = int(digit)
            self.show_digit(digit)
            await asyncio.sleep_ms(interval)
            arcade.off()

    async def interruptable_score(self, score):
        arcade = get_arcadebuttons()
        arcade.reset_flags()
        while not arcade.pressed:
            await self.display_score(score)
            await asyncio.sleep_ms(1000)


async def _test():
    d = DigitalScorer()
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    cp = get_controlpanel()
    cp.reset_flags()
    key = 0
    while 'select' not in cp.pressed:
        d.light(key)
        while not arcade.pressed:
            await asyncio.sleep_ms(1)
        key = (key + 1) % 10
        arcade.reset_flags()
        arcade.off()
        

# REMINDER
#  0  4  8 12
#  1  5  9 13
#  2  6 10 14
#  3  7 11 15


async def pharmacy_blink_circle(inwards=False):
    circles = [
        [5, 6, 9, 10],
        [i for i in range(16) if i not in [5, 6, 9, 10]]]
    arcade = get_arcadebuttons()
    arcade.off()

    sequence = [] + circles
    if inwards:
        sequence = sequence[::-1]
    for seq in sequence:
        for idx in seq:
            arcade.leds[idx].on()
        await asyncio.sleep_ms(200)
        arcade.off()


async def pharmacy_blink_spiral(inwards=False):
    sequence = [0, 4, 8, 12, 13, 14, 15, 11, 7, 3, 2, 1, 5, 9, 10, 6]
    arcade = get_arcadebuttons()
    arcade.off()

    direction = -1 if inwards else 1
    for idx in sequence[::direction]:
        arcade.leds[idx].on()
        await asyncio.sleep_ms(50)
    for idx in sequence[::direction]:
        arcade.leds[idx].off()
        await asyncio.sleep_ms(50)


async def pharmacy_blink_cross(clockwise=True):
    center = [5, 6, 9, 10]
    branches = [
        [0, 12, 15, 3],
        [4, 13, 11, 2],
        [8, 14, 7, 1],
    ]
    arcade = get_arcadebuttons()
    for idx in range(16):
        if idx in center:
            arcade.leds[idx].on()
        else:
            arcade.leds[idx].off()

    direction = 1 if clockwise else -1
    for branch in branches[::direction]:
        for idx in branch:
            arcade.leds[idx].on()
        await asyncio.sleep_ms(150)
        for idx in branch:
            arcade.leds[idx].off()


def test():
    asyncio.run(_test())


def test2():
    d = DigitalScorer()
    score = random.randint(10, 9999)
    print(score)
    asyncio.run(d.interruptable_score(score))