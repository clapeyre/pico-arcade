import asyncio
from lib.buttons import get_arcadebuttons, get_controlpanel



async def pharmacy_blink_circle(inwards=False):
    circles = [
        [5, 6, 9, 10],
        [i for i in range(16) if i not in [5, 6, 9, 10]]]
    arcade = get_arcadebuttons()
    arcade.off()

    sequence = [] + circles
    if inwards:
        sequence = sequence[::-1]
    for seq in sequence:
        for idx in seq:
            arcade.leds[idx].on()
        await asyncio.sleep_ms(200)
        arcade.off()


async def pharmacy_blink_spiral(inwards=False):
    sequence = [0, 4, 8, 12, 13, 14, 15, 11, 7, 3, 2, 1, 5, 9, 10, 6]
    arcade = get_arcadebuttons()
    arcade.off()

    direction = -1 if inwards else 1
    for idx in sequence[::direction]:
        arcade.leds[idx].on()
        await asyncio.sleep_ms(50)
    for idx in sequence[::direction]:
        arcade.leds[idx].off()
        await asyncio.sleep_ms(50)


async def pharmacy_blink_cross(clockwise=True):
    center = [5, 6, 9, 10]
    branches = [
        [0, 12, 15, 3],
        [4, 13, 11, 2],
        [8, 14, 7, 1],
    ]
    arcade = get_arcadebuttons()
    for idx in range(16):
        if idx in center:
            arcade.leds[idx].on()
        else:
            arcade.leds[idx].off()

    direction = 1 if clockwise else -1
    for branch in branches[::direction]:
        for idx in branch:
            arcade.leds[idx].on()
        await asyncio.sleep_ms(150)
        for idx in branch:
            arcade.leds[idx].off()

def sequence():
    seq = ([
        (pharmacy_blink_circle, {}, 10),
        ] +
        [(pharmacy_blink_spiral, {}, 1),
         (pharmacy_blink_spiral, {'inwards': True}, 1)] * 2 +
        [(pharmacy_blink_cross, {}, 5),
         (pharmacy_blink_cross, {'clockwise': False}, 5)
        ])
    counter = 0
    while True:
        for task, kwargs, repeat in seq:
            for _ in range(repeat):
                yield task(**kwargs)


async def app_idle():
    print("Starting idle mode...")
    cp = get_controlpanel()
    cp.reset_flags()

    seq = sequence()
    try:
        while True:
            if 'select' in cp.pressed:  # Abort
                return
            
            # Get the next animation task and await it
            task = next(seq)
            await task
            
            await asyncio.sleep_ms(10)
    except Exception as e:
        print(f"Error in idle mode: {e}")
    finally:
        get_arcadebuttons().off()