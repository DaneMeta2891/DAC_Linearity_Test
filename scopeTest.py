import scopeCommunication
import socket
from socket import timeout

#Alter as needed
SCOPE_IP = "169.254.69.144"

socket = scopeCommunication.scopeCommunincation()
socket.connect(SCOPE_IP)
inputString = input("Enter Command String: ")
while (inputString != ""):
    socket.sendRecv(inputString[1:]) if inputString[0].lower() == "r" else socket.send(inputString)
    inputString = input("Enter Command String: ")
socket.disconnect()