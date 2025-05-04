from machine import Pin, I2C
import asyncio
import utime as time
from primitives.pushbutton import Pushbutton
from drivers.mcp23017 import MCP23017
from drivers.i2c import I2C0

DEBUG = True


def button_init(nb=-1):
    i2c = I2C(0, scl=Pin(21), sda=Pin(20))
    #print(i2c.scan(), [hex(i) for i in i2c.scan()])
    mcp_yr = MCP23017(i2c, 0x26)
    mcp_wb = MCP23017(i2c, 0x27)
    buttons = [mcp_wb[pin] for pin in range(16)][::2]
    buttons += [mcp_yr[pin] for pin in range(16)][::2]
    buttons[8:] = buttons[12:] + buttons[8:12]
    leds = [mcp_wb[pin] for pin in range(16)][1::2]
    leds += [mcp_yr[pin] for pin in range(16)][1::2]
    leds[8:] = leds[12:] + leds[8:12]
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


def array_to_index(x, y):
    """
    Relate (x, y) pos to the 0 - 15 buttons
         ..  
       0 1 2 3 y
     0 o o o o
     1 o o o o
     2 o o o o
     3 o o o o
     x 
    """
    return y * 4 + x


def index_to_array(idx):
    """Simple inverse of array_to_index"""
    return idx % 4, idx // 4


# Colors
COLORS = ("white", "blue", "red", "yellow")

class LED:
    def __init__(self, pin):
        self.pin = pin
    
    def __call__(self):
        return self.value()

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
        if DEBUG:
            print("PRESSED", key)
        self.pressed_flag[key] = True
    
    def _release(self, key):
        if DEBUG:
            print("RELEASED", key)
        self.released_flag[key] = True

    def reset_flags(self):
        self.reset_pressed()
        self.reset_released()


class _ArcadeButtons(_ButtonGroup):
    def __init__(self):
        self._i2c = I2C0
        self._mcp_yr = MCP23017(self._i2c, 0x26)
        self._mcp_wb = MCP23017(self._i2c, 0x27)

        self.buttons = (
            [Pushbutton(self._mcp_wb[pin], sense=1) for pin in range(16)][::2] +
            [Pushbutton(self._mcp_yr[pin], sense=1) for pin in range(16)][::2])
        self.buttons[8:] = self.buttons[12:] + self.buttons[8:12]
        self.size = len(self.buttons)
        self.reset_flags()
        for i, but in enumerate(self.buttons):
            but.pin.input(pull=1)
            but.press_func(self._press, (i,))
            but.release_func(self._release, (i,))

        self.leds = (
            [LED(self._mcp_wb[pin]) for pin in range(16)][1::2] +
            [LED(self._mcp_yr[pin]) for pin in range(16)][1::2])
        self.leds[8:] = self.leds[12:] + self.leds[8:12]

        self.color = [j for i in range(4) for j in [COLORS[i]] * 4]
        
    def __str__(self):
        """ Nice view of board
        
        O for on, . for off:

        O O . .
        . . . O
        . . O O
        . O . O
        """
        mapping = {True: ' O', False: ' .'}
        out = ""
        for x in range(4):
            for y in range(4):
                out += mapping[self.leds[array_to_index(x, y)]()]
            out += '\n'
        return out

    @property
    def pressed(self):
        return [idx for idx, flag in enumerate(self.pressed_flag) if flag]
    
    @property
    def released(self):
        return [idx for idx, flag in enumerate(self.released_flag) if flag]

    def reset_pressed(self):
        self.pressed_flag = [False,] * self.size
    
    def reset_released(self):
        self.released_flag = [False,] * self.size

    def items(self, color=None):
        if color is None:
            return zip(self.buttons, self.leds)
        else:
            indices = [i for i, c in enumerate(self.color) if c == color]
            return zip([b for i, b in enumerate(self.buttons) if i in indices],
                       [l for i, l in enumerate(self.leds) if i in indices])
    
    def off(self):
        [led.off() for led in self.leds]
    
    def on(self):
        [led.on() for led in self.leds]
    

class _ControlPanel(_ButtonGroup):
    def __init__(self):
        pins = [0, 1, 2, 3, 4]
        self.names = "up select right down left".split()
        self.buttons = [self.up, self.select, self.right, self.down, self.left] = [
            Pushbutton(Pin(pin, Pin.IN, Pin.PULL_UP))
            for pin in pins]
        self.reset_flags()
        for i, but in enumerate(self.buttons):
            but.press_func(self._press, (self.names[i],))
            but.release_func(self._release, (self.names[i],))
    
    @property
    def pressed(self):
        return [key for key, flag in self.pressed_flag.items() if flag]
    
    @property
    def released(self):
        return [key for key, flag in self.released_flag.items() if flag]
    
    def reset_pressed(self):
        self.pressed_flag = {key: False for key in self.names}
    
    def reset_released(self):
        self.released_flag = {key: False for key in self.names}



_ARCADEBUTTONS = None
_CONTROLPANEL = None


def get_arcadebuttons():
    global _ARCADEBUTTONS
    if _ARCADEBUTTONS is None:
        _ARCADEBUTTONS = _ArcadeButtons()
    return _ARCADEBUTTONS


def get_controlpanel():
    global _CONTROLPANEL
    if _CONTROLPANEL is None:
        _CONTROLPANEL = _ControlPanel()
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
    arcade = get_arcadebuttons()
    arcade.off()
    cp = get_controlpanel()
    cp.reset_flags()

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
