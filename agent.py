#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time, random

# client, user and device details
serverUrl   = "mqtt.cumulocity.com"
clientId    = "uniqueNameYouProvide"
device_name = "nameYouProvide"
tenant      = "tenant"
username    = "username"
password    = "password#"

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

# send temperature measurement
def sendMeasurements():
    print("Sending temperature measurement...")
    publish("s/us", "200,c8y_Temperature,T," + str(random.randint(20, 30))+",C°")

# publish a message
def publish(topic, message, waitForAck = False):
    mid = client.publish(topic, message, 2)[1]
    if (waitForAck):
        while mid not in receivedMessages:
            time.sleep(0.25)

def on_publish(client, userdata, mid):
    receivedMessages.append(mid)

# connect the client to Cumulocity IoT and register a device
client = mqtt.Client(clientId)
client.username_pw_set(tenant + "/" + username, password)
client.on_message = on_message
client.on_publish = on_publish

client.connect(serverUrl)
client.loop_start()
publish("s/us", "100," + device_name + ",c8y_MQTTDevice", True)
publish("s/us", "110,S123456789,MQTT test model,Rev0.1")
publish("s/us", "114,c8y_Restart")
print("Device registered successfully!")

client.subscribe("s/ds")
while True:
    sendMeasurements()
    time.sleep(2)
