"""plow_epuck controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import math

# create the Robot instance.
robot = Robot()

# ePuck Constants
EPUCK_AXLE_DIAMETER = 0.053 # ePuck's wheels are 53mm apart.
MAX_SPEED = 6.28

TIME_STEP = int(robot.getBasicTimeStep())
WHITE_OBJECT_THRESHOLD = 25 #white_pixels 
GREY_OBJECT_THRESHOLD = 150 #green_pixels
camera = robot.getDevice("camera")
camera.enable(TIME_STEP)
keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP) #can change sampling period here

left_speed = 0 #rad/s?
right_speed = 0 #rad/s?
#mode = 'manual'
mode = 'snow_seeker'

leftMotor = robot.getDevice("left wheel motor")
rightMotor = robot.getDevice("right wheel motor")
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)
pose_x = 0
pose_y = 0
pose_theta = 0 

target_x = 0.2
target_y = 0.3

# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:

	"""if pose_y  >0.5:
		#go back to goal
		mode='snow_seeker'"""


	if mode == 'manual':
		key = keyboard.getKey()
		while(keyboard.getKey() != -1): pass
		if key == keyboard.LEFT:
			right_speed = MAX_SPEED
			left_speed = -MAX_SPEED
			if(abs(right_speed)>MAX_SPEED):
				right_speed=MAX_SPEED
			if(abs(left_speed)>MAX_SPEED):
				left_speed=MAX_SPEED
		elif key == keyboard.RIGHT:
			right_speed = -MAX_SPEED
			left_speed = MAX_SPEED
			if(abs(right_speed)>MAX_SPEED):
				right_speed=MAX_SPEED
			if(abs(left_speed)>MAX_SPEED):
				left_speed=MAX_SPEED
		elif key == keyboard.UP:
			right_speed = MAX_SPEED
			left_speed = MAX_SPEED
			if(abs(right_speed)>MAX_SPEED):
				right_speed=MAX_SPEED
			if(abs(left_speed) > MAX_SPEED):
				left_speed = MAX_SPEED
		elif key == keyboard.DOWN:
			right_speed = -MAX_SPEED
			left_speed = -MAX_SPEED
			if(abs(right_speed)>MAX_SPEED):
				right_speed=MAX_SPEED
			if(abs(left_speed)>MAX_SPEED):
				left_speed=MAX_SPEED

		elif key == ord(' '):
			left_speed = 0
			right_speed =0

	#processing camera data

	image = camera.getImageArray()
	#77 77 77 for grey 100 100 100 100
	#print(image)
	white_list = [False, False, False]
	white_count = 0
	grey_list = [False, False, False]
	grey_count = 0
	width = camera.getWidth()
	height = camera.getHeight()
	chunk_pixels = width/3 * height/2
	for x in range(0,int(width/3)): #1st chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+= 1
			if red < 50  and green > 150 and blue < 50:
				grey_count+=1
	#print("white count chunk 1 "+str(white_count))
	print("grey count chunk 1 "+str(grey_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[0] = True
	if(grey_count > GREY_OBJECT_THRESHOLD):
		grey_list[0] = True
	white_count=0
	grey_count =0
	for x in range(int(width/3), int(2/3* width)): #2nd chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+=1
			if red < 50  and green > 150 and blue < 50:
				grey_count+=1
	#print("white count chunk 2 "+str(white_count))
	print("grey count chunk 2 "+str(grey_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[1] = True
	if(grey_count > GREY_OBJECT_THRESHOLD):
		grey_list[1] = True
	white_count=0
	grey_count =0
	for x in range(int(2/3* width),int(width)): #3rd chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+=1
			if red < 50  and green > 150 and blue < 50:
				grey_count+=1
	#print("white count chunk 3 "+str(white_count))
	print("grey count chunk 3 "+str(grey_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[2] = True	
	if(grey_count > GREY_OBJECT_THRESHOLD):
		grey_list[2] = True
	#print(white_list)
	print(grey_list)

	#can now program controller based off camera data
	if mode == 'snow_seeker':
		print('seeking snow')
		#Inverse kinematics
		#error
		"""rho = math.sqrt( (pose_y-target_y)**2  +  (pose_x-target_x)**2 )    
		alpha = math.atan2(target_y-pose_y, target_x -pose_x) - pose_theta
		pos_scalar = 2*rho   
		angular_scalar = 2*alpha		
		right_speed = pos_scalar / EPUCK_AXLE_DIAMETER - angular_scalar / EPUCK_AXLE_DIAMETER	
		left_speed = right_speed - angular_scalar / EPUCK_AXLE_DIAMETER """ 
		if white_list[1] == True:
			#drive toward snow
			pass
		elif white_list[0] == True:
			#turn left 
			pass
		elif white_list[2] == True:
			#turn right
			pass
		else:
			#spin ccw
			pass
		#map navigation
		if grey_list[1] == True and grey_list[0] == True:
			#wall, turn right
			right_speed = -MAX_SPEED
			left_speed = MAX_SPEED		
		else:
			#go straight
			right_speed = MAX_SPEED
			left_speed = MAX_SPEED
	if(abs(right_speed)>MAX_SPEED):
		right_speed=MAX_SPEED
	if(abs(left_speed)>MAX_SPEED):
		left_speed=MAX_SPEED
	leftMotor.setVelocity(left_speed)
	rightMotor.setVelocity(right_speed)

	#from lab 4
	vL = left_speed
	vR = right_speed	
	EPUCK_MAX_WHEEL_SPEED = 0.11695*TIME_STEP/1000.0 
	dsr=vR/MAX_SPEED*EPUCK_MAX_WHEEL_SPEED
	dsl=vL/MAX_SPEED*EPUCK_MAX_WHEEL_SPEED
	ds=(dsr+dsl)/2.0
	
	pose_y += ds*math.cos(pose_theta)
	pose_x += ds*math.sin(pose_theta)
	pose_theta += (dsr-dsl)/EPUCK_AXLE_DIAMETER
	print("X: %f Y: %f Theta: %f " % (pose_x,pose_y,pose_theta))
# Enter here exit cleanup code.
