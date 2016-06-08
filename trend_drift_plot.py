#!/usr/bin/env python

import os
import subprocess
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

##This does not 
valid_trend_extensions = ['min', 'max', 'mean', 'rms']
micros_per_second = 1000000

parser = argparse.ArgumentParser()
parser.add_argument('-l',help='[REQUIRED] the location of the trend data being'\
     +'used')
parser.add_argument('-f', help='[REQUIRED] specifies whether to use the'\
    +'of best fit (with \'lobf\') or the mean of the trend (with \'constant\'' \
    +') to find the residual. the former might be used for a cesium clock, '\
    +'and the latter for the GPS clock.')
parser.add_argument('-t', help='the trend, i.e. min, mean, or max. Default is '\
    +'mean')
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
<<<<<<< HEAD
=======
            print current_stat
>>>>>>> f6846746fd731f660ccc082143b27c17ad5237bc
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
    for i in valid_trend_extensions:
<<<<<<< HEAD
        if set(statistics[i]['times']) == set(statistics['mean']['times']):
            pass
        else:
            print i
            print('All trends must include the same set of times')
            exit()
=======
        print i
        print statistics[i]['times']
        print statistics[i]['trend']
>>>>>>> f6846746fd731f660ccc082143b27c17ad5237bc
    return statistics

def tconvert(tstr=""):
    return os.popen("lalapps_tconvert " + tstr).read()

def make_plot(statistics_dictionary):
    stat = statistics_dictionary
    #converts all trend data from seconds to microseconds
    for extension in valid_trend_extensions:
        stat[extension]['trend'] = [i * micros_per_second for i in\
            stat[extension]['trend']]
    if vars(args)['f'] == 'lobf':
        fitted_function_description = 'line of best fit'
        #creates array with slope and y-intercept of line of best fit of the mean
        lobf_array = np.polyfit(stat['mean']['times'], stat['mean']['trend'], 1)
        #dimensionless quantity that characterizes drift
        notable_quantity = 'Drift coefficient'
        notable_quantity_value = lobf_array[0]/micros_per_second
        fitted_function = np.poly1d(lobf_array)(stat['mean']['times'])
        #creates array with the difference between line of best fit and mean value
        tmp = [lobf_array[0] * i for i in stat['mean']['times']]
        tmp += lobf_array[1]
        tmp -= stat['mean']['trend']
        mean_dif = tmp
        tmp = [lobf_array[0] * i for i in stat['max']['times']]
        tmp += lobf_array[1]
        tmp -= stat['mean']['trend']
        max_dif = tmp
        tmp = [lobf_array[0] * i for i in stat['min']['times']]
        tmp += lobf_array[1]
        tmp -= stat['min']['trend']
        min_dif = tmp
<<<<<<< HEAD
    elif vars(args)['f'] == 'constant':
        fitted_function_description = 'average'
        notable_quantity = 'Average value'
=======
        
    elif fitted_function_description == 'constant':
        drift_coef = 0
>>>>>>> f6846746fd731f660ccc082143b27c17ad5237bc
        average_value = sum(stat['mean']['trend'])/float(len(stat['mean']['trend']))
        notable_quantity_value = average_value
        fitted_function = np.poly1d(average_value)(stat['mean']['trend'])
        mean_dif = np.subtract(stat['mean']['trend'],fitted_function)
        max_dif = np.subtract(stat['max']['trend'],fitted_function)
        min_dif = np.subtract(stat['min']['trend'],fitted_function)
    else:
        print('You must specify either "lobf" or "constant" with "-f" flag')
        exit()
<<<<<<< HEAD
    ordered_max_time, ordered_max_trend = zip(*sorted(zip(stat['max']['time'\
        +'s'],stat['max']['trend'])))
    ordered_min_time, ordered_min_trend = zip(*sorted(zip(stat['min']['time'\
        +'s'],stat['min']['trend'])))
    ordered_mean_time, ordered_mean_trend = zip(*sorted(zip(stat['mean']['time'\
        +'s'],stat['mean']['trend'])))
    ordered_rms_time, ordered_rms_trend = zip(*sorted(zip(stat['rms']['time'\
        +'s'],stat['rms']['trend'])))
    rms_sqaured = [i**2 for i in ordered_rms_trend]
    mean_squared = [ i**2 for i in ordered_mean_trend]
    mean_variance_array = np.subtract(rms_sqaured,mean_squared)
    mean_std_dev_array = [i**0.5 for i in mean_variance_array]
=======
    
    mean_std_dev_array = [i-np.mean(mean_dif) for i in mean_dif]/np.std(mean_dif)
>>>>>>> f6846746fd731f660ccc082143b27c17ad5237bc
    print 'making plots'
    fig = plt.figure(figsize=(13,18))
    plt.suptitle('Characterization of diagnostic timing system 1PPS signal, '\
                 + str(location), fontsize = 20)
    plt.subplots_adjust(top=0.88888888, bottom=0.1)
    ax1 = plt.subplot2grid((5,2),(0,0), colspan=2)
