"""plow_epuck controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot

# create the Robot instance.
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())
WHITE_OBJECT_THRESHOLD = 25 #white_count 
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

# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:

	if mode == 'manual':
		key = keyboard.getKey()
		while(keyboard.getKey() != -1): pass
		if key == keyboard.LEFT:
			right_speed =+1
		elif key == keyboard.RIGHT:
			left_speed+=1
		elif key == keyboard.UP:
			left_speed+=1
			right_speed+=1
		elif key == keyboard.DOWN:
			left_speed-=1
			right_speed-=1
		elif key == ord(' '):
			speed = 0	

	#processing camera data

	image = camera.getImageArray()
	white_list = [False, False, False]
	white_count = 0
	width = camera.getWidth()
	height = camera.getHeight()
	chunk_pixels = width/3 * height/2
	for x in range(0,int(width/3)): #1st chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+=1
	print("white count chunk 1 "+str(white_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[0] = True
	white_count=0
	for x in range(int(width/3), int(2/3* width)): #2nd chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+=1
	print("white count chunk 2 "+str(white_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[1] = True
	white_count=0
	for x in range(int(2/3* width),int(width)): #3rd chunk of image
		for y in range(0,int(height)): #only need bottom half of image
			red   = image[x][y][0]
			green = image[x][y][1]
			blue  = image[x][y][2]
			if red > 200 and green > 200 and blue > 200:
				white_count+=1
	print("white count chunk 3 "+str(white_count))
	if(white_count > WHITE_OBJECT_THRESHOLD):
		white_list[2] = True	

	print(white_list)

	#can now program controller based off camera data
	if mode == 'snow_seeker':		
		if white_list[1] == True:
			#drive toward snow
			left_speed =1
			right_speed=1
		elif white_list[0] == True:
			#turn left 
			right_speed =+1	
		elif white_list[2] == True:
			#turn right
			left_speed +=1	
		else:
			#spin ccw
			left_speed =1
			right_speed -=1

	leftMotor.setVelocity(left_speed)
	rightMotor.setVelocity(right_speed)

# Enter here exit cleanup code.
