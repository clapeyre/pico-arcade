from machine import Pin, PWM
import time

class Buzzer(PWM):
    def tone(self, frequency, duration, level=0.2):
        self.freq(frequency)
        self.duty_u16(int(0.95 * level * 65535))
        time.sleep_ms(duration)
        self.duty_u16(0)

    def start_tone(self, frequency, level=0.2):
        self.freq(frequency)
        self.duty_u16(int(0.95 * level * 65535))

    def end_tone(self):
        self.duty_u16(0)

buzzer = Buzzer(Pin(14))

if __name__ == '__main__':
    buzzer.tone(440, 250, 1)
    #buzzer.tone(440, 250, 0.5)
    #buzzer.tone(440, 250, 0.1)
    time.sleep(0.5)
    buzzer.tone(int(440*1.414), 250, 0.01)
    time.sleep(0.5)
    buzzer.tone(440*2, 250, 0.005)