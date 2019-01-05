"""
configuration.yaml looks like this
light:
  - platform: mqtt
    name: "SOCKET1"
    state_topic: "home/socket1/status"
    command_topic: "home/socket1/set"
    
 From first start up the device will present an access point named something like ESP123XY
 Connect your computer to the access point using password 'uPy12345'
 Open a browser and browse to http://192.168.4.1 
 You will see a web form
 Set the name or IP address of your MQTT server
 Give your device a unique nameEnter the SSID and Password for your wifi network
 Sumbit
 
 That's it!

"""
from umqtt.simple import MQTTClient
from machine import Pin, reset
from utime import sleep, ticks_ms, ticks_diff
import ujson, os, wificonf

# set topic basestring
# e.g. set to b'home' gives topics of
# b'home/{socket_name}/status' and b'home/{socket_name}/status'
topic_base = b'home'

#### DO NOT CHANGE ANYTHING AFTER HERE ####
conf_file = "creds.txt"

def send_status():
    """ send the on / off to home assistant """
    global state
    msg = {'state':state}
    msg = ujson.dumps(msg)
    msg = msg.encode()
    c.publish(state_topic, msg)
    print('sent', msg)

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    global state
    print((topic, msg))
    msg = ujson.loads(msg)
    state = msg['state']
    print ('received state', state)
    
    if 'state' in msg:
        state = msg['state']
        if state == "ON":                       # setting the status
            relay.on()                          # set the brightness to the stored value
            red_led.off()
            blue_led.on()
        elif state == "OFF":                    # 'OFF' received
            relay.off()                         # set the brightness to the stored value
            red_led.on()
            blue_led.off()
    send_status()


# pin 13 button in
# pon 0 red led
# pin 2 blue led
# pin 4 on-board led
# pin 15 relay
button      = Pin(13, Pin.IN, Pin.PULL_UP)      # button on outside of plug
red_led     = Pin(0, Pin.OUT)                   # red led on front
blue_led    = Pin(2, Pin.OUT)                   # bue led on front
onboard_led = Pin(4, Pin.OUT)                   # blue led on ESP8266 board(not visible)
relay       = Pin(15, Pin.OUT)                  # relay


w = wificonf.wificonf(cFile = conf_file)        # initialises the config file if it doesn't exist

start_ticks = 0                                 # used as the button press timer
button_flag = False                             # true if the button has been pressed

# handler for button interrupt
def callback(p):
    global start_ticks, button_flag
    print('pin change', p, p.value())
    
    # button up event
    if (p.value()):
        time_pressed = ticks_diff(ticks_ms(), start_ticks)
        print (time_pressed)
        if time_pressed > 5000:
            button_flag = True
    # button down event        
    else:
        start_ticks = ticks_ms()

# set up the interrupt action
button.irq(trigger=Pin.IRQ_FALLING, handler=callback)

while not w.wifi():                             # start the wifi
    # if the button is pressed continuously for more tha 5 seconds
    # then go into set up mode
    if button_flag:
        button_flag = False
        w.get_params()
    print('*',end='')
    sleep(.5)

print (w.c)

state_topic   = topic_base + b'/'+ w.c['name'].encode() + b'/status'
command_topic = topic_base + b'/'+ w.c['name'].encode() + b'/set'
print (state_topic, command_topic)


mqtt = 0
while not mqtt:
    # connect to mqtt
    print('mqtt name: {} mqtt address {}'.format(w.c['name'], w.c['mqtt']))
    c = MQTTClient(w.c['name'], w.c['mqtt'])
    c.set_callback(sub_cb)                      # set the callback function
    try:
        c.connect()                             # get connected
        mqtt = 1
    except Exception as e:
        print('MQTT connection failed', e)
        w.get_params()                          # enable the web interface if the wifi doesn't connect
        reset()
        
        
c.subscribe(command_topic)                      # subscribe to command topic    

state = "OFF"                                   # socket status
relay.off()                                     # set relay off
red_led.on()                                    # set red led off   
blue_led.off()                                  # set blue led on

send_status()                                   # update home assistant with light on / off, rgb and brightness

while True:
    c.check_msg()                               # non-blocking wait for message
    if button_flag:                             # if the button has been pressed
        button_flag = False                     # clear the button press
        f = open(w.cFile, 'w')                  # clear the password to force reconfig   
        w.c["pwd"] =  ""
        f.write(ujson.dumps(w.c))
        f.close()
        reset()                                 # hard reset
    sleep(.5)
    print('#',end='')
c.disconnect()                                  # if we come out of the loop for any reason then disconnect
reset()

    