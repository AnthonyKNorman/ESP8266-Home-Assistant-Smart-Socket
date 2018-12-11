import machine, network, ubinascii, os, utime, usocket, ujson, timer
from machine import Pin

def qs_parse(qs):
    parameters = {}
    ampersandSplit = qs.split("&")
    for element in ampersandSplit:
        equalSplit = element.split("=")
        parameters[equalSplit[0]] = equalSplit[1]
    return parameters

def parse_get(line):
    spaceSplit = line.split(' ')
    if '?' in spaceSplit[1]:
        querySplit = spaceSplit[1].strip().split('?')
        print('querySplit', querySplit)
        return qs_parse(querySplit[1].strip())
    a = []
    return a
    
class wificonf():
    def __init__(self, ssid, red=0, blue=2):
        self.red_led     = Pin(red, Pin.OUT)                   # red led on front
        self.blue_led    = Pin(blue, Pin.OUT)                   # bue led on front
        self.red_flash = timer.led_toggle(self.red_led)      # start the red light flashing
        self.cFile = "creds.txt"

        self.connected = False
        try:       
            f = open(self.cFile, 'r')                # try to open credential file
            self.c = ujson.loads(f.read())
            f.close()
        except Exception as e:                  # failed
            print("file does not exist", e)
            f = open(self.cFile, 'w')
            self.c = {"essid": ssid, "ssid": "", "pwd": ""}
            f.write(ujson.dumps(self.c))
            f.close
       
        while not self.connected:        
            print('c =',self.c)
            
            if  self.wifi():                        # if wifi setup good
                self.connected = True               # set flag
                
            if not self.connected:
                print("not connected")
                self.get_params()                   # open local web site to enter credentials

    def wifi(self):
        print("Setting WiFi", self.c['ssid'], self.c['pwd'])
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)
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
            utime.sleep(1)
        print('\nnetwork config:', sta_if.ifconfig())
        print(sta_if.config('dhcp_hostname'))

        mac = ubinascii.hexlify(sta_if.config('mac'),':').decode()
        print (mac)
        return True

    def get_params(self):
        self.blue_flash = timer.led_toggle(self.blue_led)           # start the red light flashing
        self.red_flash.deinit()                                # stop the red light flashing

        print("Getting credentials", self.c)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(False)
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(True)
        ap_if.config(essid=self.c['essid'], authmode=network.AUTH_WPA_WPA2_PSK, password="uPy12345")

        html = """<!DOCTYPE html>
        <html>
            <head> 
                <title>WiFi Config</title> 
                <style>
                    h1 {color:red;}
                    body {color:blue; font-family: Arial, Helvetica, sans-serif;}
                </style>
            </head>
            <body> <h1>WiFi Config</h1>
                <form action="">
                  SSID:<br>
                  <input type="text" name="ssid" value="*"><br>
                  Password:<br>
                  <input type="password" name="password" value="*"><br><br>
                  <input type="submit" value="Submit">
                </form>
            </body>
        </html>
        """
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
            while True:
                line = cl_file.readline()
                if not line or line == b'\r\n':
                    break
                str_line = line.decode()
                print(str_line, end='')
                if "GET /?" in str_line:
                    params = parse_get(str_line)
                    print(params)
                    self.c['ssid'] = params['ssid']
                    self.c['pwd'] = params['password']
                    f = open(self.cFile, 'w')
                    f.write(ujson.dumps(self.c))
                    f.close()
                    configured = True
            response = html
            cl.send(response)
            cl.close()
        s.close()
        self.blue_flash.deinit()                             # stop the blue light flashing


 
