import os
import subprocess
import math
import sys
import matplotlib as plt

# exit if no arguments
if len(sys.argv) == 1:
    print 'Not enough arguments.'
    print 'For a input format type \'make_plot.py\' -h'
    exit(1)

if sys.argv[1] == '-h':
    print 'python make_timediff_plot.py \'[start date]\' \'[end date]\''
    print 'Enter dates as Month Day, Year hh:mm:ss'
    exit()
else:
    start_time = sys.argv[1]
    end_time = sys.argv[2]

# remove the first 6 lines and the string "Data: "
def remove_header_and_text(string):
    return remove_lines(string, 6).translate(None, 'Dat: ')

# remove the first n lines. python sux, bash rulez
def remove_lines(string, num_lines):
    i = 0
    n = 0
    l = len(string)
    while n < num_lines:
        i = string.find('\n', i+1)
        # if a newline isn't found, this means there are no new lines left.
        if i == -1:
            return ""
        # if the string ends on a newline, return empty string.
        elif i+1 == l:
            return ""
        n += 1
    return string[i+1:]

# lalapps to convert times to GPS time
def tconvert(tstr=""):
    return int(os.popen("lalapps_tconvert " + tstr).read())

# make list of times that correspond to the necessary frame files
def make_times_list(start_time , end_time):
    startn = int(tconvert(start_time) / 64)
    if end % 64 == 0:
        endn = ((tconvert(end_time) / 64) - 1)
    else:
        endn = int(tconvert(end_time) / 64)
    times = [64 * i for i in range(startn, endn + 1)]

def make_plot(x_axis, y_axis):
    plt.plot(x_axis, y_axis)
    plt.xlabel('GPS Time')
    plt.ylabel('Offset')
    plt.title('Time difference from ' + start_time + ' until ' + end_time)
    plt.savefig('Time difference from ' + start_time + 'until ' + end_time + '.png')

def main(start_time, end_time):
    for time in make_times_list(start_time, end_time):
        path = time + ".dat"
        if os.path.exists(path):
            # set up the processes for acquiring and processing the data
            with open(path,'r') as infile:
                data_string = remove_header_and_text(infile.read())
            # append arrays to existing timeseries and times
            x += [float(x) for x in data_string.split(',')]
            t += [time + dt/16 for dt in range(1024)]
    make_plot(x, t)
        # FIXME you should handle the case where the file doesn't exist


