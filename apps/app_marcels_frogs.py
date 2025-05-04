import asyncio
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel, array_to_index
from lib.music import Music, SONGS


async def light_square(size=None):
    arcade = get_arcadebuttons()
    arcade.off()

    if size:
        if isinstance(size, int):
            size = (size, size)
    else:
        while True:
            size = (random.randint(1, 4),
                    random.randint(1, 4))
            if size[0] == 4 or size[1] == 4 or size[0] * size[1] > 6 or size[0] * size[1] < 3:
                continue
            break
    
    start = (random.randint(0, 4 - size[0]),
             random.randint(0, 4 - size[1]))
    
    for i in range(size[0]):
        for j in range(size[1]):
            index = array_to_index(start[0] + i, start[1] + j)
            arcade.leds[index].on()
    
    await asyncio.sleep_ms(1)


async def app_marcels_frogs():
    print("  >>>  Bienvenue dans Marcel's Frogs!  <<<")

    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    while 'select' not in cp.pressed:
        await light_square()

        while any([led() for led in arcade.leds]):

            while not arcade.pressed and 'select' not in cp.pressed:
                await asyncio.sleep_ms(1)
            if 'select' in cp.pressed:
                return
            
            for idx in arcade.pressed:
                if arcade.leds[idx]():
                    arcade.leds[idx].off()
            arcade.reset_flags()
        
        song = Music(SONGS[random.choice(list(SONGS))])
        await asyncio.create_task(song.play())
        arcade.reset_flags()

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_marcels_frogs)