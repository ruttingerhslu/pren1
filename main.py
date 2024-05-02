import serial
import time

import sys
sys.path.append('modules')

from verification.verification import send_end_signal_to_server, send_start_signal_to_server
from cube_detection import cube_calculator

ser = serial.Serial('/dev/serial0', 9600, timeout=1)

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').rstrip()
        print("Empfangene Daten:", data)
        if data == "start":
            send_start_signal_to_server()
            cube_calculator()
            print("Start Program")
        if data == "ok":
            print("sent config has been built")
        if data == "done":
            send_end_signal_to_server()
            print("Build is completed")
            
    time.sleep(0.1)
