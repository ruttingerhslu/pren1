import serial

def main(args):
    with serial.Serial() as ser:
        ser.baudrate = 9600
        ser.port = '/dev/serial0'
        ser.open()
        ser.read(100)
        ser.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))