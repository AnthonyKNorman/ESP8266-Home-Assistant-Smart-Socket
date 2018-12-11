"""
configuration.yaml looks like this
light:
  - platform: mqtt
    name: "SOCKET1"
    state_topic: "home/socket1/status"
    command_topic: "home/socket1/set"

"""
from umqtt.simple import MQTTClient
from machine import Pin, reset
import utime, ujson, os, wificonf

#### set these to match your requirements ####
state_topic = b"home/socket1/status"
command_topic = b"home/socket1/set"
server="192.168.1.99"                      # your MQTT server
name = 'ESPSocket1'                        # unique name for the socket

#### DO NOT CHANGE ANYTHING AFTER HERE ####

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
button      = Pin(13, Pin.IN, Pin.PULL_UP)       # button on outside of plug
red_led     = Pin(0, Pin.OUT)                   # red led on front
blue_led    = Pin(2, Pin.OUT)                   # bue led on front
onboard_led = Pin(4, Pin.OUT)                   # blue led on ESP8266 board(not visible)
relay       = Pin(15, Pin.OUT)                  # relay
state = "OFF"                                    # socket status
relay.off()
red_led.on()
blue_led.off()

wificonf.wificonf(name)

# connec to mqtt
c = MQTTClient(name, server)
c.set_callback(sub_cb)                          # set the callback function
c.connect()                                     # get connected
c.subscribe(command_topic)                      # subscribe to command topic    

send_status()                                   # update home assistant with light on / off, rgb and brightness

while True:
    # blocking wait for message
    c.check_msg()                                # endless loop waiting for messages
    now = utime.ticks_ms()
    while button.value() == 0:
        if utime.ticks_diff(utime.ticks_ms(), now) > 5000:
            os.remove('creds.txt')
            reset()
    utime.sleep(.5)
c.disconnect()                                  # if we come out of the loop for any reason then disconnect
reset()

    