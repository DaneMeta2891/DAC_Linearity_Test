import socket
from socket import timeout

class scopeConnectionUtil:
    PORT = 5025
    TIMEOUT = 2

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.TIMEOUT)
    
    def connect(self, scope_IP):
        for _ in range(5):
            try:
                self.s.connect((scope_IP, self.PORT))
                return True
            except:
                print("Error connecting to scope, retrying...")
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
        
    def disconnect(self):
        self.s.close()