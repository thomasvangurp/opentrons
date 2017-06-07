# To standardize movement tetsing while implementing concurrency for compute

from opentrons import robot
from collections import namedtuple


DEFAULT_PORT = "/dev/tty.usbmodem1421"
command = namedtuple('command', 'action code')


COMMANDS = (command('move', 'G0'), command('version', 'version'))




#NOTE: Check for discrepencies between Unix and windows newlines
def write_and_read(command):
	serial_device = robot._driver.connection.device()
	command_string = ("%s\n" % command).encode('utf-8')
	
	print("CODE: %s" % command_string)
	bytes_written = serial_device.write(command_string)
	serial_device.flush() #flush() should wait until the write completes
	if not bytes_written == len(command_string):
		print("ERROR: command '%s' is of length %d while %d bytes were written to the serial device\n" % 
			(command_string, len(command_string), bytes_written)) 
	return serial_device.readall()






if __name__ == "__main__":
	robot.connect(DEFAULT_PORT)
	for command in COMMANDS:
		print("ACTION: %s" % command.action)
		response = write_and_read(command.code)
		print("RESPONSE: %s\n" % response)