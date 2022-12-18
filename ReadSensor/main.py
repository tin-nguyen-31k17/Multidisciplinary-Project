import sys
from Adafruit_IO import MQTTClient
import time
from readSerial import *

AIO_FEED_IDs = ["sensor1", "sensor2"]
AIO_USERNAME = "Fusioz"
AIO_KEY = "aio_SIMB58VHI2yANpldmbp9cww8EAxi"

def connected(client):
    print("Ket noi thanh cong ...")
    for topic in AIO_FEED_IDs:
        client.subscribe(topic)

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe thanh cong ...")

def disconnected(client):
    print("Ngat ket noi ...")
    sys.exit (1)

def message(client , feed_id , payload):
    print("Nhan du lieu: " + payload + " , feed id:" + feed_id)

client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()
counter = 10
sensor_type = 0

while True:
    if sensor_type == 0:
        temp = readTemperature()
        client.publish("sensor1", temp)
        sensor_type = 1;
    elif sensor_type == 1:
        humi = readMoisture()
        client.publish("sensor2", humi)
        sensor_type = 0;

    readSerial(client)
    time.sleep(1)
    pass