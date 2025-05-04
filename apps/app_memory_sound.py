"""app_memory_sound.py


WAITING -> PLAYING_FIRST -> WAITING_SECOND
 |   ^         |   ^           |
 v   |         v   |           |
END   ---- PLAYING_SECOND   <--
"""
import asyncio
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel
from lib.music import Music, SONGS
from lib.score import DigitalScorer

# STATES
WAITING = 1
PLAYING_FIRST = 2
WAITING_SECOND = 3
PLAYING_SECOND = 4


class _MemoryBoard:
    """Use LED board as musical memory"""
    def __init__(self):
        self.state = WAITING
        self.arcade = get_arcadebuttons()
        self.found = []
        self.guesses = [None, None]
        self.player = None
        self.turns = 0
        self.init_songs()

    def done(self):
        """Found all the pairs?"""
        assert len(self.found) <= self.arcade.size
        return len(self.found) == self.arcade.size

    def init_songs(self):
        """Create 1 song every 2 leds"""
        self.songs = [None]*self.arcade.size
        for song in list(SONGS):
            for _ in range(2):
                while True:
                    button = random.randint(0, self.arcade.size - 1)
                    if self.songs[button] is None:
                        break
                self.songs[button] = song

    def kill_player(self):
        """Kill existing player if running, and stop any sound"""
        if self.player is not None and not self.player.done():
            self.player.cancel()
        asyncio.create_task(Music([]).play())

    def play_song(self, button):
        """Start async process to play song.
        
        Use self.kill_player() to stop early, self.player.done() to check.
        """
        self.kill_player()
        self.player = asyncio.create_task(
            Music(SONGS[self.songs[button]]).play())

    def single_pressed_button(self):
        """Get a pressed button
        
        Take first if not sure.
        Avoid first guess if no second guess yet (don't press 1 button twice).
        """
        forbidden = self.found[:]
        if None in self.guesses:
            forbidden += self.guesses
        pressed = [but for but in self.arcade.pressed
                   if but not in forbidden]
        # print('ZZZ has a button been pressed?')
        # print(self.arcade.pressed)
        # print(forbidden)
        self.arcade.reset_flags()
        return pressed[0] if pressed else None

    def check_guesses(self):
        if None in self.guesses:
            return
        g1, g2 = self.guesses
        if self.songs[g1] == self.songs[g2]:
            print(f"YYY adding {self.guesses} to self.found")
            self.found += self.guesses
        self.guesses = [None, None]


async def app_memory_sound():
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    board = _MemoryBoard()
    print('YYY', board.state, board.turns)
    while True:
        # Abort
        if 'select' in cp.pressed:
            board.player.cancel()
            await asyncio.sleep_ms(1)
            return

        # Finished!
        if board.state == WAITING and board.done():
            print(board.done())
            break

        # Guess n°1
        if (board.state == WAITING or 
            (board.state == PLAYING_SECOND and not board.player.done())):
            pressed = board.single_pressed_button()
            if pressed is not None:
                board.guesses[0] = pressed
                board.turns += 1
                for i, led in enumerate(arcade.leds):
                    if i not in board.found:
                        led.off()
                arcade.leds[pressed].on()
                board.play_song(pressed)
                board.state = PLAYING_FIRST
                continue
        
        # Song 1 done
        if board.state == PLAYING_FIRST and board.player.done():
            board.state = WAITING_SECOND
            continue

        # Guess n°2
        if board.state in [PLAYING_FIRST, WAITING_SECOND]:
            # print('KKK', board.player.done())
            pressed = board.single_pressed_button()
            if pressed is not None:
                board.guesses[1] = pressed
                board.check_guesses()
                arcade.leds[pressed].on()
                board.play_song(pressed)
                board.state = PLAYING_SECOND
                continue

        # Song 2 done
        if board.state == PLAYING_SECOND and board.player.done():
            for i, led in enumerate(arcade.leds):
                if i not in board.found:
                    led.off()
            board.state = WAITING
            continue

        await asyncio.sleep_ms(1)
        # print('YYY', board.__dict__)
    
    print("All done!")
    print(f"You finished in {board.turns} turns.")
    d = DigitalScorer()
    await asyncio.run(d.interruptable_score(board.turns))
    return
        






