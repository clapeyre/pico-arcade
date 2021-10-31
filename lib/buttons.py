from machine import Pin, I2C, PWM
import time
import mcp23017

def button_init():
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
    return buttons, leds

def on(led):
    led.output(val=1)

def off(led):
    led.output(val=0)

def blink(led, up, down, times):
    for _ in times:
        led.output(val=1)
        time.sleep(up)
        led.output(val=0)
        time.sleep(down)

if __name__ == '__main__':
    buttons, leds = button_init()
    while True:
        for button, led in zip(buttons, leds):
            if button.value() == 0:
                print(f"Bouton presse! led a {led.value()}")
                led.output(val=int(not led.value()))
                print([led.value() for led in leds])
                print([button.value() for button in buttons])
                time.sleep(0.1)