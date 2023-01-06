print("Multidisciplinary AIoT Project")
import sys
from Adafruit_IO import MQTTClient
import time
import port
import serial.tools.list_ports
import read_sensors
import relay_control
from model import model

#Constants
AIO_FEED_IDs = ["sensor1", "sensor2", "sensor3", "sensor4", "relay1", "relay2", "AI"]
AIO_USERNAME = "Fusioz"
AIO_KEY = "aio_UbsT33Vd9VqI2i6NwpmCawL8onEQ"
PUBLISH_INTERVAL = 100
DETECTION_INTERVAL = 150

#Variables
count = 1
count_detect = 1
isRelay1Signal = False
isRelay1 = False
isRelay2Signal = False
isRelay2 = False

#Connect to serial port
portName = port.getPort()
print("Port: " + portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)

#MQTt callbacks
def connected(client):
    print("Ket noi thanh cong ...")
    for topic in AIO_FEED_IDs:
        client.subscribe(topic)

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe thanh cong...")

def disconnected(client):
    print("Ngat ket noi ...")
    sys.exit (1)

def message(client , feed_id , payload):
    #Update relay states based on MQTT messages
    if feed_id == "relay1":
        global isRealay1Signal, isRelay1
        isRelaySignal = True
        if payload == "ON":
            isRelay1 = True
            print("Relay 1: ON")
        else:
            isRelay1 = False
            print("Relay 1: OFF")
    elif feed_id == "relay2":
        global isRelay2Signal, isRelay2
        isRelay2Signal = True
        if payload == "ON":
            isRelay2 = True
            print("Relay 2: ON")
        else:
            isRelay2 = False
            print("Relay 2: OFF")

#Connect to Adafruit IO
client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

#Main loop
while True:
    if count == PUBLISH_INTERVAL:
        air_temp_value = read_sensors.readTemperature(ser, port.serial_read_data)/10
        print(f"Air Temperature: {air_temp_value}°C")
        client.publish("sensor2", air_temp_value)
        air_humi_value = read_sensors.readMoisture(ser, port.serial_read_data)/10
        print(f"Air Humidity: {air_humi_value}%")
        client.publish("sensor1", air_humi_value)

        soil_temp_value = read_sensors.readSoilTemp(ser, port.serial_read_data)/100
        print(f"Soil Temperature: {soil_temp_value}°C")
        client.publish("sensor3", soil_temp_value)
        soil_humi_value = read_sensors.readSoilMoisture(ser, port.serial_read_data)/100
        print(f"Soil Humidity: {soil_humi_value}%")
        client.publish("sensor4", soil_humi_value)
        count = 0
    if isRelay1Signal:
        if isRelay1:
            relay_control.setDevice1(True, ser)
        else:
            relay_control.setDevice1(False, ser)
        isRelay1Signal = False
    if isRelay2Signal:
        if isRelay2:
            relay_control.setDevice2(True, ser)
        else:
            relay_control.setDevice2(False, ser)
        isRelay2Signal = False
    # if count_detect == DETECTION_INTERVAL:
    #     print('Detecting...')
    #     model.image_capture()
    #     ai_result = model.image_detector()
    #     client.publish("AI", ai_result)
    #     count_detect = 0

    count_detect += 1
    count += 1
    time.sleep(0.5)