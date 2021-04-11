#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import paho.mqtt.client as mqtt 
import time, threading, ssl, random 
import RPi.GPIO as GPIO 
import time 

 
#pin configuration 

TRIG=7 
ECHO=11 

GPIO.setmode(GPIO.BOARD) 

 # client, user and device details 

serverUrl   = "" 
port        = 1883 
clientId    = "" 
device_name = "" 
tenant      = "" 
username    = "" 
password    = "" 

receivedMessages = [] 

# display all incoming messages 
def on_message(client, userdata, message): 
    print("Received operation " + str(message.payload)) 
    if (message.payload.startswith("510")): 
        print("Simulating device restart...") 
        publish("s/us", "501,c8y_Restart"); 
        print("...restarting...") 
        time.sleep(1) 
        publish("s/us", "503,c8y_Restart"); 
        print("...done...") 

# send distance measurement 
def sendMeasurements(): 
    try: 
#----------- 
        print ("Distance measurement in progress") 
        GPIO.setup(TRIG,GPIO.OUT) 
        GPIO.setup(ECHO,GPIO.IN) 
        GPIO.output(TRIG,False) 
        print("waiting for sensor to settle...") 
        time.sleep(0.2) 
        GPIO.output(TRIG,True) 
        time.sleep(0.00001) 
        GPIO.output(TRIG,False) 
        while GPIO.input(ECHO)==0: 
            pulse_start=time.time() 

        while GPIO.input(ECHO)==1: 
            pulse_end=time.time() 
            pulse_duration=pulse_end-pulse_start 
            distance=pulse_duration*17150 

        distance=round(distance,2) 
        print ("distance:",distance,"cm") 
#------------- 
       
        publish("s/us", "200,distance,centimeter," + str(distance)+",cm") 
    except (KeyboardInterrupt, SystemExit): 
        print ('Received keyboard interrupt, quitting ...') 

 

# publish a message 

def publish(topic, message, waitForAck = False): 
    mid = client.publish(topic, message, 2)[1] 
    if (waitForAck): 
        while mid not in receivedMessages: 
            time.sleep(0.25) 

def on_publish(client, userdata, mid): 
    receivedMessages.append(mid) 

# connect the client to Cumulocity and register a device 
client = mqtt.Client(clientId) 
client.username_pw_set(tenant + "/" + username, password) 
client.on_message = on_message 
client.on_publish = on_publish 
 
client.connect(serverUrl, port) 
client.loop_start() 
publish("s/us", "100," + device_name + ",c8y_MQTTDevice", True) 
publish("s/us", "110,S123456789,MQTT test model,Rev0.1") 
publish("s/us", "114,c8y_Restart") 
print ("Device registered successfully!") 


client.subscribe("s/ds") 
while True:
    sendMeasurements()
    time.sleep(1)