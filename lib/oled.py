from machine import Pin
from drivers.oled_1i3_sh1107 import OLED_1inch3
from lib.buttons import get_controlpanel

_OLED = None

def get_oled():
    global _OLED
    if _OLED is None:
        _OLED = _Oled()
    return _OLED

class _Oled:
    def __init__(self):
        self.oled = OLED_1inch3()
        self.width = 128
        self.height = 64
        self.font_width = 8
        self.font_height = 8
        
        # Button state tracking
        self.last_up = 1
        self.last_down = 1
        self.last_select = 1
        self.last_back = 1
        
    def clear_screen(self, show=False):
        """Clear the entire screen"""
        self.oled.fill(0x0000)
        if show:
            self.show()
        
    def draw_text(self, text, x, y, invert=False):
        """Draw text on the screen at specified coordinates"""
        if invert:
            self.oled.fill_rect(x, y, len(text) * self.font_width, self.font_height, 0xFFFF)
            self.oled.text(text, x, y, 0x0000)
        else:
            self.oled.text(text, x, y, 0xFFFF)
    
    def draw_centered_text(self, text, y, invert=False):
        """Draw text centered horizontally on the screen"""
        x = (self.width - len(text) * self.font_width) // 2
        self.draw_text(text, x, y, invert)
    
    def draw_progress_bar(self, x, y, width, height, progress, color=0xFFFF):
        """Draw a progress bar
        
        Args:
            x, y: Top-left corner
            width, height: Dimensions
            progress: Value between 0 and 1
            color: Color of the bar
        """
        self.oled.rect(x, y, width, height, color)
        if progress > 0:
            fill_width = int(width * progress)
            self.oled.fill_rect(x, y, fill_width, height, color)
    
    def draw_score(self, score, x=0, y=0):
        """Draw a score display"""
        self.draw_text(f"Score: {score}", x, y)
    
    def draw_timer(self, seconds, x=0, y=0):
        """Draw a timer display"""
        mins = seconds // 60
        secs = seconds % 60
        self.draw_text(f"Time: {mins:02d}:{secs:02d}", x, y)
    
    def draw_game_over(self, score=None):
        """Draw a game over screen"""
        self.clear_screen()
        self.draw_centered_text("GAME OVER", 20)
        if score is not None:
            self.draw_centered_text(f"Score: {score}", 35)
        self.draw_centered_text("Press to restart", 50)
        self.show()
    
    def draw_pause_screen(self):
        """Draw a pause screen"""
        self.clear_screen()
        self.draw_centered_text("PAUSED", 20)
        self.draw_centered_text("Press to resume", 35)
        self.show()
    
    def show(self):
        """Update the display with the current buffer"""
        self.oled.show()
    
    def draw_line(self, x1, y1, x2, y2, color=0xFFFF):
        """Draw a line on the screen
        
        Args:
            x1 (int): Starting X coordinate
            y1 (int): Starting Y coordinate
            x2 (int): Ending X coordinate
            y2 (int): Ending Y coordinate
            color (int): Color of the line (default: white)
        """
        self.oled.line(x1, y1, x2, y2, color)
    
    def draw_rect(self, x, y, width, height, color=0xFFFF, fill=False):
        """Draw a rectangle on the screen
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Width of rectangle
            height (int): Height of rectangle
            color (int): Color of the rectangle (default: white)
            fill (bool): If True, fill the rectangle
        """
        if fill:
            self.oled.fill_rect(x, y, width, height, color)
        else:
            self.oled.rect(x, y, width, height, color)
    
    def get_items_per_screen(self):
        """Get the number of items that can fit on one screen"""
        # Each item takes 12 pixels (8 for text + 4 spacing)
        # First 10 pixels are for title and separator
        available_height = self.height - 10
        return available_height // 12
    
    def check_buttons(self):
        """Check button states and return any pressed buttons
        
        Returns:
            dict: Dictionary with button states:
                - 'up': True if up button was pressed
                - 'down': True if down button was pressed
                - 'select': True if select button was pressed
                - 'back': True if back button was pressed
        """
        control_panel = get_controlpanel()
        up_val = control_panel.up.value()
        down_val = control_panel.down.value()
        select_val = control_panel.select.value()
        back_val = control_panel.left.value()
        
        result = {
            'up': up_val == 0 and self.last_up == 1,
            'down': down_val == 0 and self.last_down == 1,
            'select': select_val == 0 and self.last_select == 1,
            'back': back_val == 0 and self.last_back == 1
        }
        
        self.last_up = up_val
        self.last_down = down_val
        self.last_select = select_val
        self.last_back = back_val
        
        return result

if __name__ == '__main__':
    import time
    
    oled = get_oled()
    
    # Test basic text
    oled.clear_screen()
    oled.draw_text("Normal text", 0, 0)
    oled.draw_text("Inverted text", 0, 10, invert=True)
    oled.draw_centered_text("Centered!", 20)
    oled.show()
    time.sleep(2)
    
    # Test progress bar
    oled.clear_screen()
    oled.draw_centered_text("Progress Bar", 0)
    for i in range(11):
        progress = i / 10
        oled.draw_progress_bar(10, 20, 108, 10, progress)
        oled.show()
        time.sleep(0.2)
    time.sleep(1)
    
    # Test score and timer
    oled.clear_screen()
    oled.draw_score(1234, 0, 0)
    oled.draw_timer(125, 0, 10)  # 2:05
    oled.show()
    time.sleep(2)
    
    # Test game over screen
    oled.draw_game_over(score=1234)
    time.sleep(2)
    
    # Test pause screen
    oled.draw_pause_screen()
    time.sleep(2)
    
    # Clear screen at end
    oled.clear_screen()
    oled.show() 