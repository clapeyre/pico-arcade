from lib.buzzer import buzzer
from lib.buttons import button_init, on, off, _all_buttons
import uasyncio
import utime


async def blink(led, up, down, times):
    for _ in range(times):
        on(led)
        await uasyncio.sleep_ms(up)
        off(led)
        await uasyncio.sleep_ms(down)


async def buzz(tune):
    tunes = [[220, 220*1.414, 440, 440*1.414, 880],
             [220, 220*1.414, 440, 440*1.414, 880][::-1],
             [220, 220*1.414, 220, 440, 220, 440*1.414],
             [220, 220*1.414, 220, 440, 220, 440*1.414][::-1],
             ]
    for tone in tunes[tune]:
        buzzer.tone(int(tone), 60, 0.1)
        await uasyncio.sleep_ms(30)


async def app_buzzer():
    print('Bienvenue dans le buzzer!')
    buttons, leds = button_init()
    buzzers = [pair for i, pair in enumerate(zip(buttons, leds))
               #if i in (0, 1)
               ]

    map(on, leds)
    print("Ready to buzz?")
    while True:
        list(map(on, leds))
        for idx, (button, led) in enumerate(buzzers):
            if not button.value():
                list(map(off, leds))
                uasyncio.create_task(buzz(idx))
                await uasyncio.create_task(blink(led, 100, 100, 3))
                print("Ready to buzz?")
        #if not _all_buttons()[0][-1].value():
        #    return

if __name__ == '__main__':
    uasyncio.run(app_buzzer())