"""plow_epuck controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, GPS
import math
import numpy as np

# create the Robot instance.
robot = Robot()

# ePuck Constants
EPUCK_AXLE_DIAMETER = 0.053  # ePuck's wheels are 53mm apart.
MAX_SPEED = 6.28

TIME_STEP = int(robot.getBasicTimeStep())
WHITE_OBJECT_THRESHOLD = 35
MAXIMUM_WHITE_OBJECT_THRESHOLD = 40  # white_pixels
GREEN_OBJECT_THRESHOLD = 1300  # green_pixels
REACHED_TARGET_THRESHOLD = 0.01 #m
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
gps = robot.getDevice("gps")
gps.enable(TIME_STEP)
keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP)  # can change sampling period here

left_speed = 0  # rad/s?
right_speed = 0  # rad/s?
#mode = 'manual'
mode = 'plow'

leftMotor = robot.getDevice("left wheel motor")
rightMotor = robot.getDevice("right wheel motor")
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)
pose_x = 0
pose_y = 0
pose_theta = 0
last_pose_theta = 0

figure_8_path = [ (-0.37, -0.35), (0.4,-0.4),(0.4,0.4), (-0.4,0.4)]
current_target = 0
#target_x = figure_8_path[current_target][0]
#target_y = figure_8_path[current_target][1]
target_y = 0.35
target_x = 0.35
TIMER_COUNT = 0
white_counts = []

distance_to_white_values = {} 
loop_count = 0
push_snow_count = 0
free_spin_count = 0
# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:

	white_counts = []
	gps_x = gps.getValues()[0]
	gps_y = gps.getValues()[2]
	#print("x "+str(gps_x))
	#print("y "+str(gps_y))
	#print(target_x)
	if mode == 'manual':
		key = keyboard.getKey()
		while (keyboard.getKey() != -1): pass
		if key == keyboard.LEFT:
			right_speed = MAX_SPEED / 4
			left_speed = -MAX_SPEED / 4
		elif key == keyboard.RIGHT:
			right_speed = -MAX_SPEED / 4
			left_speed = MAX_SPEED / 4
		elif key == keyboard.UP:
			right_speed = MAX_SPEED
			left_speed = MAX_SPEED
		elif key == keyboard.DOWN:
			right_speed = -MAX_SPEED
			left_speed = -MAX_SPEED
		elif key == ord(' '):
			left_speed = 0
			right_speed = 0

	# processing camera data

	image = camera.getImageArray()
	# 77 77 77 for grey 100 100 100 100
	# print(image)
	white_list = [False, False, False]
	white_count = 0
	green_list = [False, False, False]
	green_count = 0
	width = camera.getWidth()
	height = camera.getHeight()
	chunk_pixels = width / 3 * height / 2
	divider = int(pose_theta / 6.28) * 5
	greenheight = False
	
	whitenum = WHITE_OBJECT_THRESHOLD - divider

	for x in range(0, int(width / 3)):  # 1st chunk of image
		for y in range(0, int(height)):  
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 220 and green > 220 and blue > 220 and (abs(red-blue-green) <6):
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 1 "+str(white_count))
	#print("grey count chunk 1 " + str(green_count))
	white_counts.append(white_count)
	if (white_count > whitenum):
		white_list[0] = True
	if (green_count > GREEN_OBJECT_THRESHOLD):
		green_list[0] = True
	white_count = 0
	green_count = 0
	for x in range(int(width / 3), int(2 / 3 * width)):  # 2nd chunk of image
		for y in range(0, 44):  
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 220 and green > 220 and blue > 220 and (abs(red-blue-green) <6):
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
		for y in range(50, int(height)):  
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 220 and green > 220 and blue > 220:
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 2 "+str(white_count))
	white_counts.append(white_count)
	#print("grey count chunk 2 " + str(green_count))
	if (white_count > whitenum):
		white_list[1] = True
	if (green_count > GREEN_OBJECT_THRESHOLD):
		green_list[1] = True
	white_count = 0
	green_count = 0
	for x in range(int(2 / 3 * width), int(width)):  # 3rd chunk of image
		for y in range(0, int(height)):  # only need bottom half of image
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 220 and green > 220 and blue > 220:
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 3 "+str(white_count))
	#print("grey count chunk 3 " + str(green_count))


	for x in range(0, width):
		for y in range (0, 10):
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red < 20 and green > 210 and blue < 20:
				greenheight = True

	white_counts.append(white_count)
	if (white_count > whitenum):
		white_list[2] = True
	if (green_count > GREEN_OBJECT_THRESHOLD):
		green_list[2] = True
	#print(white_list)
	#print(green_list)

	# can now program controller based off camera data
	if mode == 'plow':

		left_speed = MAX_SPEED / 2
		right_speed =-MAX_SPEED / 2
		free_spin_count+=1
		if white_list[1] == True and not abs(last_pose_theta-pose_theta) < .3:
			if abs(last_pose_theta-pose_theta) < .1:
				print("Same theta found")
			free_spin_count = 0
			mode = 'push_snow'
		if free_spin_count > 30: #62.5 loop counts = 1 second
			print("Raising threshold")
			WHITE_OBJECT_THRESHOLD+=2
			free_spin_count = 0
			if WHITE_OBJECT_THRESHOLD > MAXIMUM_WHITE_OBJECT_THRESHOLD:
				mode = 'stop'

	if mode == 'stop':
		print("stopped")
		left_speed = 0
		right_speed = 0
	if mode == 'push_snow':
		if greenheight == True or green_list[1] == True or green_list[0] == True or green_list[2] == True:
			mode = 'reverse'
		else:
			left_speed = MAX_SPEED
			right_speed = MAX_SPEED
			push_snow_count+=1
	if mode == 'reverse':
		if(push_snow_count == 0):
			mode = 'plow'
			last_pose_theta = pose_theta
		else:
			left_speed = -MAX_SPEED
			right_speed = -MAX_SPEED
			push_snow_count -= 1
	if right_speed > MAX_SPEED:
		right_speed = MAX_SPEED
	if left_speed > MAX_SPEED:
		left_speed = MAX_SPEED
	if right_speed < -MAX_SPEED:
		right_speed = -MAX_SPEED
	if left_speed < -MAX_SPEED:
		left_speed = MAX_SPEED

	leftMotor.setVelocity(left_speed)
	rightMotor.setVelocity(right_speed)

	# from lab 4
	#ODOMETRY
	vL = left_speed
	vR = right_speed
	EPUCK_MAX_WHEEL_SPEED = 0.11695 * TIME_STEP / 1000.0
	dsr = vR / MAX_SPEED * EPUCK_MAX_WHEEL_SPEED
	dsl = vL / MAX_SPEED * EPUCK_MAX_WHEEL_SPEED
	ds = (dsr + dsl) / 2.0

	pose_y -= ds * math.sin(pose_theta)
	pose_x -= ds * math.cos(pose_theta)
	pose_theta -= (dsr - dsl) / EPUCK_AXLE_DIAMETER
	
	#print("X: %f Y: %f Theta: %f " % (pose_x, pose_y, pose_theta))
# Enter here exit cleanup code.
