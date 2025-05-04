import gc
import utime as time
import asyncio
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, get_controlpanel, COLORS
from lib.oled import get_oled
from apps.app_sequence import app_sequence
from apps.app_light_chaser import app_light_chaser
from apps.app_light_chaser_1v1 import app_light_chaser_1v1
from apps.app_buzzer import app_buzzer
from apps.app_marcels_quest import app_marcels_quest
from apps.app_marcels_frogs import app_marcels_frogs
from apps.app_marcel_reflex import app_marcel_reflex
from apps.app_symmetry import app_symmetry
from apps.app_memory_sound import app_memory_sound
from apps.app_whackamole import app_whackamole
from apps.app_mirror_fight import app_mirror_fight
from apps.app_mirror_sequence import app_mirror_sequence
from apps.app_tug_of_war import app_tug_of_war
from apps.app_idle import app_idle
from lib.menu import GameCategory, GameMenu

# BOARD
#  0  4  8 12
#  1  5  9 13
#  2  6 10 14
#  3  7 11 15
# GAMES = [
#     # Hard solo games
#     (app_light_chaser, {'hardcore': True}),    # 0
#     (app_sequence, {}),                        # 1
#     (app_memory_sound, {}),                    # 2
#     (app_whackamole, {}),                      # 3
#     # Easy solo games
#     (app_marcels_quest, {}),                   # 4
#     (app_marcels_frogs, {}),                   # 5
#     (app_marcel_reflex, {}),                   # 6
#     (app_symmetry, {}),                        # 7
#     # Multiplayer games
#     (app_light_chaser_1v1, {}),                # 8
#     (app_mirror_sequence, {}),                 # 9
#     (app_mirror_fight, {}),                    # 10
#     (app_tug_of_war, {}),                      # 11
#     # Utils
#     (app_buzzer, {}),                          # 12
#     (app_idle, {}),                            # 13
#     (None, {}),                                # 14
#     (None, {}),                                # 15
# ]

#(app_light_chaser, {'hardcore': True}      # 1
#(app_sequence, {'sound_level': 0}),        # 2

# Map game names to their functions and parameters
GAME_MAP = {
    "Light Chaser HC": (app_light_chaser, {'hardcore': True}),
    "Sequence": (app_sequence, {}),
    "Memory Sound": (app_memory_sound, {}),
    "Whack-a-mole": (app_whackamole, {}),
    "Marcel's Quest": (app_marcels_quest, {}),
    "Marcel's Frogs": (app_marcels_frogs, {}),
    "Marcel Reflex": (app_marcel_reflex, {}),
    "Symmetry": (app_symmetry, {}),
    "Light Chaser vs": (app_light_chaser_1v1, {}),
    "Mirror Sequence": (app_mirror_sequence, {}),
    "Mirror Fight": (app_mirror_fight, {}),
    "Tug of War": (app_tug_of_war, {}),
    "Buzzer": (app_buzzer, {}),
    "Idle": (app_idle, {})
}

def flash_start():
    arcade = get_arcadebuttons()
    arcade.on()
    time.sleep_ms(500)
    for color in COLORS:
        for _, led in arcade.items(color=color):
            led.off()
        time.sleep_ms(500)
    print(" >> Go Go Go! <<")

