import utime as time
import urandom as random
import uasyncio as asyncio
from drivers.buzzer import Buzzer
from drivers.sh1107 import SH1107_I2C
from lib.buttons import button_init, on, off
from lib.score import DigitalScorer

def flash(led, tone, lvl):
    buzzer = Buzzer()
    buzzer.start_tone(tone, lvl)
    on(led)
    time.sleep_ms(300)
    buzzer.end_tone()
    off(led)
    time.sleep_ms(100)

def app_sequence(sound_level=1):
    print("Bienvenue dans le memory 2.0!")
    buzzer = Buzzer()
    oled = SH1107_I2C()
    oled.fill(0)
    oled.text('Memory', 0, 0, 1)
    oled.show()
    buttons, leds = button_init(16)
    for led in [0, 1, 4, 5, 8, 9, 12, 13]:
        on(leds[led])
    
    time.sleep_ms(500)
    buttons = [buttons[i] for i in [3, 7, 11, 15]]
    leds = [leds[i] for i in [3, 7, 11, 15]]
    sounds = [int(220*1.4**i) for i in range(1, len(buttons) + 1)]
    seq = []
    while True:
        while True:
            rnd = random.randint(0, len(leds) - 1)
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
                        d = DigitalScorer()
                        asyncio.run(d.interruptable_score(len(seq) - 1))
                        time.sleep_ms(500)
                        return
                    while not button.value():
                        time.sleep_ms(10)
                    off(leds[idx])
                    buzzer.end_tone()
            time.sleep_ms(10)
        time.sleep_ms(200)

if __name__ == '__main__':
    buttons, leds = button_init()
    while True:
        app_sequence()
        time.sleep(0.3)
        while buttons[0].value():
            time.sleep(0.01)
            