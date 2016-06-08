#!/usr/bin/env python

import os
import subprocess
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

fitted_function_description = 'lobf'
valid_trend_extensions = ['min', 'max', 'mean', 'n', 'rms']
micros_per_second = 1000000

parser = argparse.ArgumentParser()
parser.add_argument('-l', help='the location of the trend data being used')
parser.add_argument('-t', help='the trend, i.e. min, mean, or max. Default is mean')
parser.add_argument('-f', help='Allows you to specify whether to use the line'\
    +' of best fit (with \'lobf\') or the mean of the trend (with \'constant' \
    +'\') to find the residual. the former might be used for a cesium clock,'\
    +' and the latter for the GPS clock.')
args = parser.parse_args()
location = vars(args)['l']
if vars(args)['t'] == None:
    trend = 'mean'
else:
    trend = vars(args)['t']

#Takes input from geco_trend_dump and makes an array of times and corresponding
#trend values for that time
def make_time_series():
    statistics = {}
    for trend_extension in valid_trend_extensions:
        statistics[trend_extension] = {}
        statistics[trend_extension]['times'] = []
        statistics[trend_extension]['trend'] = []
    current_stat = statistics['mean']
    for line in sys.stdin:
        #reads each line of the stdin from geco_trend_dump. for each line, the
        #try, except loop makes sure the line contains only numbers. It then
        #checks that each line has 2 entries, and that the data does not look
        #anonymous
        if line.replace("\n","") in valid_trend_extensions:
            current_stat = statistics[line.replace("\n","")]
        try:
            values = [float(x) for x in line.split('\t')]
            if len(values) == 2:
                if values[1] == 0:
                    print('It seems that the signal was off during some pa'
                          'rt of ' + str(values[0]))
                elif abs(values[1]) * micros_per_second < .01:
                    print('The data at ' + str(values[0]) + ' is anomalous'
                          'ly small.')
                elif abs(values[1]) * micros_per_second > 4:
                    print('The data at ' + str(values[0]) + ' is anomalously la'
                          'rge.')
                else:
                    current_stat['times'].append(values[0])
                    current_stat['trend'].append(values[1])
            else:
                print line
        except ValueError:
            pass
    return statistics


def make_plot(statistics_dictionary):
    stat = statistics_dictionary
    fitted_function_description = vars(args)['f']
    #converts all trend data from seconds to microseconds
    for extension in valid_trend_extensions:
        stat[extension]['trend'] = [i * micros_per_second for i in\
            stat[extension]['trend']]
    if fitted_function_description == 'lobf':
        fitted_function_description = 'line of best fit'
        #creates array with slope and y-intercept of line of best fit of the mean
        lobf_array = np.polyfit(stat['mean']['times'], stat['mean']['trend'], 1)
        #dimensionless quantity that characterizes drift
        drift_coef = lobf_array[0]/micros_per_second
        fitted_function = np.poly1d(lobf_array)(stat['mean']['times'])
        #creates array with the difference between line of best fit and mean value
        tmp = [lobf_array[0] * i for i in stat['mean']['times']]
        tmp += lobf_array[1]
        tmp -= stat['mean']['trend']
        mean_dif = tmp
        tmp = [lobf_array[0] * i for i in stat['max']['times']]
        tmp += lobf_array[1]
        tmp -= stat['max']['trend']
        max_dif = tmp
        tmp = [lobf_array[0] * i for i in stat['min']['times']]
        tmp += lobf_array[1]
        tmp -= stat['min']['trend']
        min_dif = tmp
    elif fitted_function_description == 'constant':
        fitted_function_description = 'average value of mean trend'
        drift_coef = 0
        average_value = sum(stat['mean']['trend'])/float(len(stat['mean']['trend']))
        fitted_function = np.poly1d(average_value)(stat['mean']['trend'])
        mean_dif = np.subtract(stat['mean']['trend'],fitted_function)
        max_dif = np.subtract(stat['max']['trend'],fitted_function)
        min_dif = np.subtract(stat['min']['trend'],fitted_function)
    mean_std_dev_array = [i-np.mean(mean_dif) for i in mean_dif]/np.std(mean_dif)
    ##else:
        ##print('You must specify either "lobf" or "constant" with with "-f" flag')
    print 'making plots'
    fig = plt.figure(figsize=(13,18))
    plt.suptitle('Characterization of diagnostic timing system 1PPS system, '\
                 + str(location))
    plt.subplots_adjust(top=0.88888888, bottom=0.1)
    ax1 = plt.subplot2grid((5,2),(0,0), colspan=2)
    ax1.set_title('Line of best fit versus mean offset')
    ax1.plot(stat['mean']['times'], stat['mean']['trend'], '#ff0000')
    ax1.plot(stat['mean']['times'], fitted_function, '#617d8d')
    ax1.fill_between(stat['max']['times'], stat['max']['trend'] ,stat['min']\
        ['trend'] , alpha = 0.5)
    ax1.set_xlabel('GPS time')
    ax1.set_ylabel('Offset [$\mu$s]')
    ax3 = plt.subplot2grid((5,2), (2,1))
    n, bins, patches = plt.hist(mean_dif, 20, facecolor = '#139a0e')
    ax3.set_xlabel('$\Delta$t [$\mu$s]')
    ax3.set_ylabel('Frequency')
    ax3.set_title('histogram of the residual')
    ax2 = plt.subplot2grid((5,2), (2,0))
    ax2.plot(stat['mean']['times'], mean_dif)
    ax2.set_xlabel('GPS time [s]')
    ax2.set_title('Residual of the line of best fit and the mean')
    ax2.set_ylabel('Difference [$\mu$s]')
    ax4 = plt.subplot2grid((5,2),(1,1))
    ax4.plot(stat['max']['times'], max_dif, label='Line of best fit versus max offset')
    ax4.plot(stat['min']['times'], min_dif, label='Line of best fit versus min offset')
    ax4.legend(loc='best', fancybox=True, framealpha=0.5)
    ax4.set_xlabel('GPS time')
    ax5 = plt.subplot2grid((5,2),(1,0))
    ax5.plot(stat['mean']['times'], stat['mean']['trend'], label = '')
    ax5.legend(loc='best', fancybox=True, framealpha=0.5)
    ax5.set_xlabel('GPS time [s]')
    ax5.set_ylabel('Offset [$\mu$s]')
    ax6 = plt.subplot2grid((5,2), (3,0))
    n, bins, patches = plt.hist(min_dif, 20)
    ax6.set_xlabel('$\Delta$t [$\mu$s]')
    ax6.set_ylabel('Frequency')
    ax6.set_title('Histogram of the residual the line of best fit and min')
    ax7 = plt.subplot2grid((5,2), (3,1))
    n, bins, patches = plt.hist(max_dif, 20)
    ax7.set_xlabel('$\Delta$t [$\mu$s]')
    ax7.set_ylabel('Frequency')
    ax7.set_title('Histogram of the residual from the line of best fit and max')
    ax8 = plt.subplot2grid((5,2), (4,0))
    ax8.plot(stat['mean']['times'], mean_std_dev_array)
    ax9 = plt.subplot2grid((5,2), (4,1))
    n, bins, patches = plt.hist(max_dif, 20)
    ax9.set_title('Histogram of standard deviations')
    print drift_coef
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1)
    plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)
    fig.savefig('FILENAME.png')

def main():
    values = make_time_series()
    make_plot(values)

main()
