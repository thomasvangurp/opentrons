# To standardize movement tetsing while implementing concurrency for compute

from opentrons import robot
from collections import namedtuple
import sys
import time


DEFAULT_PORT = "/dev/tty.usbmodem1421"
command = namedtuple('command', 'action code')

test_command = (command('MOVE', 'G0'),command('GET_TARGET', 'M114.4'))

ONE_LINE_COMMANDS = (command('MOVE', 'G0'),
			command('SET_ZERO', 'G28.3'),
			command('GET_POSITION', 'M114.2'),
			command('GET_TARGET', 'M114.4'),
			command('GET_ENDSTOPS', 'M119'),
			command('CALM_DOWN', 'M999'),
			command('SET_SPEED', 'M203.1'),
			command('DWELL', 'G4'),
			command('SET_ACCELERATION', 'M204'),
			command('MOTORS_ON', 'M17'),
			command('MOTORS_OFF', 'M18'),
			command('AXIS_AMPERAGE', 'M907'),
			command('STEPS_PER_MM', 'M92'),
			command('POP_SPEED', 'M121'),
			command('ABSOLUTE_POSITIONING', 'G90'),
			command('RELATIVE_POSITIONING', 'G91'),
			command('POP_SPEED', 'M121')
	)

COMMANDS = (command('MOVE', 'G0'),
			command('version', 'version'),
			command('SET_ZERO', 'G28.3'),
			command('GET_POSITION', 'M114.2'),
			command('GET_TARGET', 'M114.4'),
			command('GET_ENDSTOPS', 'M119'),
			command('HALT', 'M112'),
			command('CALM_DOWN', 'M999'),
			command('SET_SPEED', 'M203.1'),
			command('DWELL', 'G4'),
			command('SET_ACCELERATION', 'M204'),
			command('MOTORS_ON', 'M17'),
			command('MOTORS_OFF', 'M18'),
			command('AXIS_AMPERAGE', 'M907'),
			command('STEPS_PER_MM', 'M92'),
			command('POP_SPEED', 'M121'),
			command('ABSOLUTE_POSITIONING', 'G90'),
			command('RELATIVE_POSITIONING', 'G91'),
			command('POP_SPEED', 'M121'),
			command('CONFIG_VERSION_GET', 'cat /sd/config')
		)

OTHER_COMMANDS = (command('RESET', 'reset'), #Turns off the board
				command('HOME', 'G28.2'), #Need motors since it's looking for switches
				command('OT_VERSION', 'ot_version') #Does not actually interact with serial connection

	)

#NOTE: Check for discrepencies between Unix and windows newlines

#@profile
def write_and_sleepRead(command):
	serial_device = robot._driver.connection.device()
	command_string = ("%s\n" % command).encode('utf-8')
	print("CODE: %s" % command_string)
	write_serial(serial_device, command_string)
	response = sleepRead_serial(serial_device)
	return response
#@profile
def write_serial(serial_device, command_string):
	bytes_written = serial_device.write(command_string)
	serial_device.flush() #flush() should wait until the write completes
	if not bytes_written == len(command_string):
		print("ERROR: command '%s' is of length %d while %d bytes were written to the serial device\n" % 
			(command_string, len(command_string), bytes_written)) 
#@profile
def sleepRead_serial(serial_device):
	return serial_device.readall()
#@profile
def write_and_blockRead(command):
	serial_device = robot._driver.connection.device()
	command_string = ("%s\n" % command).encode('utf-8')
	print("CODE: %s" % command_string)
	write_serial(serial_device, command_string)
	response = blockRead_serial()
	return response
#@profile
def blockRead_serial():
	response = robot._driver.readline_from_serial()
	return response

#@profile
def test_block_and_sleep():
	for command in ONE_LINE_COMMANDS:
		print("SLEEP ACTION: %s" % command.action)
		response = write_and_sleepRead(command.code)
		print("SLEEP RESPONSE: %s\n" % response)

		print("BLOCK ACTION: %s" % command.action)
		response = write_and_blockRead(command.code)
		print("BLOCK RESPONSE: %s\n" % response)


def main():
	if len(sys.argv) > 1:
		test = sys.argv[1]
		serial_port = sys.argv[2]
	else:
		print ("USAGE: movement_testing -testing_method [-sb for block/sleep | -sm for standard movement]  serial port [serial_port_path]")
		exit(0) 

	robot.connect(serial_port)
	while robot.is_simulating():
		time.sleep(.1)
	if test == '-sb':
	    test_block_and_sleep()
	elif test == '-sm':
		standard_move_cycle()


def standard_move_cycle():
	for X in range(50, 100, 10):
		for Y in range(50, 100, 10):
			for Z in range(0,40,10):
				robot.move_head(x=X, z=Z)
				print("moving to %d:%d" % (X,Z))




if __name__ == "__main__":
	main()
	