async def play_game(game_name):
    print(f"--> play_game: Attempting to start '{game_name}'")
    if game_name not in GAME_MAP:
        print(f"--> play_game: ERROR - Unknown game name: {game_name}")
        return

    func, kwargs = GAME_MAP[game_name]
    # Use repr(func) to see what the map holds initially (might show <generator> for async funcs here)
    print(f"--> play_game: Found func = {repr(func)}, kwargs = {kwargs}")

    flash_start() # Consider making this async if it uses time.sleep
    print(f"--> play_game: flash_start finished.")

    gc.collect()
    mem_before = gc.mem_free()
    print(f"--> play_game: Mem free before calling {game_name}: {mem_before}")

    res = None
    print(f"--> play_game: Calling {game_name}()...")
    try:
        res = func(**kwargs) # Call the function (e.g., app_idle() -> returns coro obj)
        # repr(res) will likely show <generator object ...> which is normal here
        print(f"--> play_game: Call returned. Type(res)={type(res)}, repr={repr(res)}")
    except Exception as e:
        print(f"--> play_game: EXCEPTION during function call ({game_name})!")
        sys.print_exception(e)
        return # Exit if the call itself failed

    # --- MODIFIED LOGIC ---
    # Based on testing, hasattr(res, '__await__') is unreliable on this platform.
    # We will now *always* try to await the result 'res'.
    # This assumes functions in GAME_MAP are intended to be awaitable if async.

    print(f"--> play_game: Assuming result is awaitable. >>> ENTERING AWAIT for {game_name}")
    try:
        await res # <<< ALWAYS AWAIT the result from the game function call
        print(f"--> play_game: <<< COMPLETED AWAIT for {game_name}")
    except TypeError as e:
        # This might happen if 'func' was *truly* synchronous and returned
        # something non-awaitable (like None or an int).
        # The await keyword itself handles None gracefully usually.
        print(f"--> play_game: CAUGHT TypeError during await (maybe '{game_name}' is sync?): {e}")
        # Decide how to handle - often just continuing is fine if sync funcs are simple.
    except Exception as e:
         print(f"--> play_game: EXCEPTION during await ({game_name})!")
         # Use sys.print_exception(e) for full traceback if needed
         print(f"                   Exception type: {type(e).__name__}, args: {e.args}")
         # Depending on the error, you might want to raise e here

    # --- End of modified logic ---

    gc.collect()
    mem_after = gc.mem_free()
    print(f"--> play_game: Mem free after await {game_name}: {mem_after} (Diff: {mem_before - mem_after})")
    print(f"--> play_game: Finished attempting execution for '{game_name}'")

async def flash_all():
    arcade = get_arcadebuttons()
    for _ in range(2):
        arcade.off()
        await asyncio.sleep_ms(200)
        arcade.on()
        await asyncio.sleep_ms(200)
    arcade.off()

# def oled_menu():
#     oled = SH1107_I2C()
#     oled.fill(0)
#     oled.text(' -- Menu --', 0, 0, 1)
#     oled.text('Select a Game', 10, 0, 1)
#     oled.show()
#     print(" > Main Menu")

# Define game categories
CATEGORIES = [
    GameCategory("Hard Solo", [
        "Light Chaser HC",
        "Sequence",
        "Memory Sound",
        "Whack-a-mole"
    ]),
    GameCategory("Easy Solo", [
        "Marcel's Quest",
        "Marcel's Frogs",
        "Marcel Reflex",
        "Symmetry"
    ]),
    GameCategory("Multiplayer", [
        "Light Chaser",
        "Mirror Sequence",
        "Mirror Fight",
        "Tug of War"
    ]),
    GameCategory("Utils", [
        "Buzzer",
        "Idle"
    ])
]

async def main_menu():
    print("Starting menu...")
    menu = GameMenu(CATEGORIES)
    menu.draw_menu()
    
    while True:
        selected_game = menu.handle_input()
        if selected_game:
            print(f"Selected game: {selected_game}")
            print(f"--> main_menu: Calling play_game, which is ({repr(play_game)})")
            try:
                await play_game(selected_game)
            except Exception as e:
                print(f"Error running game: {e}")
            finally:
                # Always return to menu after game ends
                menu.draw_menu()
                get_arcadebuttons().off()  # Ensure LEDs are off
        
        await asyncio.sleep_ms(50)  # Debounce delay

def cleanup():
    Buzzer().end_tone()
    get_arcadebuttons().off()
    get_oled().clear_screen(True)

if __name__ == '__main__':
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("Menu ended by user")
    finally:
        cleanup()
        # Clear screen on exit
        oled = get_oled()
        oled.clear_screen()
        oled.show()
