# ESP8266-Home-Assistant-Smart-Socket
This Micropython project is to Hack a Hyleton313 cheap WiFi smart socket

The first thing to read is this write up https://github.com/arendst/Sonoff-Tasmota/wiki/Hyleton-313-Smart-Plug

<img src="/resources/IMG_0265.JPG" width="300">
<img src="/resources/IMG_0264.JPG" width="300">

Once you get it open you can see the blue processor board next to the relay. This is an ESP8266 variant, so I decided we could re-flash this plug with micropython


There is a blue led and a red led that shine through the little pin hole on the front. Oth of these are directly controlled from GPIO pins. There is also a neat little push button switch that also goes to a GPIO pin. The relay is controlled by yet another GPIO, but when you are testing and powering the board from the usb serial this doesn't work. Probably because there is some sort of transistor driver on the board.
So, dismantle the case as per the instructions in the link above.
Thanks to the work of Theo Arends, you don't need to unsolder the ESP8266 board.

Connect your USB seral board as per Theo's instructions, but don't flash the Sonoff software. Instead, download the Micropyton image from http://micropython.org/download#esp8266 and flash it to the board using:
`esptool.py --port COM3 write_flash -fs 1MB -fm dout 0x0 esp8266-20180511-v1.9.4.bin`

Change COM3 to suit your serial port

Change esp8266-20180511-v1.9.4.bin to the name of the image you downloaded

If you haven't used esptool before, Adafruit has a great article here https://learn.adafruit.com/building-and-running-micropython-on-the-esp8266/flash-firmware

You should now be able to see the micropython prompt when you use a terminal tool such as putty.

<img src="/resources/putty.png" width="400">

Th enext step is to enble WebREPL. Once again, Adafruit has a great tutorial on how to do this. https://learn.adafruit.com/micropython-basics-esp8266-webrepl/access-webrepl

Once you have enabled WebREPL you can run scripts and upload files from your browser.

<img src="/resources/webrepl.png" width="400">

Now you can de-solder the wires for your USB Serial connector and re-assemble the Socket.

##The Files
timer.py - a class to implement a flashing led. You simple pass the timer an LED and it flashes until you run deinit

wificonf.py - I wanted this to be as easy as possible to change and move, so, at first boot you connect to the SSID presented by the ESP8266 and point a browser to the ESP8266 default IP address http://192.168.4.1. The default ESSID in the core is "ESPSocket1". You will need to chnage that if you are going to use more than one socket. You will be presented with the page below.

<img src="/resources/webpage.png" width="400">

Carefully enter your wifi SSID and password then click submit. Up to this point the blue LED will be flashing. Once you enter your credentials, and the socket connects to your wifi, the led will go out.

The socket will now be available for use by Home Assistant,or any other system that uses MQTT,

Here is a snippet from my config.yaml file
```
  - platform: mqtt_json
    name: "SOCKET1"
    state_topic: "home/socket1/status"
    command_topic: "home/socket1/set"
    
```


