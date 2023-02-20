import os
import sys
import uos
import network
import machine
import socket
import time

import wifimanager.wifimanager as wifimanager

led = machine.Pin("LED",machine.Pin.OUT)
reset_button = machine.Pin(16, machine.Pin.IN)

print("Started!")

WiFIManager = wifimanager.WiFiManager()
    
def sub_ledon():
    print("ledon")
    led.on()    

def sub_ledoff():
    print("ledoff")
    led.off()    
    
def sub_ledBlink3():
    print("blink3")
    for x in range(3):
        led.on()
        time.sleep_ms(200)
        led.off()
        time.sleep_ms(200)    
        
def sub_ledBlink10():
    print("blink10")
    for x in range(10):
        led.on()
        time.sleep_ms(200)
        led.off()
        time.sleep_ms(200)  

#while True:
#    logic_state = reset_button.value()
#    if logic_state == True:     
#      WiFIManager.ClearCredentials()
#      print(["Reset","on","2 seconds"])
#      time.sleep(2)
#      machine.reset()
      
#Inizio codice applicativo           
#time.sleep(1)
#led.off()
#time.sleep(1)
#led.on()
#time.sleep(1)
#led.off()

    
WiFIManager.Register("/?led=on", sub_ledon);
WiFIManager.Register("/?led=off", sub_ledoff);
WiFIManager.Register("/?blink3", sub_ledBlink3);
WiFIManager.Register("/?blink10", sub_ledBlink10);

while True:
    WiFIManager.WaitForCommand()
    time.sleep(1)
    
