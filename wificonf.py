import machine, network, ubinascii, os, utime, usocket, ujson, timer
from machine import Pin

def qs_parse(qs):
    line = qs.decode()
    parameters = {}
    ampersandSplit = line.split("&")
    for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = equalSplit[1]
    return parameters

class wificonf(object):
    def __init__(self, cFile = "creds.txt", red=0, blue=2):
        self.red_led     = Pin(red, Pin.OUT)                               # red led on front
        self.blue_led    = Pin(blue, Pin.OUT)                              # bue led on front
        self.red_led.value(1)                                              # red led off
        self.blue_led.value(1)                                             # blue led off
        self.cFile       = cFile
        sta_if           = network.WLAN(network.STA_IF)
        sta_if.active(True)
        self.name        = sta_if.config('dhcp_hostname')
        self.connected   = False
        
        try:       
            f = open(self.cFile, 'r')                # try to open credential file
            self.c = ujson.loads(f.read())
            f.close()
        except Exception as e:                  # failed
            print("Configuration file does not exist", e)
            f = open(self.cFile, 'w')
            self.c = {"name": self.name, "ssid": "ssid", "pwd": "pwd", "mqtt": "192.168.1.1"}
            f.write(ujson.dumps(self.c))
            f.close()
       
    def wifi(self):
        self.red_flash   = timer.led_toggle(self.red_led, msecs=200)      # start the red light flashing
        print("Setting WiFi", self.c['ssid'], self.c['pwd'])
        ap_if = network.WLAN(network.AP_IF)
        sta_if = network.WLAN(network.STA_IF)
        # if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(self.c['ssid'], self.c['pwd'])
        count = 0
        while not sta_if.isconnected():
            print('.',end='')
            if sta_if.isconnected():
                break
            count += 1
            if count > 20:
                return False
                self.red_flash.deinit()                             # stop the blue light flashing

            utime.sleep(1)
        print('\nnetwork config:', sta_if.ifconfig())
        print(sta_if.config('dhcp_hostname'))

        mac = ubinascii.hexlify(sta_if.config('mac'),':').decode()
        print (mac)
        ap_if.active(False)                 # disable the access point
        self.red_flash.deinit()             # stop the red light flashing
        return True

    def html(self):
        head = """<!DOCTYPE html>
        <html>
            <head>
                <title>WiFi Config</title> 
                <style>
                    h1 {color:red;}
                    body {color:blue; font-family: Arial, Helvetica, sans-serif;}
                </style>
            </head>
            """
        body = """
            <body> <h1>WiFi Config</h1>
                <form action="" method="post">
                  MQTT:<br>
                  <input type="text" name="mqtt" value="{}"><br>
                  ESSID:<br>
                  <input type="text" name="name" value="{}"><br>
                  SSID:<br>
                  <input type=\"text\" name=\"ssid\" value=\"{}\"><br>
                  Password:<br>
                  <input type=\"password\" name=\"pwd\" value=\"{}\"><br><br>
                  <input type=\"submit\" value=\"Submit\">
                </form>
            </body>
        </html>""".format(self.c['mqtt'], self.c['name'], self.c['ssid'], self.c['pwd'])
        
        html = head + body
        return head + body



    def get_params(self):
        self.blue_flash = timer.led_toggle(self.blue_led)      # start the blue light flashing

        print("Getting credentials", self.c)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(False)
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
        ap_if.config(essid=self.c['name'], authmode=network.AUTH_WPA_WPA2_PSK, password="uPy12345")
        print ("Defining socket")
        addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = usocket.socket()
        s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        s.bind(addr)
         
        s.listen(1)

        print('listening on', addr)
        
        configured = False
        while not configured:
            cl, addr = s.accept()
            print('client connected from', addr)
            cl_file = cl.makefile('rwb', 0)
            content_length = 0
            while True:
                line = cl_file.readline()
                if not line or line == b'\r\n':
                    break
                        
                print(line)
                if 'Content-Length' in line:
                    content_length = int(line[16:-2])
                    print ('content_length', content_length, 'type', type)
                    
            if content_length:
                body = cl_file.read(content_length)
                print('BODY', body)
                params = qs_parse(body)
                print(params)
                f = open(self.cFile, 'w')
                f.write(ujson.dumps(params))
                f.close()
                self.c = params
                configured = True
            
            print(type)
            response = self.html()
            cl.send(response)
            cl.close()
        s.close()
        self.blue_flash.deinit()                             # stop the blue light flashing


 
