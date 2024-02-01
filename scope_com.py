import socket
from socket import timeout
import subprocess

VALID_IDS = ["MSO-X 4054A"]

class scopeConnectionUtil:
    PORT = 5025
    TIMEOUT = 2

    def __init__(self):
        self.s = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *a):
        self.disconnect()

    def get_dynamic_ips(self):
        dynamic_lines = list()
        for line in subprocess.run(["arp", "-a"], capture_output=True).stdout.decode().split("\r\n"):
            if (line.find("dynamic") != -1):
                dynamic_lines.append([val for val in line.split(" ") if val != ''])
        return dynamic_lines

    def check_id(self):
        idn = self.send_recv("*IDN?")
        return True if idn.split(",")[1] in VALID_IDS else False

    def check_ips(self):
        with scopeConnectionUtil() as scope:
            for val in self.get_dynamic_ips():
                print(val[0])
                if (scope.connect(val[0]) and self.check_id(scope)):
                    return True

    def connect(self, scope_IP):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(self.TIMEOUT)
            self.s.connect((scope_IP, self.PORT))
            return True
        except Exception as error:
            self.disconnect()
            print("Socket Error: ", error)
        return False
    
    def send(self, msg):
        self.s.send((msg + "\n").encode())
        
    def send_recv(self, msg):
        self.s.send((msg + "\n").encode())
        try:
            return self.s.recv(1024).decode().rstrip("\n")
        except timeout:
            return "Socket timeout failure"
    
    def flush_buffer(self):
        while (True):
            try:
                print(self.s.recv(1024))
            except timeout:
                print("Completed Buffer Flush")
                break
    
    def check_socket(self):
        return self.send_recv("*IDN")
        
    def disconnect(self):
        self.s.close()