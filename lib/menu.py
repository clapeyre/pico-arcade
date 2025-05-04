from lib.oled import get_oled
from lib.buttons import get_controlpanel

class GameCategory:
    def __init__(self, name, games):
        self.name = name
        self.games = games

class GameMenu:
    def __init__(self, categories):
        self.oled = get_oled()
        self.cp = get_controlpanel()
        self.categories = categories
        self.in_category = False
        self.current_category = 0
        self.current_game = 0
        self.scroll_offset = 0
        
    def draw_menu(self):
        """Draw the current menu state on the screen"""
        self.oled.clear_screen()
        
        # Draw title
        if self.in_category:
            title = self.categories[self.current_category].name
        else:
            title = "Select Category"
        self.oled.draw_text(title, 0, 0)
        
        # Draw separator line
        self.oled.draw_line(0, 10, 128, 10)
        
        # Draw items
        items = (self.categories[self.current_category].games if self.in_category 
                else [cat.name for cat in self.categories])
        current_idx = self.current_game if self.in_category else self.current_category
        
        for i in range(min(self.oled.get_items_per_screen(), len(items))):
            idx = i + self.scroll_offset
            if idx >= len(items):
                break
                
            y = 15 + (i * 12)
            text = items[idx]
            if idx == current_idx:
                # Highlight current selection
                self.oled.draw_text(text, 4, y, invert=True)
            else:
                self.oled.draw_text(text, 4, y)
        
        self.oled.show()
    
    def select(self):
        """Handle selection of a category or game"""
        if not self.in_category:
            self.in_category = True
            self.current_game = 0
            self.scroll_offset = 0
        else:
            category = self.categories[self.current_category]
            game_idx = self.current_game
            return category.games[game_idx]
        self.draw_menu()
        return None
    
    def back(self):
        """Go back to category selection"""
        if self.in_category:
            self.in_category = False
            self.draw_menu()
            return True
        return False
    
    def move(self, direction):
        """Move selection up or down
        
        Args:
            direction (int): -1 for up, 1 for down
        """
        if self.in_category:
            games = self.categories[self.current_category].games
            self.current_game = (self.current_game + direction) % len(games)
            # Adjust scroll if needed
            if self.current_game < self.scroll_offset:
                self.scroll_offset = self.current_game
            elif self.current_game >= self.scroll_offset + self.oled.get_items_per_screen():
                self.scroll_offset = self.current_game - self.oled.get_items_per_screen() + 1
        else:
            self.current_category = (self.current_category + direction) % len(self.categories)
            if self.current_category < self.scroll_offset:
                self.scroll_offset = self.current_category
            elif self.current_category >= self.scroll_offset + self.oled.get_items_per_screen():
                self.scroll_offset = self.current_category - self.oled.get_items_per_screen() + 1
        
        self.draw_menu()
    
    def handle_input(self):
        """Check for button presses and handle them
        
        Returns:
            str or None: Selected game name if a game was selected, None otherwise
        """
        if 'up' in self.cp.pressed:
            self.move(-1)
        elif 'down' in self.cp.pressed:
            self.move(1)
        elif 'select' in self.cp.pressed:
            result = self.select()
            self.cp.reset_flags()
            return result
        elif 'left' in self.cp.pressed:
            self.back()

        self.cp.reset_flags()
        
        return None

if __name__ == '__main__':
    import time
    import asyncio

    AUTOMATIC = False
    INTERACTIVE = True
    
    # Create test categories
    test_categories = [
        GameCategory("Test Category 1", [
            "Game 1.1",
            "Game 1.2",
            "Game 1.3",
            "Game 1.4",
            "Game 1.5"  # Test scrolling
        ]),
        GameCategory("Test Category 2", [
            "Game 2.1",
            "Game 2.2"
        ]),
        GameCategory("Test Category 3", [
            "Game 3.1",
            "Game 3.2",
            "Game 3.3"
        ])
    ]
    
    menu = GameMenu(test_categories)
    menu.draw_menu()
    print("Showing initial menu...")
    time.sleep(1)
    
    if AUTOMATIC:
        # Test moving through categories
        print("Moving down through categories...")
        for _ in range(len(test_categories)):
            menu.move(1)
            time.sleep(0.5)
        
        # Test selecting a category
        print("Selecting first category...")
        menu.select()
        time.sleep(1)
        
        # Test moving through games
        print("Moving down through games...")
        for _ in range(5):  # Test scrolling
            menu.move(1)
            time.sleep(0.3)
        
        # Test moving up
        print("Moving up through games...")
        for _ in range(5):
            menu.move(-1)
            time.sleep(0.3)
        
        # Test going back to categories
        print("Going back to categories...")
        menu.back()
        time.sleep(1)
    
    if INTERACTIVE: 
        # Interactive mode
        print("\nEntering interactive mode...")
        print("Use the buttons to navigate the menu")
        print("Press Ctrl+C to exit")
        
        async def interactive_mode():
            while True:
                selected_game = menu.handle_input()
                if selected_game:
                    print(f"Selected game: {selected_game}")
                    # In a real game, you would launch the game here
                    # For testing, we just go back to the menu
                    menu.back()
                await asyncio.sleep_ms(50)
        
        try:
            asyncio.run(interactive_mode())
        except KeyboardInterrupt:
            print("\nTest ended by user")
        finally:
            # Clear screen at end
            menu.oled.clear_screen()
            menu.oled.show() 