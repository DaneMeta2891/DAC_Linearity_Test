import socket
from socket import timeout
import subprocess

#part of *IDN return string
VALID_IDS = ["MSO-X 4054A"]

#needs to be manually altered, check the scope
HOST_NAME = "a-mx4054a-00115"

class scopeConnectionUtil:
    PORT = 5025
    TIMEOUT = 2

    def __init__(self):
        self.s = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *a):
        self.disconnect()

    def check_host_name(self, host_name):
        if HOST_NAME != host_name:
            self.edit_host_name(host_name)

    def edit_host_name(self, host_name):
        with open("editself.py", 'r') as file:
            script = file.readlines()
        with open("editself.py", 'w') as file:
            for line in script:
                if (line.find("HOST_NAME = ") != -1 and line.find("write") == -1):
                    file.write("HOST_NAME = " + "\"" + host_name + "\"\n")
                else:
                    file.write(line)

    def get_host_ip(self):
        try:
            return socket.gethostbyname(HOST_NAME)
        except Exception as error:
            print("error getting scope IP")
            print("socket error:", error)

    def connect(self):
        scope_IP = self.get_host_ip()
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(self.TIMEOUT)
            self.s.connect((scope_IP, self.PORT))
            return True
        except Exception as error:
            self.disconnect()
            print("connection error: ", error)
        return False
    
    def send(self, msg):
        self.s.send((msg + "\n").encode())
        
    def send_recv(self, msg):
        self.s.send((msg + "\n").encode())
        try:
            return self.s.recv(1024).decode().rstrip("\n")
        except timeout:
            return "socket timeout"
        except Exception as error:
            return "send_recv error: " + error
    
    def flush_buffer(self):
        while (True):
            try:
                print(self.s.recv(1024))
            except timeout:
                print("buffer flush complete")
                break
        
    def disconnect(self):
        self.s.close()