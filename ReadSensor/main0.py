import time
import serial
from Adafruit_IO import MQTTClient

# Constants for the Adafruit IO MQTT client
AIO_FEED_IDs = ["sensor1", "sensor2", "sensor3"]
AIO_USERNAME = "Fusioz"
AIO_KEY = "aio_IWLz76sudCyUHGAmFh7fWx1Vklza"

# Callback function for when the MQTT client connects
def connected(client):
    print("Connected to Adafruit IO ...")
    # Subscribe to all feeds in the AIO_FEED_IDs list
    for topic in AIO_FEED_IDs:
        client.subscribe(topic)

# Callback function for when a subscription is successful
def subscribe(client , userdata , mid , granted_qos):
    print("Subscription successful ...")

# Callback function for when the MQTT client disconnects
def disconnected(client):
    print("Disconnected from Adafruit IO ...")
    sys.exit (1)

# Callback function for when a message is received on a subscribed feed
def message(client , feed_id , payload):
    print("Received message: " + payload + " , feed id: " + feed_id)

# Create the Adafruit IO MQTT client
client = MQTTClient(AIO_USERNAME , AIO_KEY)
# Set the callback functions for the client
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
# Connect to the Adafruit IO server
client.connect()
# Run the client loop in the background
client.loop_background()

print("Sensors and Actuators")

# Constants for the serial communication
SCH_MAX_TASKS = 10
NO_TASK_ID = 0

# Function to find the name of the serial port
def getPort():
    # Get a list of available serial ports
    ports = serial.tools.list_ports.comports()
    # Iterate over the list of ports
    for port in ports:
        # Convert the port object to a string
        port_str = str(port)
        # Check if the string contains "FT232R USB UART" (this may need to be modified depending on your device)
        if "FT232R USB UART" in port_str:
            # Split the string on spaces to get the port name
            split_port = port_str.split(" ")
            comm_port = split_port[0]
            return comm_port
    # If no matching port was found, return "None"
    return "None"

# Get the name of the serial port
port_name = getPort()
print(port_name)

# If a serial port was found, open it
if port_name != "None":
    ser = serial.Serial(port=port_name, baudrate=9600)

# Function to write data to the serial port
def writeData(data):
    # Convert the data to a bytes-like object and write it to the serial port
    ser.write(bytes(data))

# Lists of bytes to send to the actuators to turn them on and off
relay1_ON = [0, 6, 0, 0, 0, 255, 200, 91] # id - function code - data(x4) - crc(check error)
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

#Function to set the state of device 1 (on or off)

def setDevice1(state):
    if state:
        # Write the "on" command to the serial port
        writeData(relay1_ON)
    else:
        # Write the "off" command to the serial port
        writeData(relay1_OFF)

#Lists of bytes to send to the actuators to turn them on and off

relay2_ON = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

#Function to set the state of device 2 (on or off)

def setDevice2(state):
    if state:
        # Write the "on" command to the serial port
        writeData(relay2_ON)
    else:
        # Write the "off" command to the serial port
        writeData(relay2_OFF)

#Function to read data from the serial port

def serial_read_data(ser):
    # Check if there are any bytes waiting to be read
    bytes_to_read = ser.inWaiting()
    if bytes_to_read > 0:
        # Read the bytes from the serial port
        out = ser.read(bytes_to_read)
        # Convert the bytes to a list of integers
        data_array = [b for b in out]
        # Check if the list has at least 7 elements (the minimum number of elements for a valid data packet)
    if len(data_array) >= 7:
        # Get the size of the data array
        array_size = len(data_array)
        # Calculate the value of the data using the last two elements of the array
        value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
        # Return the value
        return value
    else:
        # If the data array is too small, return -1
        return -1
    # If there were no bytes to read, return 0
    return 0

#List of bytes to send to the air tempurature sensor

air_temperature = [3, 3, 0, 0, 0, 1, 133, 232]

#Function to read the air temperature from the sensor

def readTemperature():
    # Clear any stale data from the serial buffer
    serial_read_data(ser)
    # Write the command to request soil temperature data to the serial port
    writeData(soil_temperature)
    # Wait for the sensor to process the request
    time.sleep(1)
    # Read the soil temperature value from the serial port
    temp = serial_read_data(ser)
    print("Temperature:", temp)
    # Publish the temperature value to the "sensor1" feed on Adafruit IO
    client.publish("sensor1", temp)
    return temp

#List of bytes to send to the air moisture sensor

air_moisture = [3, 3, 0, 1, 0, 1, 212, 40]

#Function to read the soil moisture from the sensor

def readMoisture():
    # Clear any stale data from the serial buffer
    serial_read_data(ser)
    # Write the command to request soil moisture data to the serial port
    writeData(soil_moisture)
    # Wait for the sensor to process the request
    time.sleep(1)
    # Read the soil moisture value from the serial port
    moisture = serial_read_data(ser)
    print("Moisture:", moisture)
    # Publish the moisture value to the "sensor2" feed on Adafruit IO
    client.publish("sensor2", moisture)
    return moisture

#List of bytes to send to the light sensor

light_sensor = [3, 3, 0, 2, 0, 1, 82, 90]

#Function to read the light level from the sensor

def readLight():
    # Clear any stale data from the serial buffer
    serial_read_data(ser)
    # Write the command to request light data to the serial port
    writeData(light_sensor)
    # Wait for the sensor to process the request
    time.sleep(1)
    # Read the light value from the serial port
    light = serial_read_data(ser)
    print("Light:", light)
    # Publish the light value to the "sensor3" feed on Adafruit IO
    client.publish("sensor3", light)
    return light

#Function to detect leaf illness using the temperature, moisture and light data

def detectLeafIllness():
    # Read the temperature, moisture, and light data
    temp = readTemperature()
    moisture = readMoisture()
    light = readLight()
    # Check if any of the values are abnormal
    if temp > 30 or moisture < 20 or light > 700:
        print("Leaf illness detected!")
    else:
        print("Leafs are healthy.")

#Read the data from the sensors and detect leaf illness every 5 seconds

while True:
    detectLeafIllness()
time.sleep(5)