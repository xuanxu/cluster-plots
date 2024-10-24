import global_vars as glb
#import matplotlib.pyplot as plt

import numpy as np
import lib_aux as la
import astropy.time as ap

def plot_data(sPlot,arrData,pos):
    if sPlot['plot_type'] == "line plot":
        plot_line(sPlot,arrData,pos)


def plot_line(sPlot,arrData,pos):

    # get line plotting options
    color = sPlot['sLine']['color'] if sPlot['sLine']['color'] else ":k"
    symbol = sPlot['sLine']['symbol'] if sPlot['sLine']['symbol'] else "-"
    format = color+symbol

    # get axis options
    sYAxis = [d for d in sPlot['sAxis'] if d['type'] == "YAXIS"][0]
    ylabel = sYAxis['label']+'\n'+sYAxis['unit']

    # get the data to plot
    x_tag = [d['paramid'] for d in sPlot['sData'] if d['type'] == "X"][0]
    y_tag = [d['paramid'] for d in sPlot['sData'] if d['type'] == "Y"][0]

    x = np.array([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == x_tag])[0]
    y = np.array([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == y_tag])[0]

    # convert x to julian day for proper labels
    x_jul = ap.Time(x, format='mjd')

    # limit the number of ticks on y axis
    plt.locator_params(axis = 'y', nbins = 4)

    # create plot
    ax = plt.subplot(pos)
    plt.ylabel(ylabel, multialignment='center')

    plt.plot_date(x_jul.plot_date, y, format)

    # don't plot x axis labels yet
    ax.set_xticklabels([])

    # if this is the upper plot print the time interval as a title
    if pos[-1] == '1':
        plt.title(glb.date_start_iso+" / "+glb.date_stop_iso, multialignment='center')
