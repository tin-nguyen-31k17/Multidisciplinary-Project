#Import the package to the project
print("Sensors and Actuators")
import time
import serial.tools.list_ports
from Adafruit_TIO import MQTTClient

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

#Find the comport name (in Windows)
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range (0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort


#Open the COM port
portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port = portName, baudrate = 9600)

#Send command to Actuators
#1st Actuator
relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91]
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

def setDevice1(state):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

#2nd Actuator
relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

def setDevice2(state):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)

#Receive Response
def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

#Read soil temperature
soil_temperature = [3, 3, 0, 0, 0, 1, 133, 232]
def readTemperature():
    serial_read_data(ser)
    ser.write(soil_temperature)
    time.sleep(1)
    return serial_read_data(ser)

#Read soil moisture
soil_moisture = [3, 3, 0, 1, 0, 1, 212, 40]
def readMoisture():
    serial_read_data(ser)
    ser.write(soil_moisture)
    time.sleep(1)
    return serial_read_data(ser)

while True:
    print("TEST MOTOR")
    setDevice1(True)
    time.sleep(2)
    setDevice1(False)
    time.sleep(2)

    setDevice2(True)
    time.sleep(2)
    setDevice2(False)
    time.sleep(2)

    print("TEST SENSOR")
    print(readTemperature())
    time.sleep(2)
    print(readMoisture())
    time.sleep(2)