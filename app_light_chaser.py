import utime
import _thread
import urandom
import uasyncio as asyncio
from lib.buttons import button_init, on, off
from lib.sh1107 import get_oled


#score = 0
async def scorer():
    global score
    # from lcd1602 import LCD
    # lcd = LCD()
    new_score = -1
    while True:
        if new_score != score:
            print(f"Light-chaser 0.1\n    Score: {score}")
            # lcd.clear()
            # lcd.message(f"Light-chaser 0.1\n    Score: {score}")
            # lcd.openlight()
            new_score = score
        await asyncio.sleep_ms(100)
#_thread.start_new_thread(scorer, ())

# timer_click = 0
def app_light_chaser(hardcore=False, timer=10_000):
    oled = get_oled()
    print('Bienvenue dans le chasseur de lumière!')
    oled.fill(0)
    oled.text("Chasse", 0, 0, 1)
    oled.text("Lumiere", 0, 10, 1)
    if hardcore:
        print('Mode hardcore activé')
        oled.text("Hardcore", 0, 20, 1)
    oled.show()
    score = 0
    start = utime.ticks_ms()
    buttons, leds = button_init()
    recent = -1
    #on(leds[urandom.randint(0, len(leds) - 1)])
    while True:
        # print("Setting a random LED to 1")
        while True:
            rnd = urandom.randint(0, len(leds) - 1)
            if not leds[rnd].value() and buttons[rnd].value() and rnd != recent:
                on(leds[rnd])
                recent = rnd
                break
            utime.sleep_ms(1)

        light_found = False
        while not light_found:
            for button, led in zip(buttons, leds):
                if not button.value():
                    # print(f'led status: {[led.value() for led in leds]}')
                    # print(f'button status: {[but.value() for but in buttons]}')
                    # utime.sleep(0.3)
                    if led.value():
                        off(led)
                        light_found = True
                        score += 1
                        while not button.value():
                            utime.sleep_ms(1)
                        #print(f"Score is: {score}")
                        #print(utime.ticks_diff(start, utime.ticks_ms()))
                    elif hardcore:
                        while not button.value():
                            utime.sleep_ms(1)
                        score -= 1
            utime.sleep_ms(1)
        if utime.ticks_diff(utime.ticks_ms(), start) >= timer:
            print('\n >>> FINI <<<')
            print(f"\n Score: {score}")
            oled.fill(0)
            oled.text('Fini!', 0, 0, 1)
            oled.text('Score:', 0, 20, 1)
            oled.text(f'  {score}', 0, 40, 1)
            oled.show()
            return
        # else:
        #     print(f"                   Debug: {score}")

if __name__ == '__main__':
    buttons, leds = button_init()
    while True:
        app_light_chaser()
        utime.sleep(0.3)
        while buttons[0].value():
            utime.sleep(0.01)