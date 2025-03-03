import uasyncio as asyncio
import utime as time
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel, array_to_index, index_to_array
from drivers.sh1107 import SH1107_I2C
from lib.music import Music, SONGS


class Symmetry:
    def __init__(self):
        self._init_pattern()

    def _init_pattern(self):
        self.pattern = [[False]*4 for _ in range(2)]

    def new_pattern(self, proportion=0.5):
        """Define a pattern to symmetrize and light matching LEDs"""
        self._init_pattern()

        while sum(a for line in self.pattern for a in line) < proportion * 8:
            self.pattern[random.randint(0, 1)][random.randint(0, 3)] = True
    
        arcade = get_arcadebuttons()
        arcade.off()
        for x in range(2):
            for y in range(4):
                if self.pattern[x][y]:
                    index = array_to_index(x, y)
                    arcade.leds[index].on()
    
    @property
    def full_pattern(self):
        """Full board if symmetry is matched"""
        out = self.pattern + self.pattern[::-1]
        # Transpose and flatten
        return [e for pair in zip(*out) for e in pair]


async def app_symmetry():
    print("  >>>  Welcome to Symmetry !  <<<")

    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    oled = SH1107_I2C()
    oled.fill(0)
    oled.text('Symmetry', 0, 0, 1)
    oled.show()

    sym = Symmetry()

    while 'select' not in cp.pressed:
        sym.new_pattern()

        while sym.full_pattern != [bool(led()) for led in arcade.leds]:

            while not arcade.pressed and 'select' not in cp.pressed:
                await asyncio.sleep_ms(1)
            if 'select' in cp.pressed:
                return
            
            for idx in arcade.pressed:
                x, _ = index_to_array(idx)
                if x > 1:
                    arcade.leds[idx].toggle()
            arcade.reset_flags()
        
        song = Music(SONGS[random.choice(list(SONGS))])
        await asyncio.create_task(song.play())

if __name__ == '__main__':
    asyncio.run(app_symmetry())