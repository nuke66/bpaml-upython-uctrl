import network
import socket
from time import sleep
import machine

connection = None

try:
    from secrets import secrets
except ImportError:
    print("Error: secrets.py file not found or secrets dictionary not defined.")
    print("Please create a secrets.py file with your WiFi credentials.")
    raise

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets['ssid'], secrets['password'])

    count=0
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())
    return wlan.ifconfig()[0]

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print("socket opened")
    return connection


def serve(connection):
    print("serving")
    #Start a web server
    state = 'OFF'
    internal_led.off()
    led.off()
    while True:
        print("accepting connection")
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
            print(request)
        except IndexError:
            pass

        if request.find('/?led=toggle'):
            print('LED ON')
            internal_led.toggle()
            led.toggle()            
            state = 'ON' if state == 'OFF' else 'ON'

        html = """<!DOCTYPE html>
<html>
<head><title>BPAML uPython</title></head>
<body style="background-color: #A0F5D3;">
<h1 style="text-align: center;">µPython server example</h1>
<form style="flex-direction: column; display: flex; align-items: center; padding: 50px 10px;border: 1px solid grey; background-color: white; max-width: 300px; margin: 0 auto;">
<button name="led" value="toggle" type="submit" style="display:block; margin: 20px 0; width:100px; height: 60px">Toggle LED</button><div>LED is """ + state + """</div>
</form>
</body>
</html>
"""
        client.send(html)
        client.close()

        
# main

internal_led=machine.Pin("LED",machine.Pin.OUT)
led=machine.Pin(15,machine.Pin.OUT)

print("connecting to wifi")
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    print("keyboard interrupt")
    if connection:
        connection.close()