<<<<<<< HEAD
    ax1.set_title(fitted_function_description+' versus mean offset')
    ax1.plot(stat['mean']['times'], stat['mean']['trend'], 'blue', label = 'Me'\
        +'an minute trend')
    ax1.plot(stat['mean']['times'], fitted_function, '#000000', label = \
        fitted_function_description)
    ax1.fill_between(ordered_max_time, ordered_max_trend, ordered_min_trend\
        ,alpha = 0.25, label='min/max range')
    ax1.set_xlabel('GPS time')
    ax1.set_ylabel('Offset [$\mu$s]')
    ax1.text(0.01, 0.05, notable_quantity+'='+str(notable_quantity_value), \
        transform=ax1.transAxes, bbox=dict(facecolor='#99ccff',\
        boxstyle='round', alpha=0.25))
    ax1.legend(loc='best', fancybox=True, framealpha=0.5)
    ax3 = plt.subplot2grid((5,2), (2,0))
    n, bins, patches = plt.hist(mean_dif, 20, facecolor='blue')
    ax3.set_xlabel('$\Delta$t [$\mu$s]')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Histogram of deviations')
    ax2 = plt.subplot2grid((5,2), (1,0))
    ax2.plot(stat['mean']['times'], mean_dif, 'blue')
    ax2.set_xlabel('GPS time')
    ax2.set_title('Deviation of mean trend from '+fitted_function_description)
    ax2.set_ylabel('Deviation [$\mu$s]')
    ax4 = plt.subplot2grid((5,2),(3,0), colspan=2)
    ax4.plot(stat['max']['times'], max_dif, 'red', label='Positive')
    ax4.plot(stat['min']['times'], min_dif, 'green', label='Negative')
    ax4.legend(loc='best', fancybox=True, framealpha=0.5)
    ax4.set_xlabel('GPS time')
    ax4.set_ylabel('Deviation [$\mu$s]')
    ax4.set_title('Maximum deviation from the '+fitted_function_description)
    #Comment theses lines back to add a plot with only the mean trend
    ##ax5 = plt.subplot2grid((5,2),(3,1))
    ##ax5.plot(stat['mean']['times'], stat['mean']['trend'], label = '')
    ##ax5.legend(loc='best', fancybox=True, framealpha=0.5)
    ##ax5.set_xlabel('GPS time [s]')
    ##ax5.set_ylabel('Offset [$\mu$s]')
    ax6 = plt.subplot2grid((5,2), (4,0))
    n, bins, patches = plt.hist(min_dif, 20, facecolor='green')
    ax6.set_xlabel('$\Delta$t [$\mu$s]')
    ax6.set_ylabel('Frequency')
    ax6.set_title('Deviation of min from '+fitted_function_description)
    ax7 = plt.subplot2grid((5,2), (4,1))
    n, bins, patches = plt.hist(max_dif, 20, facecolor='red')
    ax7.set_xlabel('$\Delta$t [$\mu$s]')
    ax7.set_ylabel('Frequency')
    ax7.set_title('Deviation of max from '+fitted_function_description)
    ax8 = plt.subplot2grid((5,2), (1,1))
    ax8.plot(ordered_mean_time, mean_std_dev_array, '#00ffff')
    ax8.set_xlabel('GPS time')
    ax8.set_ylabel('Standard deviation')
    ax8.set_title('Standard deviation')
    ax9 = plt.subplot2grid((5,2), (2,1))
    n, bins, patches = plt.hist(mean_std_dev_array, 20, facecolor='#00FFFF')
    ax9.set_title('Histogram of standard deviations')
    ax9.set_xlabel('Standard deviation')
    ax9.set_ylabel('Frequency')
    print(notable_quantity_value)
=======
    ax1.set_title('Line of best fit versus offset')
    ax1.plot(stat['mean']['times'], stat['mean']['trend'], '#ff0000')
    ax1.plot(stat['mean']['times'], fitted_function, '#617d8d')
    ax1.fill_between(stat['max']['times'], min_dif, max_dif, alpha = 0.5)
    ax1.set_xlabel('GPS time')
    ax1.set_ylabel('Offset [$\mu$s]')
    ax3 = plt.subplot2grid((5,2), (1,0))
    n, bins, patches = plt.hist(mean_dif, 20, facecolor = '#139a0e')
    ax3.set_xlabel('$\Delta$t [$\mu$s]')
    ax3.set_ylabel('Frequency')
    ax3.set_title('histogram of the residual')
    ax2 = plt.subplot2grid((5,2), (1,1))
    ax2.plot(stat['mean']['times'], mean_dif)
    ax2.set_xlabel('GPS time [s]')
    ax2.set_title('Residual of the line of best fit')
    ax2.set_ylabel('Difference [$\mu$s]')
    ax4 = plt.subplot2grid((5,2),(0,0))
    ##ax4.plot(
    print drift_coef
>>>>>>> f6846746fd731f660ccc082143b27c17ad5237bc
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1)
    plt.subplots_adjust(left=0.1, right=0.95, top=0.92, bottom=0.05)
    fig.savefig('charicterization_of_diagnostic_timing_system_from_'+tconvert(\
        str(int(stat['mean']['times'][0]))).replace(" ", "_").replace("_GMT",""\
        )+'_until_'+tconvert(str(int(stat['mean']['times'][-1]))).replace(" ","\
        _").replace("_GMT","")+'.png', dpi=300)

def main():
    values = make_time_series()
    make_plot(values)

main()
