from lib.buttons import button_init, on, off
from lib.buzzer import buzzer
from lib.sh1107 import get_oled
import utime
import urandom
import uasyncio as asyncio

def flash(led, tone, lvl):
    buzzer.start_tone(tone, lvl)
    on(led)
    utime.sleep_ms(300)
    buzzer.end_tone()
    off(led)
    utime.sleep_ms(100)

def app_memory(sound_level=1):
    print("Bienvenue dans le memory 2.0!")
    oled = get_oled()
    oled.fill(0)
    oled.text('Memory', 0, 0, 1)
    oled.show()
    buttons, leds = button_init(16)
    buttons = [buttons[i] for i in [3, 7, 11, 15]]
    leds = [leds[i] for i in [3, 7, 11, 15]]
    sounds = [int(220*1.4**i) for i in range(1, len(buttons) + 1)]
    seq = []
    while True:
        while True:
            rnd = urandom.randint(0, len(leds) - 1)
            three_in_row = [rnd != s for s in seq[-3:]]
            if any(three_in_row) or not three_in_row:
                break
        seq.append(rnd)
        for idx in seq:
            flash(leds[idx], sounds[idx], sound_level)
        
        seq_try = []
        while len(seq_try) < len(seq):
            #print([button.value() for button in buttons])
            for idx, button in enumerate(buttons):
                if not button.value():
                    buzzer.start_tone(sounds[idx], sound_level)
                    on(leds[idx])
                    seq_try.append(idx)
                    if seq_try != seq[:len(seq_try)]:
                        off(leds[idx])
                        buzzer.end_tone()
                        print('\n >>> Perdu! <<<')
                        print(f'Score: {len(seq) - 1}')
                        oled.fill(0)
                        oled.text('Perdu!', 0, 0, 1)
                        oled.text('Score:', 0, 20, 1)
                        oled.text(f'  {len(seq) - 1}', 0, 40, 1)
                        oled.show()
                        return
                    while not button.value():
                        utime.sleep_ms(10)
                    off(leds[idx])
                    buzzer.end_tone()
            utime.sleep_ms(10)
        utime.sleep_ms(200)

if __name__ == '__main__':
    buttons, leds = button_init()
    while True:
        app_memory()
        utime.sleep(0.3)
        while buttons[0].value():
            utime.sleep(0.01)
            