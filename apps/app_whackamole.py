import utime as time
import urandom as random
import asyncio
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, get_controlpanel, off
from lib.score import DigitalScorer


async def app_whackamole(interval=1_000, coeff=0.95, max_miss=5):
    print('Welcome to Whack a Mole!')
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    cp = get_controlpanel()
    cp.reset_flags()

    buzzer = Buzzer()

    def light_random(forbidden=None):
        """Light a random LED that is off (not in forbidden)"""
        if forbidden is None:
            forbidden = []
        while True:
            rnd = random.randint(0, arcade.size - 1)
            if not arcade.leds[rnd]() and rnd not in forbidden:
                break
        arcade.leds[rnd].on()
        return rnd

    score = 0
    missed = 0
    off_press = 0
    last_light = time.ticks_ms()
    timer = {light_random(): time.ticks_add(last_light, 2*interval)}

    while True:
        # Interrupt
        if 'select' in cp.pressed:
            break

        # Lost
        if missed == max_miss or off_press >= 100:
            arcade.off()
            print('\n >>> Done <<<')
            print(f"\n Score: {score}")

            for tone in [880, 440*1.414, 440, 220*1.414, 220]:
                await buzzer.tone(int(tone), 60, 0.5)
                await asyncio.sleep_ms(30)

            d = DigitalScorer()
            await d.interruptable_score(score)
            break

        # Add new mole
        if time.ticks_diff(time.ticks_ms(), last_light) > interval:
            last_light = time.ticks_ms()
            timer[light_random()] = time.ticks_add(last_light, 2*int(interval))
            if interval < 250:
                coeff = 0.99
            interval *= coeff

        # Old moles disappear
        remove = [mole for mole in timer
                  if time.ticks_diff(time.ticks_ms(), timer[mole]) > 0]
        for mole in remove:
            missed += 1
            arcade.leds[mole].off()
            del timer[mole]

        # Mole pressed
        if arcade.pressed:
            found = [i for i in arcade.pressed if arcade.leds[i]()]
            if found:
                missed = 0
            for idx in found:
                arcade.leds[idx].off()
                del timer[idx]
                asyncio.create_task(buzzer.tone(440, 30, 0.5))
            score += len(found)
            off_press += len(arcade.pressed) - len(found)
            # Too harsh: press off = miss
            # if len(found) < len(arcade.pressed):
            #     missed += len(arcade.pressed) - len(found)
            arcade.reset_flags()

        await asyncio.sleep_ms(0)

    return


def test():
    asyncio.run(app_whackamole())


if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_whackamole)