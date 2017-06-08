#!/bin/bash
#arg1 is outfile name - must end in .prof, arg2 is the serial port for the connection

python3 -m cProfile -o ${1} movement_testing.py ${2}
snakeviz ${1}
