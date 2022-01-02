from machine import Pin, I2C


I2C0 = I2C(0, scl=Pin(21), sda=Pin(20))
