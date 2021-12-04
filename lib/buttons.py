from machine import Pin, I2C, PWM
import uasyncio as asyncio
import utime as time
from primitives.pushbutton import Pushbutton
from lib import mcp23017

def button_init(nb=-1):
    i2c = I2C(0, scl=Pin(21), sda=Pin(20))
    #print(i2c.scan(), [hex(i) for i in i2c.scan()])
    mcp = mcp23017.MCP23017(i2c, 0x27)
    buttons = [mcp[pin] for pin in range(16)][::2]
    leds = [mcp[pin] for pin in range(16)][1::2]
    #buttons = [mcp[pin] for pin in range(4)]
    #leds = [mcp[15 - pin] for pin in range(4)]
    #buttons = [mcp[pin] for pin in range(6, 10)]
    #leds = [mcp[pin] for pin in range(10, 14)]
    for button in buttons:
        button.input(pull=1)
    if nb > 0:
        buttons = buttons[:nb]
        leds = leds[:nb]
    return buttons, leds


class LED:
    def __init__(self, pin):
        self.pin = pin

    def output(self, *args, **kwargs):
        return self.pin.output(*args, **kwargs)

    def value(self, *args, **kwargs):
        return self.pin.value(*args, **kwargs)

    def on(self):
        self.output(val=1)

    def off(self):
        self.output(val=0)

    def toggle(self):
        self.output(val=int(not self.value()))

    async def blink(self, up, down, times):
        for _ in range(times):
            self.on()
            await asyncio.sleep_ms(up)
            self.off()
            await asyncio.sleep_ms(down)

class _ButtonGroup:
    def __getitem__(self, key):
        return self.pressed_flag[key]
    
    def __setitem__(self, key, val):
        self.pressed_flag[key] = val
    
    def _press(self, key):
        self.pressed_flag[key] = True

    def reset_flags(self):
        for key in self.pressed:
            self[key] = False

    async def run(self, loop_delay=20):
        await asyncio.sleep(loop_delay)  # Dummy..?
    

class _ArcadeButtons(_ButtonGroup):
    def __init__(self, pressed_flag=False):
        self._i2c = I2C(0, scl=Pin(21), sda=Pin(20))
        self._mcp_yr = mcp23017.MCP23017(self._i2c, 0x26)
        self._mcp_wb = mcp23017.MCP23017(self._i2c, 0x27)
        self.buttons = (
            [Pushbutton(self._mcp_wb[pin], sense=1) for pin in range(16)][::2] +
            [Pushbutton(self._mcp_yr[pin], sense=1) for pin in range(16)][::2])
        for but in self.buttons:
            but.pin.input(pull=1)
        self.leds = (
            [LED(self._mcp_wb[pin]) for pin in range(16)][1::2] +
            [LED(self._mcp_yr[pin]) for pin in range(16)][1::2])
        self.pressed_flag = None
        if pressed_flag:
            self.pressed_flag_behaviour()

    @property
    def pressed(self):
        return [idx for idx, flag in enumerate(self.pressed_flag) if flag]
    
    def pressed_flag_behaviour(self):
        self.pressed_flag = [False,] * len(self.buttons)
        for i, but in enumerate(self.buttons):
            but.press_func(self._press, (i,))
    
    def off(self):
        [led.off() for led in self.leds]
    
    def on(self):
        [led.on() for led in self.leds]
    

class _ControlPanel(_ButtonGroup):
    def __init__(self, pressed_flag=False):
        pins = [3, 6, 7, 8, 9]
        self.names = "up select right left down".split()
        self.buttons = [self.up, self.select, self.right, self.left, self.down] = [
            Pushbutton(Pin(pin, Pin.IN, Pin.PULL_UP))
            for pin in pins]
        self.pressed_flag = None
        if pressed_flag:
            self.pressed_flag_behaviour()

    @property
    def pressed(self):
        return [key for key, flag in self.pressed_flag.items() if flag]
    
    def pressed_flag_behaviour(self):
        self.pressed_flag = {key: False for key in self.names}
        for i, but in enumerate(self.buttons):
            but.press_func(self._press, (self.names[i],))
    

_ARCADEBUTTONS = None
_CONTROLPANEL = None


def get_arcadebuttons(pressed_flag=False):
    global _ARCADEBUTTONS
    if _ARCADEBUTTONS is None:
        _ARCADEBUTTONS = _ArcadeButtons()
    if pressed_flag:
        _ARCADEBUTTONS.pressed_flag_behaviour()
    return _ARCADEBUTTONS


def get_controlpanel(pressed_flag=False):
    global _CONTROLPANEL
    if _CONTROLPANEL is None:
        _CONTROLPANEL = _ControlPanel()
    if pressed_flag:
        _CONTROLPANEL.pressed_flag_behaviour()
    return _CONTROLPANEL


def on(led):
    led.output(val=1)


def off(led):
    led.output(val=0)


def toggle(led):
    led.output(val=int(not led.value()))


def blink(led, up, down, times):
    for _ in times:
        led.output(val=1)
        time.sleep(up)
        led.output(val=0)
        time.sleep(down)




async def _test():
    arcade = get_arcadebuttons(pressed_flag=True)
    arcade.off()
    asyncio.create_task(arcade.run(5))
    cp = get_controlpanel(pressed_flag=True)
    asyncio.create_task(cp.run(5))

    #async def _debug():
    #    arcade = get_arcadebuttons(pressed_flag=True)
    #    while True:
    #        print([led.value() for led in arcade.leds])
    #        await asyncio.sleep_ms(1000)
    #asyncio.create_task(_debug())

    print("  >>>  Please test any button(s)  <<")
    while True:
        if arcade.pressed:
            plural = 's' if len(arcade.pressed) > 1 else ''
            print(f"Button{plural} {', '.join([str(i) for i in arcade.pressed])} pressed!")
            for idx in arcade.pressed:
                arcade.leds[idx].toggle()
                arcade[idx] = False

        if cp.pressed:
            plural = 's' if len(cp.pressed) > 1 else ''
            print(f"Button{plural} {', '.join(cp.pressed)} pressed!")
            for key in cp.pressed:
                cp[key] = False
        await asyncio.sleep_ms(10)

if __name__ == '__main__':
    asyncio.run(_test())
