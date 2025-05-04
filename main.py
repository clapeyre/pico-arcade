# main.py (Revised for uasyncio compatibility, using gather)
import asyncio
import time
import sys
from machine import Pin
from main_menu import main_menu, cleanup
from lib.oled import get_oled

# --- Configuration ---
INTERRUPT_BUTTON_PIN = 1
LONG_PRESS_DURATION_MS = 3000
# ---------------------

# --- Global variable to signal interruption ---
# Still useful for the watcher to stop itself cleanly
interrupt_signal = {'triggered': False}
# ---------------------------------------------

def set_global_exception():
    def _handle_exception(loop, context):
        print("--- Global Exception Handler Triggered ---")
        # Check if it's the cancellation we triggered
        if isinstance(context.get('exception'), asyncio.CancelledError):
            print("Exception was CancelledError (expected from interrupt).")
        else:
            # Print other exceptions
            sys.print_exception(context["exception"])
        print("----------------------------------------")
        # sys.exit() might still be too abrupt, consider commenting out
        # cleanup() should be called in the finally block anyway
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)

# --- MODIFIED: Accepts main_task_handle ---
async def watch_interrupt_button(pin_number, long_press_ms, main_task_handle):
    """Monitors a button for a long press and cancels the main task."""
    # Configure the button pin
    button = Pin(pin_number, Pin.IN, Pin.PULL_UP)
    press_start_time = None
    print(f"Interrupt watcher started on Pin {pin_number}. Hold for {long_press_ms / 1000}s to stop main task.")

    try:
        while not interrupt_signal['triggered']:
            if button.value() == 0: # Button pressed (assuming pull-up)
                if press_start_time is None:
                    press_start_time = time.ticks_ms()
                else:
                    if time.ticks_diff(time.ticks_ms(), press_start_time) >= long_press_ms:
                        print(f"Long press detected! Cancelling main task...")
                        interrupt_signal['triggered'] = True
                        # --- Directly cancel the main task ---
                        if main_task_handle:
                            main_task_handle.cancel()
                        # ------------------------------------
                        break # Exit watcher loop
            else: # Button released
                press_start_time = None

            # Yield control
            await asyncio.sleep_ms(50)

    except Exception as e:
        print("Error in interrupt watcher:")
        sys.print_exception(e)
        # If watcher crashes, maybe still try to cancel main task? Optional.
        # if main_task_handle and not main_task_handle.done():
        #    main_task_handle.cancel()
    finally:
        print("Interrupt watcher finished.")


async def main_wrapper():
    """Wraps the main application logic."""
    try:
        print("Starting main application (main_menu)...")
        await main_menu()
        print("main_menu finished normally.")
    except asyncio.CancelledError:
        print("main_menu task was cancelled (expected via interrupt).")
        # Allow cleanup in the main finally block
        # No need to re-raise, cancellation is handled by gather
    except Exception as e:
        print("Exception caught in main_wrapper:")
        sys.print_exception(e)
        # Let the exception propagate to be handled by gather/global handler
        raise

# --- MODIFIED: Uses asyncio.gather ---
async def run_concurrently():
    """Runs the main application and the interrupt watcher concurrently using gather."""
    set_global_exception()

    main_task = None
    interrupt_task = None
    results = []

    try:
        # Create main task first to get its handle
        main_task = asyncio.create_task(main_wrapper())
        # Create watcher task, passing the handle
        interrupt_task = asyncio.create_task(
            watch_interrupt_button(INTERRUPT_BUTTON_PIN, LONG_PRESS_DURATION_MS, main_task)
        )

        # Run both tasks concurrently and wait for BOTH to complete.
        # If the watcher cancels main_task, main_task will finish with
        # CancelledError, and the watcher will finish its loop.
        # gather will then return.
        print("Running tasks using asyncio.gather...")
        # `return_exceptions=True` prevents gather stopping on the first exception (like CancelledError)
        results = await asyncio.gather(main_task, interrupt_task, return_exceptions=True)
        print(f"asyncio.gather completed. Results/Exceptions: {results}")

    except Exception as e:
        # Catch exceptions not handled by gather's return_exceptions=True
        # or exceptions *during* the gather setup itself.
        print(f"Unexpected exception during run_concurrently: {type(e).__name__}")
        sys.print_exception(e)
        # Ensure tasks are cancelled if they are still running (unlikely here)
        if main_task and not main_task.done(): main_task.cancel()
        if interrupt_task and not interrupt_task.done(): interrupt_task.cancel()
        # Await cancellations briefly - might not be strictly necessary
        # await asyncio.sleep_ms(10) # Give cancellations time to process

    finally:
        print("run_concurrently finished.")
        # Check results for specific exceptions if needed
        if results:
             if isinstance(results[0], asyncio.CancelledError):
                 print("Confirmed main_task was cancelled.")
             elif isinstance(results[0], Exception):
                 print(f"Main task finished with exception: {results[0]}")

             if isinstance(results[1], Exception):
                 print(f"Interrupt watcher finished with exception: {results[1]}")


# --- Main Execution Block ---
try:
    # Optional: Add the initial delay here as well? Maybe not needed if button works.
    # print("Starting in 3s...")
    # time.sleep(3)

    print("Starting asyncio loop with concurrent tasks (using gather)...")
    asyncio.run(run_concurrently())

except Exception as e:
    print("Unhandled exception in top level:")
    sys.print_exception(e)

finally:
    # This cleanup runs regardless of how the asyncio loop exited
    print("Performing final cleanup...")
    cleanup()
    get_oled().draw_centered_text("DEBUG", 30)
    get_oled().show()
    print("Main script finished. REPL should be available.")


# Old method:
# import asyncio
# from main_menu import main_menu, cleanup
# 
# 
# def set_global_exception():
#     def _handle_exception(loop, context):
#         import sys
#         sys.print_exception(context["exception"])
#         sys.exit()
#     loop = asyncio.get_event_loop()
#     loop.set_exception_handler(_handle_exception)
# 
# 
# async def main():
#     set_global_exception()
#     await main_menu()
# try:
#     asyncio.run(main())
# finally:
#     cleanup()
#     print('Mainloop killed. Ctrl+D to restart')
# 