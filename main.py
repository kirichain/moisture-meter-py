import serial
import paho.mqtt.client as mqtt

# Variable to indicate that we are receiving data
receiving = False

# Variable to count how many bytes we has received
receivedByteCount = 0

# MQTT variables
broker = "localhost"
port = 1883
topic = "moisture-meter-results"

def connect_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker, port, 60)

    # Publish a message
    client.publish(topic, "Hello world!")
    # Exit when user presses enter
    input("Press enter to exit")

def connect_meter():
    # Global variables
    global receiving
    global receivedByteCount

    ser = serial.Serial('/dev/ttyUSB0', 2400)

    # Check if serial is available then print what is read
    if ser.isOpen():
        print(ser.name + ' is open...')
        while True:
            # Read bytes from serial
            data = ser.read()
            if (receiving == True):
                # If we are receiving data, print it without a new line
                print(data.hex(), end='')
                # Increment the receivedByteCount
                receivedByteCount += 1
                # If we have received 4 bytes, we are done
                if receivedByteCount == 10:
                    # Reset the receivedByteCount
                    receivedByteCount = 0
                    # We are no longer receiving data
                    receiving = False
                    # Print a new line
                    print('')
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
    connect_meter()
    # Wait for any key to be pressed
    input("Press enter to exit")

main()