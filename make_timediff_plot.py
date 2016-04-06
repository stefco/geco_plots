#!/usr/bin/env python

import os
import subprocess
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import collections

bit_rate = 16

# exit if no arguments
if len(sys.argv) == 1:
    print 'Not enough arguments.'
    print 'For a input format type \'make_timediff_plot.py -h\''
    exit(1)

if sys.argv[1] == '-h':
    print 'python make_timediff_plot.py \'start date\' \'end date\''
    print 'Enter dates as Month Day, Year hh:mm:ss'
    exit()
else:
    start = sys.argv[1]
    end = sys.argv[2]

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
    print('converting times')
    return int(os.popen("lalapps_tconvert " + tstr).read())

# make list of times that correspond to the necessary frame files
def make_times_list(s_time , e_time):
    print('making list of times')
    gps_start = tconvert(s_time)
    gps_end = tconvert(e_time)
    startn = int(gps_start) / 64
    if int(gps_end) % 64 == 0:
        endn = (gps_end / 64) - 1
    else:
        endn = int(gps_end) / 64
    return [64 * i for i in range(startn, endn + 1)]
    print 'made a times array'

def make_plot(x_axis, y_axis):
    print('making plots')
    plt.plot(x_axis, y_axis)
    plt.xlabel('GPS Time')
    plt.ylabel('Offset')
    plt.title('Time difference from ' + start + ' until ' + end)
    plt.savefig('Time difference from ' + start + ' until ' + end + '.png')

def main(start_time, end_time):
    num_seconds = (len(make_times_list(start_time , end_time))) * 64
    time_series = np.zeros(num_seconds * bit_rate)
    t = np.zeros(num_seconds * bit_rate)
    n_skip = 0
    current_pos = 0
    for time in make_times_list(start_time, end_time):
        path = str(time) + ".dat"
        if os.path.exists(path):
	    # replaces 0s in time_series and t with values of the time
	    # series at that position
	    with open(path,'r') as infile:
                time_series[current_pos : current_pos + (64 * bit_rate)] = \
                    np.fromstring(remove_header_and_text(infile.read()) , sep= ',')
                t[current_pos : current_pos +(64 * bit_rate)] = \
                    np.linspace(start = time, stop = time + 64, num = 64 * bit_rate, 
                    endpoint = False)
                current_pos += 64 * bit_rate
        else:
            print('file ' + path + ' not found.')
            n_skip += 64 * bit_rate
    time_series = time_series[: len(time_series) - n_skip]
    t = t[:len(t) - n_skip]
    make_plot(t, time_series)

main(start, end)
