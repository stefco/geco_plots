#!/usr/bin/env python

import os
import subprocess
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

micros_per_second = 1000000

parser = argparse.ArgumentParser()
parser.add_argument('-l', help='the location of the trend data being used')
parser.add_argument('-t', help='the trend, i.e. min, mean, or max. Default it mean')
args = parser.parse_args()
location = vars(args)['l']
if vars(args)['t'] == None:
    trend = 'Mean'
else:
    trend = vars(args)['t']

#Takes input from geco_trend_dump and makes an array of times and corresponding
#trend values for that time
def make_time_series():
    times = []
    trend = []
    for line in sys.stdin:
        #reads each line of the stdin from geco_trend_dump. for each line, the
        #try, except loop makes sure the line contains only numbers. It then
        #checks that each line has 2 entries, and that the data does not look
        #anonymous
        try:
            values = [float(x) for x in line.split('\t')]
            if len(values) == 2:
                if values[1] == 0:
                    print 'It seems that the signal was off during some part o'\
                        'f ' + str(i[0])
                elif abs(values[1]) * micros_per_second < .01:
                    print 'The data at ' + str(values[0]) + ' is anomalously s'\
                        'mall.'
                elif abs(values[1]) * micros_per_second > 4:
                    print 'The data at ' + str(values[0]) + ' is anomalously l'\
                        'arge.'
                else:
                    times.append(values[0])
                    trend.append(values[1])
            else:
                print line
        except ValueError:
            pass
    return (times, trend)

def make_plot(x_axis, y_axis):
    #converts y_axis time to microseconds from seconds
    y_axis = [i * micros_per_second for i in y_axis]
    #creates array with slope and y-intercept of line of best fit
    lobf_array = np.polyfit(x_axis, y_axis, 1)
    #dimensionless quantity that characterizes drift
    drift_coef = lobf_array[0]/micros_per_second
    y_axis_lobf = np.poly1d(lobf_array)(x_axis)
    tmp = [lobf_array[0] * i for i in x_axis]
    tmp += lobf_array[1]
    tmp -= y_axis
    y_dif = tmp
    print 'making plots'
    fig = plt.figure(figsize=(6.5,9))
    plt.suptitle('Characterization of diagnostic timing system 1PPS system, '+location)
    plt.subplots_adjust(top=0.88888888, bottom=0.1)
    ax1 = fig.add_subplot(311)
    ax1.set_title('Line of best fit versus offset')
    ax1.plot(x_axis, y_axis, '#ff0000')
    ax1.plot(x_axis, y_axis_lobf, '#617d8d')
    ax1.set_xlabel('GPS time')
    ax1.set_ylabel('Offset [$\mu$s]')
    ax3 = fig.add_subplot(313)
    n, bins, patches = plt.hist(y_dif, 20, facecolor = '#139a0e')
    ax3.set_xlabel('$\Delta$t [$\mu$s]')
    ax3.set_ylabel('Frequency')
    ax3.set_title('histogram of the residual')
    ax2 = fig.add_subplot(312)
    ax2.plot(x_axis, y_dif)
    ax2.set_xlabel('GPS time [s]')
    ax2.set_title('Residual of the line of best fit')
    ax2.set_ylabel('Difference [$\mu$s]')
    print drift_coef
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1)
    plt.subplots_adjust(left=0.2, right=0.8, top=0.9, bottom=0.1)
    fig.savefig('FILENAME.png')

def main():
    values = make_time_series()
    make_plot(values[0], values[1])

main()
