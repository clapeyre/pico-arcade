import uasyncio as asyncio
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel
from lib.music import Music, SONGS


async def app_memory_sound():
    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel(pressed_flag=True)
    cp.reset_flags()

    # Init
    songs = [None]*16
    for song in list(SONGS):
        while True:
            button = random.randint(0, 15)
            if songs[button] is None:
                break
        songs[button] = song
        while True:
            button = random.randint(0, 15)
            if songs[button] is None:
                break
        songs[button] = song

    turns = 0
    while not all(led() for led in arcade.leds):
        if 'select' in cp.pressed:
            return
        
        while not [but for but in arcade.pressed if not arcade.leds[but]()]:
            await asyncio.sleep_ms(1)

        turns += 1

        first_button = [but for but in arcade.pressed if not arcade.leds[but]()][0]
        arcade.leds[first_button].on()
        song = Music(SONGS[songs[first_button]])
        await asyncio.create_task(song.play())
        arcade.reset_flags()

        while not [but for but in arcade.pressed if not arcade.leds[but]()]:
            await asyncio.sleep_ms(1)

        second_button = [but for but in arcade.pressed if not arcade.leds[but]()][0]
        arcade.leds[second_button].on()
        song2 = Music(SONGS[songs[second_button]])
        await asyncio.create_task(song2.play())
        arcade.reset_flags()

        if songs[first_button] == songs[second_button]:
            continue
        else:
            arcade.leds[first_button].off()
            arcade.leds[second_button].off()
        arcade.reset_flags()
    
    print("All done!")
    print(f"You finished in {turns} turns.")
        






