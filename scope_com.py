import socket
from socket import timeout

#part of *IDN return string
VALID_IDS = ["MSO-X 4054A"]

#scope host name, used to get the IP address of the scope
HOST_NAME = "a-mx4054a-00115"

#scope communication class
class scopeConnectionUtil:
    PORT = 5025
    TIMEOUT = 2

    def __init__(self):
        self.s = None
    
    def __del__(self):
        self.disconnect()

    #using these two functions in place of a config file for HOST_NAME
    def check_host_name(self, host_name:str):
        '''
        check if HOST_NAME is set to host_name, if not changes the variable

        host_name (str): string used to check/config HOST_NAME
        '''
        if HOST_NAME != host_name:
            self.edit_host_name(host_name)

    def edit_host_name(self, host_name:str):
        '''
        edits this scripts HOST_NAME constant 

        host_name (str): str to replace HOST_NAME with
        '''
        with open("scope_com.py", 'r') as file:
            script = file.readlines()
        with open("scope_com.py", 'w') as file:
            for line in script:
                if (line.find("HOST_NAME = ") != -1 and line.find("write") == -1):
                    file.write("HOST_NAME = " + "\"" + host_name + "\"\n")
                else:
                    file.write(line)

    def get_host_ip(self):
        '''
        uses HOST_NAME to get scope IP address
        '''
        try:
            return socket.gethostbyname(HOST_NAME)
        except Exception as error:
            print("error getting scope IP")
            print("socket error:", error)

    def connect(self):
        '''
        connects to scope with IP returned from get_host_ip()
        '''
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
    
    def send(self, msg:str):
        '''
        sends a string over socket

        msg (str): string to send
        '''
        self.s.send((msg + "\n").encode())
        
    def send_recv(self, msg:str):
        '''
        sends a string over socket then waits for return data

        msg (str): string to send
        '''
        self.s.send((msg + "\n").encode())
        try:
            return self.s.recv(1024).decode().rstrip("\n")
        except timeout:
            return "socket timeout"
        except Exception as error:
            return "send_recv error: " + error
    
    def flush_buffer(self):
        '''
        flushes return buffer of connected scope
        '''
        while (True):
            try:
                print(self.s.recv(1024))
            except timeout:
                print("buffer flush complete")
                break
        
    def disconnect(self):
        self.s.close()