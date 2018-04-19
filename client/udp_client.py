import socket
import serial
from time import sleep

IP = "192.168.1.1"
PORT = 3553

ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
print(ser.name)

while True:

	data = ser.read(12)

	print("Data: ", data ,"\t",len(data), "Bytes |")

	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSock.sendto(data, (IP, PORT))
