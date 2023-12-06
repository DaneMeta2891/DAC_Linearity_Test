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
            print(self.s.recv(1024).decode().rstrip("\n"))
            return
        except timeout:
            print("Socket Timeout")
            return False
        
    def disconnect(self):
        self.s.close()