import serial
import time

from verification.verification import send_end_signal_to_server

ser = serial.Serial('/dev/serial0', 9600, timeout=1)

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').rstrip()
        print("Empfangene Daten:", data)
        if data == "start":
            print("Start Program")
        if data == "ok":
            print("sent config has been built")
        if data == "done":
            send_end_signal_to_server()
            print("Build is completed")
            
    time.sleep(0.1)
