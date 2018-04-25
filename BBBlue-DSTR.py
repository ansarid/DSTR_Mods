#!/usr/bin/env python3

# Modify /etc/default/bb-wl18xx for AP SSID and Gateway <---- Especially important!

#led.red.on()
#time.sleep(30)
#led.green.on()
#led.red.off()

# To Do:

# 1. Check if sudo - DONE
# 2. Check if rcpy installed - Not working wth
# 3. config file
# 4. Start DSTR on Boot?
# 5. Start DSTR on SSH?

# Servo  defaults
servo_duty = 1.5
period = 0.02
channel = 0
sweep = False
brk = False
free = False

import os
import time
import socket

user = os.getenv("SUDO_USER")
if user is None:
    print("\n   \033[1;37;48mExecute as \033[1;31;48msudo\033[1;37;48m!\033[0;37;48m\n")
    exit()

try:
	import rcpy
#	print("\nRCPY is installed!")
except ImportError:
	print("\nRCPY is not installed!")
	
	permission = input("Should I install the missing packages for you? (y/n): ")
    
	if permission.lower == "y":
		print("Installing missing packages!")
		os.sys("sudo apt-get update && sudo apt-get install roboticscape -y && sudo apt-get upgrade roboticscape -y && sudo apt-get install python3 python3-pip -y && sudo pip3 install rcpy")
		
		# Configure Network
		
		change_ap_ssid = input("Change the AP SSID? (y/n): ")
		
		if change_ap_ssid.lower == "y":
			
			ap_ssid = input("Enter new SSID: ")
			
		elif change_ap_ssid.lower == "n":
			
			pass
		
		change_ap_pass = input("Change the AP password? (y/n): ")

		if change_ap_pass.lower == "y":
			
			ap_pass = input("Enter new AP password: ")
			
		elif change_ap_pass.lower == "n":
			
			pass
		
		# Configure Home Directory
		
		home_dir = input("Set default home directory to /var/lib/cloud9? (y/n): ")
		
		if home_dir.lower == "y":
			
			home_dir = "/var/lib/cloud9"
			
		elif home_dir.lower == "n":
			
			home_dir = input("Set default home directory to /home/debian? (y/n): ")
				
			if home_dir.lower == "y":
				
				home_dir = "/home/debian"
				
			elif home_dir.lower == "n":
				
				home_dir = input("Enter custom directory path: ")
			
		# Configure Logo
		
		logo = input("Do you want to display the DSTR logo at the start of a SSH session? (y/n): ")
		
		if logo.lower == "y":
			
			os.sys("echo '", home_dir ,"\nclear\npython ./.dstr_logo.py'","wget https://raw.githubusercontent.com/ansarid/DSTR_Mods/master/.dstr_logo.py")
		
		elif logo.lower == "n":
				
			os.sys("echo '", home_dir ,"\nclear'","wget https://raw.githubusercontent.com/ansarid/DSTR_Mods/master/.dstr_logo.py")
		
		print("Done!")
	
		exit()
	
	elif permission.lower == "n":
		print("\nExiting!\n")
		exit()

import time, math
import getopt, sys
import rcpy
import rcpy.motor as motor
import rcpy.servo as servo
import rcpy.clock as clock
import rcpy.gpio as gpio
import rcpy.led as led

def motors(x, y):

	motor.set(motor_x, x)
	motor.set(motor_y, y)

# Server Details

UDP_IP = "192.168.1.1"	# IP to Listen on
UDP_PORT = 3553			# Port to Listen on

# Place to Store Data

bufferSize = 1024 # Yes, lots of space, will resize appropriately later.

# Set Motors Pins

motor_x = 3
motor_y = 4

# Initial Motor Duty Cycles

motor_duty_x = 0
motor_duty_y = 0

# Set RCPY State to rcpy.RUNNING
rcpy.set_state(rcpy.RUNNING)

srvo = servo.Servo(channel)

clck = clock.Clock(srvo, period)

try:
	# Start UDP Server

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	sock.settimeout(.25)

	# enable servos				
	servo.enable()

	# start clock
	clck.start()
	srvo.set(servo_duty)
	
	while True:

		if rcpy.get_state() == rcpy.RUNNING:

			try:	
			
				data, addr = sock.recvfrom(bufferSize)
				
				if len(data) == 4:
				
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0],"  ", data[1],"  ", data[2],"  ", data[3],"|  Duty: ",motor_duty_x,",",motor_duty_y, "  |   Data from DSTR App")
				
				elif len(data) == 12:
				
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11],"|  Duty: ",motor_duty_x,",",motor_duty_y, "   |   Data from Nunchuck Device")
					
				elif len(data) != 4 and len(data) != 12:
					
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11],"|  Duty: ",motor_duty_x,",",motor_duty_y, "   |   Data from Unknown Device")

			except socket.timeout:

				motor_duty_x = 0
				motor_duty_y = 0
				data = 0
				motor.set_brake(motor_x)
				motor.set_brake(motor_y)
				continue

			if int(data[0]) == 187:

				motor_duty_x = (int(data[3])-255)/255

			elif int(data[0]) == 170:

				motor_duty_x = -1*(int(data[3])-255)/255

			if int(data[2]) == 187:

				motor_duty_y = (int(data[1])-255)/255

			elif int(data[2]) == 170:

				motor_duty_y = -1*(int(data[1])-255)/255

			motors(motor_duty_x,motor_duty_y)
			
			srvo.set(d)
			
			pass

		# Check if Paused
	
		elif rcpy.get_state() == rcpy.PAUSED:

			# do nothing
			pass

except KeyboardInterrupt:

	# Kill if Ctrl-C

	# stop clock
	clck.stop()

	# disable servos
	servo.disable()

	pass

finally:

	# stop clock
	clck.stop()

	# disable servos
	servo.disable()

	# Finish Program
	print("\nExiting!")
