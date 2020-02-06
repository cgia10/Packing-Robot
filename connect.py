

import socket


def connect2Arm():
    TCP_IP = "169.254.222.242"
    TCP_PORT = 8000
    BUFFER_SIZE = 1024
    MESSAGE = "Hello, World!"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    return s
