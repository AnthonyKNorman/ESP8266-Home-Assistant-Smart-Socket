from machine import Timer
from utime import sleep
import micropython

micropython.alloc_emergency_exception_buf(100)
 
class led_toggle(object):
    # set up a timer interrupt to toggle a led
    def __init__(self, led):
        self.led = led
        # this is used to remember the led state
        self._value = False
        # set up the timer
        self.timer = Timer(0)
        # start the timer
        # 2 second period
        # PERIODIC mode means that it repeats
        # uses the cb function when timer triggers
        self.timer.init(period=500, mode=Timer.PERIODIC, callback=self.cb)
         
    def cb(self, timer):
        # timer callback function
        # toggle the value
        self.led.value(not self.led.value())
        
    def deinit(self):
        self.timer.deinit()
 