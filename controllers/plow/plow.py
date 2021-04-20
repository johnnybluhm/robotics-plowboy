"""plow controller."""
from controller import Robot
from vehicle import Car, Driver

# create the Robot instance.
driver = Driver()

print(driver.getType())
camera = driver.getDevice("camera")

# get the time step of the current world
TIME_STEP = int(driver.getBasicTimeStep())
camera.enable(TIME_STEP)

MAX_SPEED = 10 #km/h?

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while driver.step() != -1:
	current_steer_angle = driver.getSteeringAngle()
	turn_angle = 0.17 #radians 

	if mode == 'manual':
		key = keyboard.getKey()
		while(keyboard.getKey() != -1): pass
		if key == keyboard.LEFT:
			new_angle = current_steer_angle - turn_angle
		elif key == keyboard.RIGHT:
			new_angle = current_steer_angle + turn_angle
		elif key == keyboard.UP:
			
		elif key == keyboard.DOWN:

		elif key == ord(' '):
			vL = 0
			vR = 0
  
	driver.setCruisingSpeed()	
	print(camera.getImage())
# Enter here exit cleanup code.