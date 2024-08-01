import socket
import sys
import time
import argparse
import signal
import json
import pyautogui

MOVE_PIECE_LEFT = "left"
MOVE_PIECE_RIGHT = "right"
DROP_PIECE = "space"
ROTATE_PIECE = "up"


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
    print("Calibration done. You may now begin flappy bird!")
    
    while True:
        data, addr = sock.recvfrom(20000)  # buffer size is 20000 bytes
        if args.option == "print":
            obj = json.loads(data.decode())
            if obj.get('type') == 'emg':
                emg_data = obj.get('data')
                fp1 = emg_data[0]
                fp2 = emg_data[1]
                to_continue = 0
                for i in range(2, 8):
                    if emg_data[i] > 0.8:
                        to_continue += 1
                if (to_continue < 4):
                    if fp2 < 0.6:
                        rotated = False
                    elif (fp2 > 0.6 and fp1 > 0.6) and not rotated:
                        pyautogui.press('space')
                        rotated = True
            numSamples += 1