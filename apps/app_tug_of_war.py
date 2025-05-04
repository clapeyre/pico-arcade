import utime as time
import urandom as random
import asyncio
from drivers.buzzer import Buzzer
from lib.buttons import get_arcadebuttons, COLORS, get_controlpanel


async def buzz():
    buzzer = Buzzer()
    for tone in [220, 440, 880, 440, 220]:
        await buzzer.tone(int(tone), 60, 0.5)
        await asyncio.sleep_ms(30)


class TugOfWar:
    def __init__(self):
        arcade = get_arcadebuttons()
        self.leds = arcade.leds
        # Left player (blue/white)
        self.left_buttons = [i for i, c in enumerate(arcade.color)
                           if c in ("white", "blue")]
        # Right player (red/yellow)
        self.right_buttons = [i for i, c in enumerate(arcade.color)
                            if c in ("red", "yellow")]
        
        # The "rope" - 8 LEDs that can be pulled to either side
        self.rope_start = 4  # Position of the rope start
        
        # Player scores
        self.left_score = 0
        self.right_score = 0
        
        # Threshold for moving the rope
        self.threshold = 3
        
        # Start time for game duration tracking
        self.start_time = time.ticks_ms()
    
    @property
    def rope_positions(self):
        return list(range(self.rope_start, self.rope_start + 8))
    
    def update_rope_display(self):
        """Update the LED display based on rope position"""
        for i, led in enumerate(self.leds):
            if not led() and i in self.rope_positions:
                led.on()
            elif led() and i not in self.rope_positions:
                led.off()
    
    def update_score(self, left_pressed, right_pressed):
        """Update scores based on button presses"""
        self.left_score += left_pressed
        self.right_score += right_pressed
        
        # Calculate score difference and move rope if threshold reached
        score_diff = self.left_score - self.right_score
        
        # Move rope to the left (player 1 winning)
        if score_diff >= self.threshold:
            self.rope_start -= 1
            self.left_score = 0
            self.right_score = 0
        
        # Move rope to the right (player 2 winning)
        elif score_diff <= -self.threshold:
            self.rope_start += 1
            self.left_score = 0
            self.right_score = 0
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.rope_start == 0 or self.rope_start == 8
    
    def winner(self):
        """Return the winner: 'left', 'right', or None"""
        if self.rope_start == 0:
            return 'left'
        elif self.rope_start == 8:
            return 'right'
        return None
    
    def blink_winner(self):
        """Blink the winner's side LEDs"""
        if self.winner() == 'left':
            return [led.blink(300, 300, 3) for led in self.leds[:8]]
        else:
            return [led.blink(300, 300, 3) for led in self.leds[8:]]


async def app_tug_of_war(time_limit=60_000):
    print(' WELCOME to Tug of War! ')
    
    arcade = get_arcadebuttons()
    arcade.reset_flags()
    arcade.off()
    
    cp = get_controlpanel()
    cp.reset_flags()
    
    game = TugOfWar()
    
    # Rule reminder: show initial rope position
    game.update_rope_display()
    await asyncio.sleep(1)
    
    # Game loop
    while True:
        # Check for abort
        if 'select' in cp.pressed:
            arcade.off()
            await asyncio.sleep_ms(0)
            return
        
        # Check for time limit
        if time.ticks_diff(time.ticks_ms(), game.start_time) >= time_limit:
            break
        
        # Count button presses for each player
        left_pressed = 3 in arcade.pressed
        right_pressed = 12 in arcade.pressed
        
        # Update scores and rope position
        if left_pressed > 0 or right_pressed > 0:
            game.update_score(left_pressed, right_pressed)
            game.update_rope_display()
        
        # Check for game over
        if game.is_game_over():
            break
        
        arcade.reset_flags()
        await asyncio.sleep_ms(10)
    
    # Game over
    arcade.off()
    print('\n >>> GAME OVER <<<')
    
    # Show winner
    winner = game.winner()
    if winner:
        print(f"Winner: {winner} player!")
        tasks = [buzz()]
        tasks += game.blink_winner()
        await asyncio.gather(*tasks)
        win_leds = game.leds[:8] if winner == 'left' else game.leds[8:]
        for led in win_leds:
            led.on()
    else:
        print("Time's up! It's a draw!")
    
    await asyncio.sleep(1)
    
    # Wait for any button press to exit
    arcade.reset_flags()
    while True:
        if arcade.pressed:
            arcade.reset_flags()
            arcade.off()
            return
        await asyncio.sleep_ms(1)