import serial

from constants.constants import uart_color_mapping

def main(args):
    with serial.Serial() as ser:
        ser.baudrate = 9600
        ser.port = '/dev/serial0'
        ser.open()
        ser.write(b'abcd')
        ser.close()

def send_config_to_micro(config):
    convert_config_to_uart_format(config)
    send_message_to_micro('')

def send_done_to_micro():
    send_message_to_micro('D')

def convert_config_to_uart_format(config):
    result = ""
    for key in sorted(config["config"].keys()):
        color = config["config"][key]
        if color in uart_color_mapping:
            result += uart_color_mapping[color]
        else:
            result += "E"
    return result

def send_message_to_micro(message):
    if isinstance(message, str):
        message = message.encode()
    with serial.Serial() as ser:
        ser.baudrate = 9600
        ser.port = '/dev/serial0'
        ser.open()
        ser.write(message)
        ser.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))