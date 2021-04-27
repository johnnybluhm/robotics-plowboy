"""plow_epuck controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, GPS
import math

# create the Robot instance.
robot = Robot()

# ePuck Constants
EPUCK_AXLE_DIAMETER = 0.053  # ePuck's wheels are 53mm apart.
MAX_SPEED = 6.28


TIME_STEP = int(robot.getBasicTimeStep())
WHITE_OBJECT_THRESHOLD = 30  # white_pixels
GREEN_OBJECT_THRESHOLD = 450  # green_pixels
REACHED_TARGET_THRESHOLD = 0.1 #m
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
gps = robot.getDevice("gps")
gps.enable(TIME_STEP)
keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP)  # can change sampling period here

left_speed = 0  # rad/s?
right_speed = 0  # rad/s?
#mode = 'manual'
#mode = 'snow_seeker'
#mode = 'inverse_kinematics'
#mode = 'wall_avoidance'
mode = 'stupid_plow'
leftMotor = robot.getDevice("left wheel motor")
rightMotor = robot.getDevice("right wheel motor")
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)
pose_x = 0
pose_y = 0
pose_theta = 0

figure_8_path = [ (-0.37, -0.35), (0.4,-0.4),(0.4,0.4), (-0.4,0.4)]
current_target = 0
#target_x = figure_8_path[current_target][0]
#target_y = figure_8_path[current_target][1]
target_y = 0.35
target_x = 0.35
TIMER_COUNT = 0
# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:

	gps_x = gps.getValues()[0]
	gps_y = gps.getValues()[2]
	
	#print("x "+str(gps_x))
	#print("y "+str(gps_y))
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

	for x in range(0, int(width / 3)):  # 1st chunk of image
		for y in range(0, int(height)):  # only need bottom half of image
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 240 and green > 240 and blue > 240:
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 1 "+str(white_count))
	#print("grey count chunk 1 " + str(green_count))
	if (white_count > WHITE_OBJECT_THRESHOLD):
		white_list[0] = True
	if (green_count > GREEN_OBJECT_THRESHOLD):
		green_list[0] = True
	white_count = 0
	green_count = 0
	for x in range(int(width / 3), int(2 / 3 * width)):  # 2nd chunk of image
		for y in range(0, int(height)):  # only need bottom half of image
			red = image[x][y][0]
			green = image[x][y][1]
			blue = image[x][y][2]
			if red > 240 and green > 240 and blue > 240:
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 2 "+str(white_count))
	#print("grey count chunk 2 " + str(green_count))
	if (white_count > WHITE_OBJECT_THRESHOLD):
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
			if red > 240 and green > 240 and blue > 240:
				white_count += 1
			if red < 50 and green > 150 and blue < 50:
				green_count += 1
	#print("white count chunk 3 "+str(white_count))
	#print("grey count chunk 3 " + str(green_count))
	if (white_count > WHITE_OBJECT_THRESHOLD):
		white_list[2] = True
	if (green_count > GREEN_OBJECT_THRESHOLD):
		green_list[2] = True
	print(white_list)
	#print(green_list)

	# can now program controller based off camera data
	if mode == 'inverse_kinematics':		
		# Inverse kinematics
		# error
		#print("Seeking snow")
		rho = math.sqrt( (target_y- pose_y)**2  +  (target_x-pose_x)**2 )
		alpha = math.atan2(target_y-pose_y, target_x -pose_x) + pose_theta

		if rho < REACHED_TARGET_THRESHOLD:
			current_target+=1
			"""if(current_target == 4):
				current_target = 0
			target_x = figure_8_path[current_target][0]
			target_y = figure_8_path[current_target][1]"""
			#left_speed = 0
			#right_speed = 0

		if(abs(alpha)>0.25):
			pos_scalar=0
			angular_scalar= -10*alpha
		else:
			pos_scalar= 10*rho
			angular_scalar= -5*alpha

		"""if(alpha== 0):
			angular_scalar = 0
			pos_scalar = 10*rho
		elif abs(alpha) <1.57 and abs(alpha) > 0.7:
			angular_scalar = -10*alpha #rotate faster
			pos_scalar = 1*rho
		elif abs(alpha)< 0.7 and abs(alpha) > 0.3:
			angular_scalar = -5* alpha
			pos_scalar = 5* rho
		else:
			angular_scalar = -2.5*alpha
			pos_scalar = 2.5*rho"""
						
		left_speed = (2* pos_scalar - angular_scalar*EPUCK_AXLE_DIAMETER)/2		
		right_speed = (2* pos_scalar + angular_scalar*EPUCK_AXLE_DIAMETER)/2

		#print("alpha: "+str(alpha)+"\nRho: "+str(rho))
	"""if white_list[1] == True:
		# drive toward snow
		mode = 'inverse_kinematics'
	elif white_list[0] == True:
		# turn left
		mode = 'inverse_kinematics'
	elif white_list[2] == True:
		# turn right
		mode = 'inverse_kinematics'"""


	if mode == 'wall_avoidance':
		# map navigation
		#print("Avoiding walls")
		if green_list[1] == True and green_list[0] == True:
			# wall, turn right
			right_speed = -MAX_SPEED
			left_speed = MAX_SPEED
		else:
			# go straight
			right_speed = MAX_SPEED
			left_speed = MAX_SPEED
	if mode == 'stupid_plow':
		left_speed = MAX_SPEED / 2
		right_speed =-MAX_SPEED / 2

		if white_list[1] == True:
			#push snow forward for 1 second			
			left_speed = MAX_SPEED
			right_speed = MAX_SPEED
			leftMotor.setVelocity(left_speed)
			rightMotor.setVelocity(right_speed)
			for i in range(0,100):
				robot.step(TIME_STEP)
			left_speed = -MAX_SPEED
			right_speed = -MAX_SPEED
			leftMotor.setVelocity(left_speed)
			rightMotor.setVelocity(right_speed)
			for i in range(0,100):
				robot.step(TIME_STEP)

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

	pose_y += ds * math.cos(pose_theta)
	pose_x += ds * math.sin(pose_theta)
	pose_theta += (dsr - dsl) / EPUCK_AXLE_DIAMETER
	#print("X: %f Y: %f Theta: %f " % (pose_x, pose_y, pose_theta))
# Enter here exit cleanup code.