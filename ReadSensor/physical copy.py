import time
import serial
from Adafruit_IO import MQTTClient

# Constants for the Adafruit IO MQTT client
AIO_FEED_IDs = ["sensor1", "sensor2", "sensor3"]
AIO_USERNAME = "Fusioz"
AIO_KEY = "aio_SIMB58VHI2yANpldmbp9cww8EAxi"

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
# Function to write data to the serial port
def writeData(data):
    # Convert the data to a bytes-like object and write it to the serial port
    ser.write(bytes(data))

# Lists of bytes to send to the actuators to turn them on and off
relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91] # id - function code - data(x4) - crc(check error)
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

# Function to set the state of device 1 (on or off)
def setDevice1(state):
    if state:
        # Write the "on" command to the serial port
        writeData(relay1_ON)
    else:
        # Write the "off" command to the serial port
        writeData(relay1_OFF)

# Lists of bytes to send to the actuators to turn them on and off
relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

# Function to set the state of device 2 (on or off)
def setDevice2(state):
    if state:
        # Write the "on" command to the serial port
        writeData(relay2_ON)
    else:
        # Write the "off" command to the serial port
        writeData(relay2_OFF)

# Function to read data from the serial port
def serial_read_data(ser):
    # Check if there are any bytes waiting to be read
    bytes_to_read = ser.inWaiting()
    if bytes_to_read > 0:
        # Read the bytes from the serial port
        out = ser.read(bytes_to_read)
        # Convert the bytes to a list of integers
        data_array = [b for b in out]
        # Check if the list has at least 7 elements (the minimum number of elements for a
