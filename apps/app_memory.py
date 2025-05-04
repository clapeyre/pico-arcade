from drivers.buzzer import Buzzer
from lib.oled import get_oled
from lib.buttons import button_init, on, off
from lib.score import DigitalScorer
import utime as time
import urandom as random
import asyncio

def flash(led, tone, lvl):
    buzzer = Buzzer()
    buzzer.start_tone(tone, lvl)
    on(led)
    time.sleep_ms(300)
    buzzer.end_tone()
    off(led)
    time.sleep_ms(100)

def app_memory(sound_level=1):
    print("Bienvenue dans le memory 2.0!")
    buzzer = Buzzer()
    oled = get_oled()
    oled.clear_screen()
    oled.draw_centered_text('Memory', 0)
    oled.show()
    buttons, leds = button_init(16)
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
                        oled.clear_screen()
                        oled.draw_centered_text('Perdu!', 0)
                        oled.draw_centered_text('Score:', 20)
                        oled.draw_centered_text(f'{len(seq) - 1}', 40)
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
    from lib.test_utils import run_test
    run_test(app_memory)
            