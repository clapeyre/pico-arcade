import utime as time
import urandom as random
import asyncio
from drivers.buzzer import Buzzer
from lib.oled import get_oled
from lib.buttons import get_arcadebuttons
from lib.score import DigitalScorer


async def app_light_chaser(hardcore=False, timer=20_000, nleds=3):
    oled = get_oled()
    print('Bienvenue dans le chasseur de lumière!')
    oled.clear_screen()
    oled.draw_centered_text("Chasse", 0)
    oled.draw_centered_text("Lumiere", 10)
    if hardcore:
        print('Mode hardcore activé')
        oled.draw_centered_text("Hardcore", 20)
    oled.show()
    score = 0
    start = time.ticks_ms()
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()

    def light_random(forbidden=None):
        """Light a random LED that is off (not in forbidden)"""
        if forbidden is None:
            forbidden = []
        while True:
            rnd = random.randint(0, arcade.size - 1)
            if not arcade.leds[rnd].value() and rnd not in forbidden:
                break
            # time.sleep_ms(1)
        arcade.leds[rnd].on()
        return rnd

    for _ in range(nleds):
        light_random()

    printed = 0
    print()
    while True:
        while not arcade.pressed and time.ticks_diff(time.ticks_ms(), start) < timer:
            await asyncio.sleep_ms(1)
            if time.ticks_diff(time.ticks_ms(), start) > (printed + 1) * 1000:
                printed += 1
                print(printed, end=' ')

        if time.ticks_diff(time.ticks_ms(), start) >= timer:
            break

        found = [i for i in arcade.pressed if arcade.leds[i]()]
        for _ in found:
            light_random()
        for idx in found:
            arcade.leds[idx].off()
        score += len(found)

        if hardcore:
            score -= (len(arcade.pressed) - len(found))
        
        arcade.reset_flags()

    arcade.off()
    print('\n >>> FINI <<<')
    print(f"\n Score: {score}")
    oled.clear_screen()
    oled.draw_centered_text('Fini!', 0)
    oled.draw_centered_text('Score:', 20)
    oled.draw_centered_text(f'{score}', 40)
    oled.show()

    buzzer = Buzzer()
    for tone in [880, 440*1.414, 440, 220*1.414, 220]:
        await asyncio.create_task(buzzer.tone(int(tone), 60, 0.5))
        time.sleep_ms(30)

    d = DigitalScorer()
    await d.interruptable_score(score)

    return

def menu_light_chaser():
    asyncio.run(app_light_chaser())

async def test():
    try:
        while True:
            # Run the game with a short timer for testing
            await app_light_chaser(timer=1000)
            print('Game completed, waiting for button press or timeout...')
            
            # Setup arcade buttons
            arcade = get_arcadebuttons()
            arcade.reset_flags()
            
            # Wait for button press with timeout
            start_time = time.ticks_ms()
            while not arcade.pressed:
                if time.ticks_diff(time.ticks_ms(), start_time) > 5000:  # 5 second timeout
                    print('Timeout reached, restarting game...')
                    break
                await asyncio.sleep_ms(10)
            
            # Cleanup
            arcade.off()
            arcade.reset_flags()
            
    except KeyboardInterrupt:
        print('Test interrupted by user')
    finally:
        # Ensure cleanup happens even if interrupted
        arcade = get_arcadebuttons()
        arcade.off()
        arcade.reset_flags()
        print('Test cleanup completed')

if __name__ == '__main__':
    from lib.test_utils import run_test
    run_test(app_light_chaser, timer=1000)