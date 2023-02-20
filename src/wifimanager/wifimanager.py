import os
import sys
import uos
import machine
import network
import socket
import time

import wifimanager.htmlmanager as htmlmanager
import wifimanager.credentialsutility as Credentials
import wifimanager.requestutility as Req

version = '0.2 alpha'
ssid = 'PicoW2'
password = '12345678'

led = machine.Pin("LED",machine.Pin.OUT)

class WiFiManager():
    
    def __init__(self):       
        
        if Credentials.Founds():
            credentials = Credentials.Read()
            n_name=credentials[0]
            n_password=credentials[1]
            
            n_name=n_name.replace('\n','')
            n_password=n_password.replace('\n','')
            print("Credentials founds. Connecting...")
            self._sub_connect_to_network(n_name,n_password)
        else:
            print("Credentials NOT founds")
            
            self._sub_start_portal()         
    
    _isReady = True;
    def IsReady(self):
        return self._isReady

    def _sub_start_portal(self):
        html = htmlmanager.HTMLMANAGER('Titolo')
        htmlDropdownNetworks='<option></option>'
        
        wlan = network.WLAN()
        wlan.active(True)
        networks = wlan.scan()
        i=0
        networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
        for w in networks:
            i+=1
            htmlDropdownNetworks+="<option value='" + w[0].decode() +"'>" + w[0].decode() +"</option>"
            print(i,w[0].decode())
        
        css = htmlmanager.GetCss()
        htmlMain = html.GetIndexPage('Wi-Fi Configuration', htmlDropdownNetworks)    
        htmlInfo = html.GetInfoPage('Info', version, os.uname().version, os.uname().machine )    
        htmlPasswordOk = html.GetPasswordOkPage('Password saved')    
        htmlShutdown = html.GetStoppedPage('Stopped')    
        htmlRestarting = html.GetRestartingPage('Restarting')
        
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password=password)
        ap.active(True)

        while ap.active() == False:
            pass

        print('Connection successful')
        status = ap.ifconfig()
        print(ap.ifconfig())
        
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)

        print('listening on', addr)        
        
        print(["Connect on", ssid +"." ,"Navigate on", str(status[0]), "Password:", "12345678" ])
        
        # Listen for connections
        while True:
         
            try:
                cl, addr = s.accept()
                #print('client connected from', addr)            
                request = cl.recv(1024)
                print('----------- START RAW -----------')
                print(request)
                print('----------- END RAW -----------')
                requestString = request.decode('utf-8')
                
                if request.startswith('POST'):                              
                    n=Req.GetParameterValue(requestString,'txtnetwork=')                
                    p=Req.GetParameterValue(requestString,'txtpassword=')
                                    
                    Credentials.Save(n,p)
                    
                    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                    cl.send(htmlPasswordOk)
                    
                    print(["Informations", "saved." ,"Restart","the device"])
                    
                else:                  
                    requestedPage = Req.GetRequestPageGet(requestString)             
                            
                    if requestedPage == '/' or requestedPage == '':
                        cl.send(htmlMain)
                        cl.close()
                    elif requestedPage == '/style.css':
                        cl.send(css)
                        cl.close()    
                    elif requestedPage == '/info':                    
                        cl.send(htmlInfo)
                        cl.close()                
                    elif requestedPage == '/server/restart':
                        print('Restarting...')
                        cl.send(htmlRestarting)
                        cl.close()
                        machine.reset()                                 
                            
                    else:
                        print('Page not found')
                        print('404: ' + requestedPage)
                        cl.send('HTTP/1.0 404 OK\r\nContent-type: text/html\r\n\r\n')
                        cl.close()

            except OSError as e:
                cl.close()
                
                print('connection closed')

    def _sub_connect_to_network(self, n_name,n_password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(n_name,n_password)
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
        max_wait -= 1
        time.sleep(1)
        
        if wlan.status() != 3:
            Credentials.Clear()
            print('network connection failed. Network name:' + n_name) 
            machine.reset()

        status = wlan.ifconfig()
        print('Connected!')
        
        print("Connected to " + n_name + ". My ip is " + status[0])

        time.sleep(1)
        
        return 

    def ClearCredentials(self):
        Credentials.Clear()
        
    _registeredFunctions=[]
    
    def Register(self, command, sub):
        print("Registered " + command)
        self._registeredFunctions.append([command,sub])
 
 #https://stackoverflow.com/questions/74551529/raspi-pico-w-errno-98-eaddrinuse-despite-using-socket-so-reuseaddr
 
    def WaitForCommand(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 80))
        s.listen(5)
                    
        while True:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            #print('Content = %s' % request)  
            
            for x in self._registeredFunctions:
                req = request.find(x[0])
                
                if req>0:                    
                    
                    response = """ok"""
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    conn.close()
                    s.close()
                    
                    x[1]()
                    
                    self._isReady = True
                    return
                
            response = """command not registered"""
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            s.close()
            self._isReady = True
            
            #led_on = request.find('/?led=on')
            #led_off = request.find('/?led=off')
            #if led_on == 6:
            #    print('LED ON')
            #    led.on()
            #if led_off == 6:
            #    print('LED OFF')
            #    led.off()
            
            
            
            