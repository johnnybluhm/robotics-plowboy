"""plow controller."""
from controller import Robot, Keyboard
from vehicle import Car, Driver

# create the Robot instance.
driver = Driver()
# get the time step of the current world
TIME_STEP = int(driver.getBasicTimeStep())

camera = driver.getDevice("camera")
camera.enable(TIME_STEP)
keyboard = driver.getKeyboard()
keyboard.enable(TIME_STEP)




speed = 10 #km/h?
mode = 'manual'
# Main loop:
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
				print(steer_angle)
				steer_angle = -0.5
				print("steer_angle after "+str(steer_angle))
		elif key == keyboard.RIGHT:
			steer_angle += turn_angle
			if(steer_angle>=0.631):
				steer_angle = 0.5
		elif key == keyboard.UP:
			speed+=10
			if speed >175:
				speed = 175
		elif key == keyboard.DOWN:
			speed-=10
			if speed <-50:
				speed = -50
		elif key == ord(' '):
			speed = 0
	driver.setSteeringAngle(steer_angle)
	driver.setCruisingSpeed(speed)	
	#print(camera.getImage())
# Enter here exit cleanup code.