import asyncio
from drivers.buzzer import Buzzer


class Music:
    notes = "do do# ré ré# mi fa fa# sol sol# la la# si".split()
    freqs = [[130.8, 138.6, 146.8, 155.6, 164.8, 174.6, 185.0, 196.0, 207.7, 220.0, 233.1, 246.9],
             [261.6, 277.2, 293.7, 311.1, 329.6, 349.2, 370.0, 392.0, 415.3, 440.0, 466.2, 493.9],
             [523.3, 554.4, 587.3, 622.3, 659.3, 698.5, 740.0, 784.0, 830.6, 880.0, 932.3, 987.8]]
    
    def __init__(self, seq, level=1.0, tempo=200):
        self.seq = seq
        self.level = level
        self.tempo = tempo

    async def play(self):
        buzzer = Buzzer()
        for cmd in self.seq:
            if cmd is None:
                await asyncio.sleep_ms(time)
            else:
                time = int(cmd[1]) * self.tempo * 0.95
                freq = self.freqs[int(cmd[0])][self.notes.index(cmd[2:])]
                buzzer.start_tone(freq, level=self.level)
                await asyncio.sleep_ms(int(time))
                buzzer.end_tone()
                await asyncio.sleep_ms(int(time / 20))


SONGS = {
    "Lune": '11do 11do 11do 11ré 12mi 12ré 11do 11mi 11ré 11ré 11do'.split(),
    "MacDonald": '11sol 11sol 11sol 11ré 11mi 11mi 12ré 11si 11si 11la 11la 13sol'.split(),
    "Spider": '12do 11do 12do 11ré 13mi 12mi 11mi 12ré 11do 12ré 11mi 13do'.split(),
    "Twinkle": '11do 11do 11sol 11sol 11la 11la 12sol 11fa 11fa 11mi 11mi 11ré 11ré 12do'.split(),
    "Crocodiles": '11do 11la 11la 11la 11do 11la 11la 11la 11do 11la 11la 11la 12la# 12sol'.split(),
    "Jacques": '11do 11ré 11mi 11do 11do 11ré 11mi 11do 11mi 11fa 12sol 11mi 11fa 12sol'.split(),
    "Meunier": '02sol 14do 12mi 14do 11ré 11ré 12ré 11ré 11ré 12ré 11do 11ré 12mi 12do'.split(),
    "Bateaux": '11si 11si 11si 12sol 12si 21do 11si 12si 11la'.split()
}


def test():
    try:
        music = Music(SONGS["Meunier"])
        asyncio.run(music.play())
    finally:
        buzzer = Buzzer()
        buzzer.end_tone()