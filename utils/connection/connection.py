import socket
import json
import logging as log


class Connection:
    def __init__(self, port=23783, is_server=True):

        self.port = port
        self.socket = socket.socket()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.conn = None

        self.is_server = is_server
