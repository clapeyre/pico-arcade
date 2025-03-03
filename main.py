import uasyncio as asyncio
from app_menu import app_menu, cleanup


def set_global_exception():
    def _handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)


async def main():
    set_global_exception()
    await app_menu()
try:
    asyncio.run(main())
finally:
    cleanup()
    print('Mainloop killed. Ctrl+D to restart')
