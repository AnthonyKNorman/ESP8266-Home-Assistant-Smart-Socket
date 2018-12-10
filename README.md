# ESP8266-Home-Assistant-Smart-Socket
This Micropython project is to Hack a Hyleton313 cheap WiFi smart socket

The first thing to read is this write up https://github.com/arendst/Sonoff-Tasmota/wiki/Hyleton-313-Smart-Plug

<img src="/resources/IMG_0265.JPG" width="300">

Once you get it open you can see the blue processor board next to the relay. This is an ESP8266 variant, so I decided we could re-flash this plug with micropython

<img src="/resources/IMG_0264.JPG" width="300">

There is a blue led and a red led that shine through the little pin hole on the front. Oth of these are directly controlled from GPIO pins. There is also a neat little push button switch that also goes to a GPIO pin. The relay is controlled by yet another GPIO, but when you are testing and powering the board from the usb serial this doesn't work. Probably because there is some sort of transistor driver on the board.
So, dismantle the case as per the instructions in the link above.
Thanks to the work of Theo Arends, you don't need to unsolder the ESP8266 board.

Connect your USB seral board as per Theo's instructions, but don't flash the Sonoff software. Instead, download the Micropyton image from http://micropython.org/download#esp8266 and flash it to the board using:
`esptool.py --port COM3 write_flash -fs 1MB -fm dout 0x0 esp8266-20180511-v1.9.4.bin`

Change COM3 to suit your serial port

Change esp8266-20180511-v1.9.4.bin to the name of the image you downloaded

If you haven't used esptool before, Adafruit has a great article here https://learn.adafruit.com/building-and-running-micropython-on-the-esp8266/flash-firmware

You should now be able to see the micropython prompt when you use a terminal tool such as putty.









