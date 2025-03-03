import uasyncio as asyncio
from lib.buttons import get_arcadebuttons, get_controlpanel
from lib.score import (
    pharmacy_blink_circle, pharmacy_blink_spiral,
    pharmacy_blink_cross)


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

    cp = get_controlpanel()
    cp.reset_flags()

    ongoing = None
    seq = sequence()
    while True:
        if 'select' in cp.pressed:  # Abort
            ongoing.cancel()
            return
        
        if ongoing is None or ongoing.done():
            task = next(seq)
            ongoing = asyncio.create_task(task)
        
        await asyncio.sleep_ms(0)