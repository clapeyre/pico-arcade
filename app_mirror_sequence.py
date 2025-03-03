import utime as time
import urandom as random
import uasyncio as asyncio

from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, COLORS, get_controlpanel


class Board:
    def __init__(self):
        self.arcade = get_arcadebuttons()
        self.buzzer = Buzzer()
        self.leds = self.arcade.leds
        self.left = [i for i, c in enumerate(self.arcade.color)
                     if c in ("white", "blue")]
        self.right = [i for i, c in enumerate(self.arcade.color)
                      if c in ("red", "yellow")]
        self.active = self.left
        self.start_time = time.ticks_ms()
        self.sounds = tuple(int(110*1.4**i) for i in range(len(self.left)))
        self.currently_pressed = None

        """
        0 4 |  8 12   0 <-> 12
        1 5 |  9 13   1 <-> 13
        2 6 | 10 14     ...
        3 7 | 11 15   4 <-> 8
        """
        self.mirror = {0: 12, 1: 13, 2: 14, 3: 15,
                       4:  8, 5:  9, 6: 10, 7: 11}
        self.mirror.update({v: k for k, v in self.mirror.items()})
        print('TTT almost done initializing board')

        self._monitor = asyncio.create_task(self.button_sounds())
        print('TTT board button monitor running')

    def play_tone(self, idx):
        sound_nb = idx if idx < 8 else self.mirror[idx]
        self.buzzer.start_tone(self.sounds[sound_nb], 1)

    def end_tone(self):
        self.buzzer.end_tone()

    async def button_sounds(self):
        while True:
            # Active button press
            if self.currently_pressed is None and self.arcade.pressed:
               #  print(f"TTT detected button press: {self.arcade.pressed}")
                pressed = self.arcade.pressed[0]
                self.arcade.reset_pressed()
                if pressed in self.active:
                    self.currently_pressed = pressed
                    self.play_tone(pressed)
                    self.on(pressed)

            # if self.arcade.released:
            #     print(self.arcade.released)
            #     self.arcade.reset_released()

            # Pressed button release
            # print(self.currently_pressed, self.arcade.released)
            if (self.currently_pressed is not None and
                self.arcade.released_flag[self.currently_pressed]):
                    # print(f"TTT detected button release: {self.arcade.released}")
                    self.arcade.reset_released()
                    self.arcade.off()
                    self.currently_pressed = None
                    self.end_tone()
            await asyncio.sleep_ms(0)
    
    def stop(self):
        self.end_tone()
        self._monitor.cancel()
        del self

    def blink(self):
        """Blink all the half-board leds (e.g. when you win)"""
        return [self.leds[idx].blink(300, 300, 3) for idx in self.active]

    def on(self, idx):
        """Light an LED and it's mirror"""
        self.leds[idx].on()
        self.leds[self.mirror[idx]].on()

    def turn_change(self):
        self.active = self.right if self.active == self.left else self.left
        self.arcade.reset_flags()
        # print("III Turn change. Now:", self.active)


class Sequence:
    def __init__(self, mirror):
        self.mirror = mirror
        self._sequence = []
    
    def __len__(self):
        return len(self._sequence)

    def __str__(self):
        return self._sequence

    def _mirror(self, val):
        return val if val < 8 else self.mirror[val]

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
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    # Rule reminder: left starts
    for idx in (1, 4, 5, 6, 9, 13):
        arcade.leds[idx].on()
    await asyncio.sleep(1)
    arcade.off()
    arcade.reset_flags()

    board = Board()
    sequence = Sequence(board.mirror)
    # print(board.__dict__)

    # Start!
    guess = []
    # print("TTT start mainloop")
    while True:
        if 'select' in cp.pressed:  # Abort
            board.stop()
            await asyncio.sleep_ms(0)
            return
        
        if board.currently_pressed is not None:
            pressed = int(board.currently_pressed)
            # Don't move forward until button is released
            while board.currently_pressed is not None:
                await asyncio.sleep_ms(1)

            guess.append(pressed)
            print("Compare:", guess, sequence)

            if not sequence.check(guess):  # You lose!
                board.end_tone()
                board.turn_change()
                break

            # Added one to current sequence, change turn
            if len(guess) > len(sequence):
                sequence.append(pressed)
                guess = []
                board.turn_change()
                board.arcade.on()
                await asyncio.sleep_ms(300)
                board.arcade.off()

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

    board.stop()
    arcade.reset_flags()
    while True:
        if arcade.pressed:
            arcade.reset_flags()
            arcade.off()
            return
        await asyncio.sleep_ms(1)
