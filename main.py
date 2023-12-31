import serial
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from gpiozero import Buzzer
from gpiozero import LED
from time import sleep

# Variable to indicate that we are receiving data
receiving = False

# Variable to count how many bytes we has received
receivedByteCount = 0

# JSON string to send measurement
jsonString = ""

# Dictionary to store measurements
measurement = {
    "timestamp": "",
    "moisture": "",
    "raw": ""
}

# MQTT variables
client = None
broker = "125.234.135.55"
port = 1883
topic = "moisture-meter-results"

# GPIO variables
buzzer = None
def init_gpio():
    global buzzer

    #buzzer = LED(17)
    return True
def connect_mqtt():
    # Global variables
    global client

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port, 60)

    # Publish a message
    client.publish(topic, "Connection established")
    # Exit when user presses enter
    #input("Press enter to exit")

def connect_meter():
    # Global variables
    global receiving
    global receivedByteCount
    global jsonString
    global measurement
    global buzzer
    global isMeasurementLowerThan10

    try:
        ser = serial.Serial('/dev/ttyUSB0', 2400)
        #ser = serial.Serial('COM16', 2400)
    except:
        print("Serial not available")
        return False

    # Check if serial is available then print what is read
    if ser.isOpen():
        print(ser.name + ' is open...')
        while True:
            # Read bytes from serial
            data = ser.read()
            if (receiving == True):
                # If we are receiving data, print it without a new line
                print(data.hex(), end='')
                # Add to raw
                measurement["raw"] += data.hex()
                if (receivedByteCount == 5):
                    # If the value is 0x0a, skip it
                    if data.hex()[1:] == "a":
                        continue
                    else:
                        measurement["moisture"] += data.hex()[1:]
                if (receivedByteCount == 6):
                    measurement["moisture"] += data.hex()[1:]
                # Add decimal delimiter if we are at the last byte
                if receivedByteCount == 7:
                    temp = data.hex()[1:]
                if receivedByteCount == 8:
                    # Add decimal delimiter if value is 0x01 and vice versa
                    if data.hex()[1:] == "1":
                        measurement["moisture"] = measurement["moisture"][:2] + "." + temp
                    else:
                        measurement["moisture"] = measurement["moisture"][:2] + temp
                # Increment the receivedByteCount
                receivedByteCount += 1
                # If we have received 10 bytes, we are done
                if receivedByteCount == 10:
                    # Reset the receivedByteCount
                    receivedByteCount = 0
                    # We are no longer receiving data
                    receiving = False
                    # Print a new line
                    print('')
                    # Get the timestamp
                    timestamp = datetime.now()
                    # Add timestamp
                    measurement["timestamp"] = str(timestamp)
                    # Print the jsonString
                    jsonString = json.dumps(measurement)
                    print(jsonString)
                    # Publish the jsonString
                    client.publish(topic, jsonString)
                    # Blink buzzer GPIO to indicate that we have sent a measurement
                    #buzzer.beep()
                    # Reset the jsonString and measurement
                    jsonString = ""
                    measurement = {
                        "timestamp": "",
                        "moisture": "",
                        "raw": ""
                    }
                #else:
                    #print('Not enough 10 bytes')
            else:
                # Print what is read
                print(data.hex())
            # Check if we get 0x10
            if data == b'\x10':
                receiving = True
                # Send 0x20
                ser.write(b'\x20')
                # Then check if we got data, if so print it
                #if ser.in_waiting > 0:
                    #print("Got data")
                #else:
                    #print("No data")
        else:
            print('serial not available')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main():
    init_gpio()
    connect_mqtt()
    connect_meter()
    # Wait for any key to be pressed
    input("Press enter to exit")

main()