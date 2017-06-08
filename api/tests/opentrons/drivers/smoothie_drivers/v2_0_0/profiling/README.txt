Currently profiling the v2 driver to understand the source of latency in robot movement when running on the raspberryPi zero. Making simple documentation for the process for future reference.

Tools used: cProfile, snakeviz, line_profiler

line_profiler - https://github.com/rkern/line_profiler:
Tool from Robert Kern which allows you to place a @profile decorator above a function and see line by line profiling of a function.
Can be run using `kernprof -l -v movement_testing.py`

cProfile - (in stdlib):
Gives a breakdown of the latency in the program and does not require source code modification. 
Can be run using `python -m cProfile -o program.prof my_program.py` where the output file, `program.prof` will be used with snakeviz

snakeviz - (https://jiffyclub.github.io/snakeviz/#snakeviz):
Tool used for visualizing the output of cProfile. 
Run with `snakeviz output_from_cProfile.prof`


Where to start:
cProfile together with snakeviz is good for either very high level or lower level understandings. Since it doesn't require decorators it is good when you are not sure what you're looking for.
The line_profiler is a more granular but still digestable profiler. It gives line by line understanding without as much noise. This is probably the best tool for actually identifying the specific line that is causing problems. Only then, if you need to descend further, should you switch back to cProfile and snakeviz since it will descend into the lower level operations like built-int methods.


