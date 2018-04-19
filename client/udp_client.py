import socket
import serial

IP = "192.168.1.1"	# Beagle Bone AP Default Gateway IP
PORT = 3553		# Beagle Bone DSTR Server Port

ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)	# (port, baud, timeout)

print(ser.name)		# /dev/ttyUSB0

while True: # Run Forever

	# Number of Byes to Read
	
	data = ser.read(12)

	# Display Data
	
	print("Data: ", data ,"\t",len(data), "Bytes |")

	# Send Data
	
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSock.sendto(data, (IP, PORT))
