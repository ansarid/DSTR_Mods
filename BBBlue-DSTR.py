#!/usr/bin/env python3

# Modify /etc/default/bb-wl18xx for AP SSID and Gateway <---- Especially important!

#led.red.on()
#time.sleep(30)
#led.green.on()
#led.red.off()

# To Do:

# 1. Check if sudo
# 2. Check if rcpy installed
# 3. config file

import time, math
import getopt, sys

# import rcpy library
# This automatically initizalizes the robotics cape
import rcpy 
import rcpy.servo as servo
import rcpy.clock as clock

import os
import time
import socket
import serial


# Servo  defaults
duty = 0
period = 0.02

base_channel	= 1
shoulder_channel= 2
elbow_channel	= 3
pitch_channel	= 4
roll_channel	= 5
grabber_channel	= 6

base_dock		= 0
shoulder_dock	= -1.5
elbow_dock		= 1.5
pitch_dock		= -0.5
roll_dock		= 0
grabber_dock	= -1.1

base_ready		= 0
shoulder_ready	= -0.7
elbow_ready		= 0.5
pitch_ready		= -0.6
roll_ready		= 0
grabber_ready	= 0.1


base_duty = 0
pitch_duty = 0
roll_duty = 0

serial_input = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)  # (port, baud, timeout)

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
		os.sys("sudo apt-get update and sudo apt-get install roboticscape -y and sudo apt-get upgrade roboticscape -y and sudo apt-get install python3 python3-pip -y and sudo pip3 install rcpy and sudo pip3 install numpy")
		
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


import rcpy
import rcpy.motor as motor
import rcpy.gpio as gpio
import rcpy.led as led

def motors(x, y):

	motor.set(motor_x, x)
	motor.set(motor_y, y)

# Server Details

UDP_IP = "192.168.1.1"	# IP to Listen on
UDP_PORT = 3553			# Port to Listen on

# Place to Store Data

bufferSize = 1024 # Yes, lots of space.

# Set Motors Pins

motor_x = 3
motor_y = 4

# Initial Motor Duty Cycles

duty_x = 0
duty_y = 0

# Set RCPY State to rcpy.RUNNING

rcpy.set_state(rcpy.RUNNING)

base_srvo = servo.Servo(base_channel)
shoulder_srvo = servo.Servo(shoulder_channel)
elbow_srvo = servo.Servo(elbow_channel)
pitch_srvo = servo.Servo(pitch_channel)
roll_srvo = servo.Servo(roll_channel)
grabber_srvo = servo.Servo(grabber_channel)

base_clck = clock.Clock(base_srvo, period)
shoulder_clck = clock.Clock(shoulder_srvo, period)
elbow_clck = clock.Clock(elbow_srvo, period)
pitch_clck = clock.Clock(pitch_srvo, period)
roll_clck = clock.Clock(roll_srvo, period)
grabber_clck = clock.Clock(grabber_srvo, period)

def dock_arm():
	base_srvo.set(base_dock)
	shoulder_srvo.set(shoulder_dock)
	elbow_srvo.set(elbow_dock)
	pitch_srvo.set(pitch_dock)
	roll_srvo.set(roll_dock)
	grabber_srvo.set(grabber_dock)


def ready_arm():
	base_srvo.set(base_ready)
	shoulder_srvo.set(shoulder_ready)
	elbow_srvo.set(elbow_ready)
	pitch_srvo.set(pitch_ready)
	roll_srvo.set(roll_ready)
	grabber_srvo.set(grabber_ready)

try:
	# Start UDP Server

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	sock.settimeout(.25)

	# enable servos				
	servo.enable()

	# start clock
	base_clck.start()
	shoulder_clck.start()
	elbow_clck.start()
	pitch_clck.start()
	roll_clck.start()
	grabber_clck.start()
	
	dock_arm()
	
	time.sleep(1)
	
	ready_arm()

	time.sleep(0.5)
	
	while True:

		if rcpy.get_state() == rcpy.RUNNING:

			try:	
			
