import socket
from socket import timeout

PORT = 5025

class scopeConnectionUtil:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(4)
    
    def connect(self, SCOPE_IP):
        self.s.connect((SCOPE_IP, PORT))
    
    def send(self, msg):
        self.s.send((msg + "\n").encode())
        
    def sendRecv(self, msg):
        self.s.send((msg + "\n").encode())
        try:
            print(self.s.recv(1024).decode().rstrip("\n"))
            return
        except timeout:
            print("Socket Timeout")
            return False
    
    def disconnect(self):
        self.s.close()