import socket
import sys
import time
import argparse
import signal
import json
import pyautogui
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)


# Clean exit from print mode
def exit_print(signal, frame): 
    print("Closing listener")
    sys.exit(0)


if __name__ == "__main__":
    # Collect command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=12345, help="The port to listen on")
    parser.add_argument("--address", default="/openbci", help="address to listen to")
    parser.add_argument("--option", default="print", help="Debugger option")
    parser.add_argument("--len", default=8, help="Debugger option")
    args = parser.parse_args()

    # Set up necessary parameters from command line
    length = args.len
    if args.option == "print":
        signal.signal(signal.SIGINT, exit_print)

    # Connect to socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (args.ip, args.port)
    sock.bind(server_address)

    # Display socket attributes
    print('--------------------')
    print("-- UDP LISTENER -- ")
    print('--------------------')
    print("IP:", args.ip)
    print("PORT:", args.port)
    print('--------------------')

    # Receive messages
    print("Calibration period, remain neutral...")
    start = time.time()
    numSamples = 0
    duration = 10
    rotated = False
    space_pressed = False
    data, addr = sock.recvfrom(20000)  # buffer size is 20000 bytes
    print("Calibration done!")
    led = 0
    
    while True:
        data, addr = sock.recvfrom(20000)  # buffer size is 20000 bytes
        if args.option == "print":
            obj = json.loads(data.decode())
            if obj.get('type') == 'focus':
                emg_data = obj.get('data')
                if (emg_data == 1 and led == 0):
                    GPIO.output(17,GPIO.HIGH)
                    led = 1
                elif(emg_data == 0 and led == 1):
                    GPIO.output(17,GPIO.LOW)
                    led = 0
            numSamples += 1
    
GPIO.cleanup()