#				line = serial_input.readline()
#				print(line)
			
				data, addr = sock.recvfrom(bufferSize)
				
				if len(data) == 0:
				
					print("Receiving empty packets!")
				
				elif len(data) == 4:
			
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0],"  ", data[1],"  ", data[2],"  ", data[3], "  |   Data from DSTR App")
				
				elif len(data) == 12:
				
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11],"   |   Data from Nunchuck Device")
					
				elif len(data) != 4 and len(data) != 12:
					
					print(time.time(),"\t",len(data),"\t","|   Data:  ", data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11],"   |   Data from Unknown Device")

			except socket.timeout:

				duty_x = 0
				duty_y = 0
				data = 0
				motor.set_brake(motor_x)
				motor.set_brake(motor_y)
				continue

			if int(data[0]) == 187:

				duty_x = 1*(int(data[3])-255)/255

			elif int(data[0]) == 170:

				duty_x = -1*(int(data[3])-255)/255

			

			if int(data[2]) == 187:

				duty_y = 1*(int(data[1])-255)/255

			elif int(data[2]) == 170:

				duty_y = -1*(int(data[1])-255)/255

#			print(duty_x,duty_y)

#			motors(duty_x,duty_y)
			
			shoulder_duty = -0.7
			elbow_duty = 0.5
			
			
			
			if data[0] == 170 and data[0] != data[2] and data[7] > 1:

				base_duty = base_duty - 0.1	
			
			
			elif data[2] == 170 and data[0] != data[2] and data[7] > 1:

				base_duty = base_duty + 0.1	
			
			
			if data[5] > 150 and data[7] > 1:
			
				pitch_duty = pitch_duty - 0.15
				
				#roll_duty = (0.027 * data[4] - 3.54)
			
			elif data[5] < 100 and data[7] > 1:
				
				pitch_duty = pitch_duty - 0.15
			
			
			
			
			
			if data[4] > 180 and data[7] > 1:
				
				roll_duty = roll_duty + 0.15
				
				#roll_duty = (0.027 * data[4] - 3.54)
			
			elif data[4] < 90 and data[7] > 1:
				
				roll_duty = roll_duty - 0.15
			
			
			
			
			
			grabber_duty = data[8]



			if (base_duty > 1.5):

				base_duty = 1.5

			elif (base_duty < -1.5):
				
				base_duty = -1.5



			if (shoulder_duty > 1.5):

				shoulder_duty = 1.5

			elif (shoulder_duty < -1.5):
				
				shoulder_duty = -1.5


			if (elbow_duty == 1):

				elbow_duty = -1.1

			elif (elbow_duty == 0):
				
				elbow_duty = 1.1


			if (pitch_duty > 1.5):

				pitch_duty = 1.5

			elif (pitch_duty < -1.5):
				
				pitch_duty = -1.5



			if (roll_duty > 1.5):

				roll_duty = 1.5

			elif (roll_duty < -1.5):
				
				roll_duty = -1.5


			#print(roll_duty, pitch_duty)


			if (grabber_duty == 1): #  and data[7] > 1

				grabber_duty = -1.5

			elif (grabber_duty == 2): #  and data[7] > 1
				
				grabber_duty = 0.6

			base_srvo.set(base_duty)
			shoulder_srvo.set(shoulder_duty)
			elbow_srvo.set(elbow_duty)
			pitch_srvo.set(pitch_duty)
			roll_srvo.set(roll_duty)
			grabber_srvo.set(grabber_duty)
			
			pass

		# Check if Paused
	
		elif rcpy.get_state() == rcpy.PAUSED:

			# do nothing
			pass

except KeyboardInterrupt:
	
	# Kill if Ctrl-C
	
	dock_arm()
	
	time.sleep(1)
	
	# stop clock
	base_clck.stop()
	shoulder_clck.stop()
	elbow_clck.stop()
	pitch_clck.stop()
	roll_clck.stop()
	grabber_clck.stop()
        
    # disable servos
	servo.disable()
	
	pass
		
finally:
	
	dock_arm()
	
	# stop clock
	base_clck.stop()
	shoulder_clck.stop()
	elbow_clck.stop()
	pitch_clck.stop()
	roll_clck.stop()
	grabber_clck.stop()
        
        # disable servos
	servo.disable()
	
	# Finish Program
	print("\nExiting!")
