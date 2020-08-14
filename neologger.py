from neopixel_hat import Pixels, PixelError, RED, GREEN, BLUE, WHITE, YELLOW, OFF
from multiprocessing import Process
import time

class NeoLogger:
    class __NeoLogger:
        def __init__(self):
            self.pixels = Pixels()
        def debug(self, msg):
            Process(target=self._debug, args=(msg,)).start() # do this to not block, the process is finite so it will terminate and get garbage collected
        def info(self, msg):
            Process(target=self._info, args=(msg,)).start()
        def warning(self, msg):
            Process(target=self._warning, args=(msg,)).start()
        def error(self, msg):
            Process(target=self._error, args=(msg,)).start()
        def _debug(self,msg):
            self.pixels.set_pixel(1,WHITE)
            print(f"DEBUG: {msg}")
            time.sleep(0.25)
            self.pixels.set_pixel(1,OFF)
        def _info(self, msg):
            self.pixels.set_pixel(1,BLUE)
            print(f"INFO: {msg}")
            time.sleep(0.25)
            self.pixels.set_pixel(1,OFF)
        def _warning(self, msg): 
            self.pixels.set_pixel(1,ORANGE)
            print(f"WARNING: {msg}")
            time.sleep(0.25)
            self.pixels.set_pixel(1,OFF)
        def _error(self, msg):
            self.pixels.set_pixel(1,RED)
            print(f"ERROR: {msg}")
            time.sleep(0.25)
            self.pixels.set_pixel(1,OFF)
    instance = None
    def __init__(self):
        if not NeoLogger.instance:
            NeoLogger.instance = NeoLogger.__NeoLogger()
    def __getattr__(self, name):
        return getattr(self.instance, name)
