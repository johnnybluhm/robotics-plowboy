"""plow controller."""
from controller import Robot, Keyboard
from vehicle import Car, Driver

# create the Robot instance.
driver = Driver()
# get the time step of the current world
TIME_STEP = int(driver.getBasicTimeStep())
WHITE_OBJECT_THRESHOLD = 25 #white_count 
camera = driver.getDevice("camera")
camera.enable(TIME_STEP)
keyboard = driver.getKeyboard()
keyboard.enable(TIME_STEP) #can change sampling period here

driver.setAntifogLights(True)

speed = 0 #km/h?
#mode = 'manual'
mode = 'snow_seeker'

# - perform simulation steps until Webots is stopping the controller
while driver.step() != -1:

	steer_angle = driver.getSteeringAngle()
	turn_angle = 0.17 #	radians, turn 10 degrees each press


	if mode == 'manual':
		key = keyboard.getKey()
		while(keyboard.getKey() != -1): pass
		if key == keyboard.LEFT:
			steer_angle -= turn_angle
			if(steer_angle<= -0.631):
				steer_angle = -0.5				
		elif key == keyboard.RIGHT:
			steer_angle += turn_angle
			if(steer_angle>=0.631):
				steer_angle = 0.5
		elif key == keyboard.UP:
			speed+=0.5
			if speed >175:
				speed = 175
		elif key == keyboard.DOWN:
			speed-=0.5
			if speed <-50:
				speed = -50
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
			speed =2.5
		elif white_list[0] == True:
			#turn left 
			speed =2.5
			steer_angle -= turn_angle
			if(steer_angle<= -0.631):
				steer_angle = -0.5	
		elif white_list[2] == True:
			#turn right
			speed =2.5
			steer_angle += turn_angle
			if(steer_angle>=0.631):
				steer_angle = 0.5	
		else:
			speed = 0


	driver.setSteeringAngle(steer_angle)
	driver.setCruisingSpeed(speed)

# Enter here exit cleanup code.