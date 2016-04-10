#_!/usr/bin/env python

import os
import subprocess
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import collections

bit_rate = 16
second_to_micros = 1000000
arg_n = len(sys.argv)

#exit if no arguments
if arg_n == 1:
    print 'Not enough arguments.'
    print 'For a input format type \'make_timediff_plot.py -h\''
    exit(1)

elif sys.argv[1] == '-h':
    print 'python make_timediff_plot.py \'start date\' \'end date\' [input_directory]'
    print 'Enter dates as Month Day, Year hh:mm:ss'
    print 'If you do not specifiy an input directory the program will look for'
    print ' files in the current directory'
    exit()

else:
    start = sys.argv[1]
    end = sys.argv[2]
    channel = sys.argv[3]

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

#lalapps to convert times to GPS time
def tconvert(tstr=""):
    return int(os.popen("lalapps_tconvert " + tstr).read())

#make list of times that correspond to the necessary frame files
def make_times_list(s_time , e_time):
    gps_start = tconvert(s_time)
    gps_end = tconvert(e_time)
    startn = int(gps_start) / 64
    if int(gps_end) % 64 == 0:
        endn = (gps_end / 64) - 1
    else:
        endn = int(gps_end) / 64
    return [64 * i for i in range(startn, endn + 1)]

#Makes arrays of min max and mean of each frame file is_data_good approves
def min_max_mean(s_time, e_time):
    good_indeces = is_data_good(s_time, e_time)
    t = make_times_list(s_time, e_time)
    print len(good_indeces)
    time_array = np.zeros(len(t))
    min_array = np.zeros(len(t))
    max_array = np.zeros(len(t))
    mean_array = np.zeros(len(t))
    n_skip = 0
    current_pos = 0
    for i in range(0, len(t)):
        if good_indeces[i] == 0:
            t[i] = 0
    for time in t:
        path = make_path_name(time)
        if os.path.exists(path):
            with open(path,'r') as infile:
                infile_array = np.fromstring(remove_header_and_text(infile.read()) , sep= ',')
                min_array[current_pos] = min(infile_array)
                max_array[current_pos] = max(infile_array)
                mean_array[current_pos] = np.mean(infile_array)
                time_array[current_pos] = time
                current_pos += 1
        else:
            n_skip += 1
    min_array = min_array[:len(min_array) - n_skip]
    max_array = max_array[:len(max_array) - n_skip]
    mean_array = mean_array[:len(mean_array) - n_skip]
    time_array = time_array[:len(time_array) - n_skip]
    return (time_array, min_array, max_array, mean_array)

#Defines the pa  th where the file is from input
def make_path_name(file_name):
    if arg_n == 3:
        path = str(file_name) + '.dat'
    elif arg_n  == 4:
        path = channel + '/' + str(file_name) + ".dat"
    return path

#Creates an array whose vallues are 0 or 1 depending on if the corresponding
#frame file has reasonable data. This roundabout method is used because using
#the convention found in other section of this code gives an array with times
#in scientific notation, which cannot then be used to specify a path name
#This is done to avoid these outliers affecting lobf calculations
def is_data_good(start_time, end_time):
    current_pos = 0
    n_skip = 0
    good_files = np.zeros(len(make_times_list(start_time, end_time)))
    for time in make_times_list(start_time, end_time):
        #TODO maybe make these next three lines a seperate function
        path =  make_path_name(time)
        if os.path.exists(path):
            with open(path, 'r') as infile:
                infile_array = np.fromstring(remove_header_and_text(infile.read()) \
                    , sep = ',')
                if np.mean(infile_array) < 0:
                    lower_lim = abs(max(infile_array))
                    upper_lim = abs(min(infile_array))
                elif np.mean(infile_array) > 0:
                    lower_lim = min(infile_array)
                    upper_lim = max(infile_array)
                elif np.mean(infile_array) == 0:
                    print 'It seems there was no signal at ' + str(time)
                if lower_lim * second_to_micros > 0.01 and upper_lim * \
                    second_to_micros < 4:
                    good_files[current_pos] = 1
                    current_pos += 1
                elif lower_lim * second_to_micros < 0.01:
                    print 'Signal at ' + str(time) + ' is anomalously small'
                    current_pos += 1
                elif upper_lim * second_to_micros > 4:
                    print 'Signal at ' + str(time) + ' is anomalously large'
                    current_pos += 1
    return good_files

def make_timediff_plot(x_axis, y_axis):
    print('making plots')
    print len(y_axis)
    y_axis = y_axis * second_to_micros
    mmavg = min_max_mean(start, end)
    # Creates an array for a line of best fit from the mean of each frame file
    lobf_array = np.polyfit(mmavg[0], mmavg[3], 1)
    x_axis_lobf = mmavg[0]
    y_axis_lobf = np.poly1d(lobf_array)(x_axis_lobf) * second_to_micros
    #Makes an array of the difference between the y-axis and the line of best
    #fit at that point
    tmp = lobf_array[0] * second_to_micros * x_axis
    tmp += lobf_array[1] * second_to_micros
    tmp -= y_axis
    y_dif = tmp
    print len(y_axis)
    #plots the data and a line of best fit on the same graph
    plt.figure(1)
    plt.subplot(211)
    plt.plot(x_axis, y_axis, '#ff0000', x_axis_lobf, y_axis_lobf, '#617d8d')
    #TODO add a legend in the upper right corner to display the slop of the line of best fit
    plt.xlabel('GPS Time')
    plt.ylabel('Offset [$\mu$s]')
    plt.title('Time difference from ' + start + ' until ' + end)
    #makes histogram of the difference between data and line of best fit
    plt.subplot(212)
    n, bins, patches = plt.hist(y_dif, 20, facecolor = '#139a0e')
    plt.xlabel('Time difference [$\mu$s]')
    plt.savefig('Time difference from ' + start + ' until ' + end + '.png')

#returns a duple whose elements are the gps times and the corresponding file
#value from the input file
def time_timeseries(start_time, end_time):
    num_seconds = (len(make_times_list(start_time , end_time))) * 64
    time_series = np.zeros(num_seconds * bit_rate)
    t = np.zeros(num_seconds * bit_rate)
    n_skip = 0
    current_pos = 0
    for time in make_times_list(start_time, end_time):
        path = make_path_name(time)
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
            print('file ' + str(time) + ' not found.')
            n_skip += 64 * bit_rate
    time_series = time_series[: len(time_series) - n_skip]
    t = t[:len(t) - n_skip]
    return (t, time_series)

def main(start_time, end_time):
    t = time_timeseries(start_time, end_time)[0]
    time_series = time_timeseries(start_time, end_time)[1]
    make_timediff_plot(t, time_series)

main(start, end)
