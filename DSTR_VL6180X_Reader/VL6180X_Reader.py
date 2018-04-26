import socket
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # (port, baud, timeout)

print(ser.name)         # /dev/ttyUSB0

while True: # Run Forever

        # Number of Byes to Read

        data = ser.read(3)
        line = ser.readline()

        # Display Data  
        print(data)
