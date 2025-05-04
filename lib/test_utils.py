import utime as time
import asyncio
from lib.buttons import get_arcadebuttons

async def run_app_with_cleanup(app_func, *args, **kwargs):
    """
    Run an app function with proper cleanup and safeguards.
    
    Args:
        app_func: The async app function to run
        *args: Positional arguments to pass to the app function
        **kwargs: Keyword arguments to pass to the app function
    """
    try:
        await app_func(*args, **kwargs)
    except Exception as e:
        print(f'Error running app: {e}')
    finally:
        # Ensure cleanup happens even if interrupted
        arcade = get_arcadebuttons()
        arcade.off()
        arcade.reset_flags()

async def test_app_loop(app_func, *args, **kwargs):
    """
    Run an app in a test loop with proper cleanup and safeguards.
    Includes timeout for button presses and graceful exit handling.
    
    Args:
        app_func: The async app function to run
        *args: Positional arguments to pass to the app function
        **kwargs: Keyword arguments to pass to the app function
    """
    try:
        while True:
            # Run the app
            await run_app_with_cleanup(app_func, *args, **kwargs)
            print('App completed, waiting for button press or timeout...')
            
            # Setup arcade buttons
            arcade = get_arcadebuttons()
            arcade.reset_flags()
            
            # Wait for button press with timeout
            start_time = time.ticks_ms()
            while not arcade.pressed:
                if time.ticks_diff(time.ticks_ms(), start_time) > 5000:  # 5 second timeout
                    print('Timeout reached, restarting app...')
                    break
                await asyncio.sleep_ms(10)
            
            # Cleanup
            arcade.off()
            arcade.reset_flags()
            
    except KeyboardInterrupt:
        print('Test interrupted by user')
    finally:
        # Ensure cleanup happens even if interrupted
        arcade = get_arcadebuttons()
        arcade.off()
        arcade.reset_flags()
        print('Test cleanup completed')

def run_test(app_func, *args, **kwargs):
    """
    Main entry point for running app tests.
    Handles the asyncio event loop and final cleanup.
    
    Args:
        app_func: The async app function to run
        *args: Positional arguments to pass to the app function
        **kwargs: Keyword arguments to pass to the app function
    """
    try:
        asyncio.run(test_app_loop(app_func, *args, **kwargs))
    except KeyboardInterrupt:
        print('Test terminated by user')
    finally:
        # Final cleanup
        arcade = get_arcadebuttons()
        arcade.off()
        arcade.reset_flags()
        print('Final cleanup completed') 