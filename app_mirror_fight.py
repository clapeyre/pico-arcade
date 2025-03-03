import utime as time
import urandom as random
import uasyncio as asyncio
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, COLORS, get_controlpanel


class Board:
    def __init__(self):
        arcade = get_arcadebuttons()
        self.leds = arcade.leds
        self.left = [i for i, c in enumerate(arcade.color)
                     if c in ("white", "blue")]
        self.right = [i for i, c in enumerate(arcade.color)
                      if c in ("red", "yellow")]
        self.start_time = time.ticks_ms()
        self._create_mirror()

    def _create_mirror(self):
        """
        0 4 |  8 12   0 <-> 12
        1 5 |  9 13   1 <-> 13
        2 6 | 10 14     ...
        3 7 | 11 15   4 <-> 8
        """
        self.mirror = {0: 12, 1: 13, 2: 14, 3: 15,
                       4:  8, 5:  9, 6: 10, 7: 11}
        self.mirror.update({v: k for k, v in self.mirror.items()})

    def light_random(self):
        """Light a random LED that is off"""
        idx = random.choice([i for i, led in enumerate(self.leds)
                             if not led()])
        self.leds[idx].on()
        self.leds[self.mirror[idx]].on()

    def blink(self, left=True):
        """Blink all the half-board leds (e.g. when you win)"""
        leds = self.leds[:8] if left else self.leds[8:]
        return [led.blink(300, 300, 3) for led in leds]
    
    def toggle(self, idx):
        self.leds[idx].toggle()
        self.leds[self.mirror[idx]].toggle()

    def state(self):
        """Current state. Access underlying pin for optim purposes."""
        return [led.pin.value() for led in self.leds]


async def buzz():
    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await buzzer.tone(int(tone), 60, 0.5)
        await asyncio.sleep_ms(30)


async def app_mirror_fight(time_limit=20_000):
    print(' WELCOME to Mirror Fight! ')
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    board = Board()
    # Rule reminder: left must be on, right off
    for idx in board.left:
        arcade.leds[idx].on()
    await asyncio.sleep(1)
    arcade.off()

    # Start!
    left_wins = None
    for _ in range(4):
        board.light_random()
    while True:
        # Abort
        if 'select' in cp.pressed:
            await asyncio.sleep_ms(0)
            return

        # Time limit
        if time.ticks_diff(time.ticks_ms(), board.start_time) >= time_limit:
            break

        # Win
        state = board.state()
        if all(state):
            left_wins = True
            break
        if not sum(state):
            left_wins = False
            break

        [board.toggle(idx) for idx in arcade.pressed]

        arcade.reset_flags()
        await asyncio.sleep_ms(0)

    # print("DEBUG")
    # print(arcade)
    arcade.off()
    print('\n >>> DONE <<<')

    tasks = [buzz()]
    if left_wins is None:
        mapping = range(16)
        print(' Time limit reached')
    else:
        mapping = board.left if left_wins else board.right
        tasks += board.blink(left=left_wins)
    await asyncio.gather(*tasks)

    # Show fixed on leds for winner
    for idx in mapping:
        arcade.leds[idx].on()
    await asyncio.sleep(1)

    arcade.reset_flags()
    while True:
        if arcade.pressed:
            arcade.reset_flags()
            arcade.off()
            return
        await asyncio.sleep_ms(1)
