import json
import serial
import time

# Define the data to send
data = {
    "1": "red",
    "2": "blue",
    "3": "red",
    "4": "yellow",
    "5": "",
    "6": "",
    "7": "yellow",
    "8": "red"
}

# Convert the data to a JSON string
json_data = json.dumps(data)

# Setup serial connection
# Replace '/dev/ttyS0' with your serial port and adjust the baud rate if needed
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# Give some time for the serial connection to initialize
time.sleep(2)

try:
    # Send the data
    ser.write(json_data.encode())
    print("Data sent over UART:", json_data)
finally:
    # Close the serial connection
    ser.close()