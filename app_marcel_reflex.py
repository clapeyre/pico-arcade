import uasyncio as asyncio
import utime as time
import urandom as random
from lib.buttons import get_arcadebuttons, get_controlpanel
from lib.music import Music, SONGS


async def app_marcel_reflex():
    print("  >>>  Marcel's Reflex!  <<<")

    TIME_TO_PRESS = 1500
    TIME_BETWEEN_PRESS = 3000

    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    state = 0  # 0: between press (all off), 1: press quick!
    timer = time.ticks_ms()
    last = -1

    while True:

        if "select" in cp.pressed:
            # Cleanup and exit
            arcade.off()
            arcade.reset_flags()
            await asyncio.sleep_ms(0)
            return

        if state and time.ticks_diff(time.ticks_ms(), timer) > TIME_TO_PRESS:
            print("Timer reached: switching off")
            arcade.off()
            state = 0
            timer = time.ticks_ms()

        if not state and time.ticks_diff(time.ticks_ms(), timer) > TIME_BETWEEN_PRESS:
            while True:
                rnd = random.randint(0, len(arcade.leds) - 1)
                if not arcade.leds[rnd]() and not arcade[rnd] and rnd != last:
                    break
            print(f"Timer reached: switching {rnd} on")
            arcade.leds[rnd].on()
            last = rnd
            state = 1
            timer = time.ticks_ms()

        if state and arcade.pressed:
            for idx in arcade.pressed:
                print(idx)
                print(arcade.leds[idx]())
                if arcade.leds[idx]():
                    arcade.leds[idx].off()
                    song = Music(SONGS[random.choice(list(SONGS))])
                    await asyncio.create_task(song.play())
            arcade.reset_flags()

        await asyncio.sleep_ms(1)


if __name__ == "__main__":
    asyncio.run(app_marcel_reflex())
