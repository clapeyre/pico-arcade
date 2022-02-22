import utime as time
import urandom as random
import uasyncio as asyncio

from drivers.buzzer import Buzzer
from lib.buttons import (get_arcadebuttons, _ArcadeButtons,
                         COLORS, get_controlpanel)


class Board:
    def __init__(self):
        #self.arcade = _ArcadeButtons(pressed_flag=False)
        self.arcade = get_arcadebuttons()
        self.buttons = self.arcade.buttons
        self.buzzer = Buzzer()
        self.leds = self.arcade.leds
        self.left = [i for i, c in enumerate(self.arcade.color)
                     if c in ("white", "blue")]
        self.right = [i for i, c in enumerate(self.arcade.color)
                      if c in ("red", "yellow")]
        self.active = self.left
        self.start_time = time.ticks_ms()
        self.sounds = [int(110*1.4**i) for i in range(8)]
        self.pressed = None
        self._create_mirror()
        self._press_behavior()
        self._release_behavior()

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

    def _press_behavior(self):
        """Associate press callback to each button"""
        for i, but in enumerate(self.buttons):
            but.press_func(self._press_func, (i,))

    def _press_func(self, idx):
        """Callback when a button is pressed.
        
        Tasks: light both mirror LEDs, play a sound.
        Ignore if an LED is already on.
        """
        if ((any([led() for led in self.leds])) or
            (idx not in self.active) or
            (self.pressed is not None)):
            return
        
        sound_nb = idx if idx < 8 else self.mirror[idx]
        self.buzzer.start_tone(self.sounds[sound_nb], 1)
        self.on(idx)
        self.pressed = idx

    def _release_behavior(self):
        """Associate release callback to each button"""
        for i, but in enumerate(self.buttons):
            but.release_func(self._release_func, (i,))

    def _release_func(self, idx):
        """Callback when a button is released.
        
        Tasks: turn all buttons off, kill buzzer.
        """
        print("Release button called")
        if idx not in self.active:
            return
        self.arcade.off()
        self.buzzer.end_tone()
        self.pressed = None

    def blink(self):
        """Blink all the half-board leds (e.g. when you win)"""
        return [self.leds[idx].blink(300, 300, 3) for idx in self.active]

    def on(self, idx):
        """Light an LED and it's mirror"""
        self.leds[idx].on()
        self.leds[self.mirror[idx]].on()

    async def turn_change(self):
        while self.pressed is not None:
            await asyncio.sleep_ms(1)
        self.active = self.right if self.active == self.left else self.left
        print("III Turn change:", self.active)


class Sequence:
    def __init__(self, board):
        self.board = board
        self._sequence = []
    
    def __len__(self):
        return len(self._sequence)

    def __str__(self):
        return self._sequence

    def _mirror(self, val):
        return val if val < 8 else self.board.mirror[val]

    def check(self, seq):
        if len(seq) > len(self):
            if len(seq) - len(self) > 1:
                return False
            return self.check(seq[:-1])
        return list(map(self._mirror, seq)) == self._sequence[:len(seq)]

    def append(self, val):
        self._sequence.append(self._mirror(val))


async def win_tone():
    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await buzzer.tone(int(tone), 60, 0.5)
        await asyncio.sleep_ms(30)


async def app_mirror_sequence():
    print(' WELCOME to Mirror Sequence! ')

    arcade = get_arcadebuttons()
    board = Board()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    # Rule reminder: left starts
    for idx in (1, 4, 5, 6, 9, 13):
        arcade.leds[idx].on()
    await asyncio.sleep(1)
    arcade.off()

    sequence = Sequence(board)

    # Start!
    guess = []
    while True:
        # Abort
        if 'select' in cp.pressed:
            await asyncio.sleep_ms(0)
            return
        
        if board.pressed:
            pressed = int(board.pressed)
            guess.append(pressed)
            board.pressed = None
            print("Compare:", guess, sequence)

            if not sequence.check(guess): # You lose!
                await board.turn_change()
                break

            # Added one to current sequence, change turn
            if len(guess) > len(sequence):
                sequence.append(pressed)
                guess = []
                await board.turn_change()
                board.arcade.on()
                await asyncio.sleep_ms(300)
                board.arcade.off()
                continue

        await asyncio.sleep_ms(0)

    # print("DEBUG")
    # print(arcade)
    arcade.off()
    print('\n >>> DONE <<<')

    tasks = [win_tone()]
    tasks += board.blink()
    await asyncio.gather(*tasks)

    # Show fixed on leds for winner
    for idx in board.active:
        arcade.leds[idx].on()
    await asyncio.sleep_ms(1000)

    arcade.pressed_flag_behaviour()
    arcade.reset_flags()
    while True:
        if arcade.pressed:
            arcade.reset_flags()
            arcade.off()
            return
        await asyncio.sleep_ms(1)
