import time
import signal

import sys
from Adafruit_IO import MQTTClient
import time

AIO_FEED_IDs = ["sensor1", "sensor2", "sensor3", "sensor4" "relay1"]
AIO_USERNAME = "Fusioz"
AIO_KEY = "aio_IWLz76sudCyUHGAmFh7fWx1Vklza"

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
    print("Nhan du lieu: " + payload + " , feed id: " + feed_id)
    if feed_id == "bbc-btnled":#nut nhan 1
      if payload == "ON":
        print("relay 1")
        setDevice1(True)
      else:
        setDevice1(False)
    if feed_id == "relay2":#nut nhan 2
      if payload == "ON":
        setDevice2(True)
      else:
        setDevice2(False)
client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()


print("Sensors and Actuators")
import serial.tools.list_ports

SCH_MAX_TASKS = 10
NO_TASK_ID = 0

#find the comport name
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)
        if "FT232R USB UART" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

#open the COM port
portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)


#send command to actuators
relay1_ON  = [0, 6, 0, 0, 0, 255, 200, 91] #id cua slave: id - function code - data(x4) - crc(check error)
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

def setDevice1(state):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

def setDevice2(state):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)


def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        #print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0

soil_temperature =[3, 3, 0, 0, 0, 1, 133, 232]
def readTemperature():
    serial_read_data(ser)
    ser.write(soil_temperature)
    time.sleep(1)
    temp = serial_read_data(ser)
    print("Temperature:", temp)
    client.publish("bbc-temp", temp)
    return temp

soil_moisture = [3, 3, 0, 1, 0, 1, 212, 40]
def readMoisture():
    serial_read_data(ser)
    ser.write(soil_moisture)
    time.sleep(1)
    humid = serial_read_data(ser)
    print("Moisture:   ", humid)
    client.publish("bbc-humid", humid)
    return humid

def show_num():
    print('NUM 1, 2, 3, ...')

def show_char():
    print('CHAR a, b, c, ...')

list_func = [[show_num, 0]]

def task_init():
    print("--- Initial System ---")

def sch_report_status():
    print("Status System:...")

def sch_go_to_sleep():
    print("System Sleep:...")
    time.sleep(2)

def timer_init():
    timer = 0
    return timer

def watchdog_init():
    print("Watchdog Init ...")
    time.sleep(2)

sch_task_queue = [[task_init, 1, 2, 0]]
#sch_task_queue = [[show_num, 0, 0, 0]]


# pTask:
# Delay  [1] ( ticks ) until the function will (next) be run
# Period [2]: Interval ( ticks ) between subsequent runs
# RunMe  [3]: Incremented (by scheduler) when task is due to execute


def sch_init():
    print('PHASE: INITIAL SCHEDULER')

    global sch_task_queue
    leng_queue_task = len(sch_task_queue)
    print(leng_queue_task)
    for i in range(leng_queue_task-1):
        sch_delete_task(i)

    sch_task_queue = [[task_init, 1, 2, 0]]
    error_code = 0
    timer_init()
    watchdog_init()

def sch_add_task(function=task_init, delay=0, period=0):
    print('PHASE: ADD Task')

    global sch_task_queue
    index = len(sch_task_queue)

    if len(sch_task_queue) == SCH_MAX_TASKS:
        # error_code = ERROR_SCH_TOO_MANY_TASKS
        print("ERROR: MAX TASKS")
        return SCH_MAX_TASKS

    new_task = [function, delay, period, 0]
    sch_task_queue.append(new_task)

    return index

def sch_update():
    print('PHASE: UPDATE')

    global sch_task_queue
    leng_queue_task = len(sch_task_queue)
    for i in range(0, leng_queue_task):
        if sch_task_queue[i][0]:
            if sch_task_queue[i][1] == 0:
                sch_task_queue[i][3] = sch_task_queue[i][3] + 1
                if sch_task_queue[i][2]:
                    sch_task_queue[i][1] = sch_task_queue[i][2]
            else:
                sch_task_queue[i][1] = sch_task_queue[i][1] - 1

def PeriodElapsedCallback():
    sch_update()

def sch_dispatch_task():
    print('PHASE: DISPATCH')

    global sch_task_queue
    leng_queue_task = len(sch_task_queue)
    for i in range(0, leng_queue_task):
        if sch_task_queue[i][3] > 0:
            sch_task_queue[i][0]()
            sch_task_queue[i][3] = sch_task_queue[i][3] - 1
            if sch_task_queue[i][2] == 0:
                sch_delete_task(i)

    # Report system status
    sch_report_status()
    #The scheduler enters idle mode at this point
    sch_go_to_sleep()


def sch_delete_task(TASK_INDEX):
    print('PHASE: DELETE Task')

    return_code = 0
    if len(sch_task_queue) == TASK_INDEX or sch_task_queue[TASK_INDEX][0] == 0:
        print("Error")
        return_code = 1
    else:
        return_code = 0
    sch_task_queue.pop(TASK_INDEX)
    

def main():
    print("Smart Agriculture!")

    sch_init()

    sch_add_task(readTemperature, 2, 1)
    sch_add_task(readMoisture, 2, 1)
    
    while(True):
        #setDevice2(True)
        #time.sleep(1)
        #setDevice2(False)
        sch_update()
        time.sleep(1)
        sch_dispatch_task()
        
        time.sleep(1)


if __name__ == "__main__":
    main()

