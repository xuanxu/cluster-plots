import global_vars as glb

import numpy as np
import math
import lib_aux as la
import astropy.time as ap
import bottleneck as bn
from math import isnan
import ceflib
from copy import deepcopy

import time

# TK: This is needed, because, for some reason, django times out if numpy throws an exception or warning
np.seterr(all='print')


############################################################################################################################
def calc_range(data,axis_type,plot_type):
# Calculate the plot range in case of an auto-scaling
# remove the alpha% higher and lower values of the signal
#	-> alpha = 5% for spectro and 2% for 2D plots
# calculate the min (mini) and max (maxi) of the remaining points
#
# for 3D plots the range is:
#	min = mini
#	max = maxi
#
# for 2D plots:
# remove 10 higher and lower points for 2D plots with more than 100 points or 2 lower/higher if
# between 10 and 100 points
# calculate the min (mini) and max (maxi) of the remaining points#
# for a log scale:
# 	- for a spectro: we make sure that we have a "power of ten" included in the range as only them are labelled
# by IDL on the axis
#	- for a 2D plot: if the ratio max/min < 10 then we switch to a linear scale
    yrange = [1.,10.]

    if plot_type == 'line':
        #alpha = 0.02

        if axis_type == 'logarithmic':
            ind_finite = np.where(np.isfinite(np.log10(data)))[0]
        else:
            ind_finite = np.where(np.isfinite(data))[0]

        if ind_finite.any():
            data = data[ind_finite]
            count = len(ind_finite)
            data_sort = np.sort(data)
            #mini = data_sort[int(math.floor(alpha*count))]
            #maxi = data_sort[int(math.floor(count-alpha*count))]

            if count > 100:
                mini = data_sort[9]
                maxi = data_sort[count-10]
            elif count > 10:
                mini = data_sort[2]
                maxi = data_sort[count-3]
            else:
                mini = data_sort[0]
                maxi = data_sort[count-1]

            delta = abs(maxi-mini)
            if delta == 0:
                maxi += 1
                mini -= 1

            if axis_type == 'logarithmic':

                delta_log = np.log10(maxi) - np.log10(mini)
                mini_log = 10**(np.log10(mini)-0.4*delta_log)
                maxi_log = 10**(np.log10(maxi)+0.2*delta_log)

#                if ((mini != 0) and (maxi/mini) < 10.) or ((mini == 0) and (maxi < 1)) or ((maxi == 0) and (mini > -1)):
                    # swith scale to linear
#                    mini = mini
#                    maxi = maxi
#                    axis_type = 'linear'

 #               else:
                mini = mini_log
                maxi = maxi_log

            else:
                mini -= 0.2*delta
                maxi += 0.2*delta

            yrange = [mini,maxi]

    else:
        alpha = 0.05
        data = np.ravel(data)

        # ignore non-finite and zero values (zero can happen eg for RAPID count spectrograms)
        ind_finite = np.where(np.logical_and(np.isfinite(data),data > 0 ) )[0]

        if ind_finite.any():
            data = data[ind_finite]
            count = len(ind_finite)
            data_sort = np.sort(data)
            mini = data_sort[int(math.floor(alpha*count))]
            maxi = data_sort[int(math.floor(count-alpha*count))]
            yrange = [mini,maxi]

#    return yrange, axis_type
    return yrange




############################################################################################################################
############################################################################################################################
def create_json(sSubPanel,arrData):
    print("In lib_echarts")
    data_div = []
    panel_type = 'line'

    # get axis options (look for Y axis among the sPlot that has display set to 1)
    ylabel = ''
    zlabel = ''

    sPlot = sSubPanel['sPlot'][0]
    idx = [ind for (ind,d) in enumerate(sPlot['sAxis']) if d['display'] == 1 and d['type'] == "YAXIS"][0]

    if idx != -1:
        sYAxis = sPlot['sAxis'][idx]
        ylabel = sYAxis['label']+ '<br/>'  +sYAxis['unit']
        ytype = 'linear'
        if sYAxis['log'] == 1:
            ytype = 'logarithmic'


    num_series = sSubPanel['num_plots']
    order = sSubPanel['order']

    # get the data to plot
    flag_first_line = 1
    for (idx,elt) in [(ind,el) for (ind,el) in enumerate(sSubPanel['sPlot'])]:

        x_tag = [d['paramid'] for d in elt['sData'] if d['type'] == "X"][0]
        y_tag = [d['paramid'] for d in elt['sData'] if d['type'] == "Y"][0]

        x_data = [list(el['arrData']) for (ind,el) in enumerate(arrData) if el['paramid'] == x_tag][0]
        y_data = [list(el['arrData']) if el['arrData'].ndim > 0 else [el['arrData']] for (ind,el) in enumerate(arrData) if el['paramid'] == y_tag]

        flag_empty = 1
        if len(y_data) > 0:
            x_data = deepcopy(np.array(x_data))
            y_data = deepcopy(np.array(y_data[0]))
            if np.isfinite(y_data).any():
                flag_empty = 0

        print(flag_empty)
        if panel_type == 'line':
            if flag_empty == 0:
                # priority is given to heatmap info when overplotting line
                delta_t = [float(el['arrDeltaP'])+float(el['arrDeltaM']) for (ind,el) in enumerate(arrData) if el['paramid'] == x_tag][0]
                delta_y = [float(el['arrDeltaP'])+float(el['arrDeltaM']) for (ind,el) in enumerate(arrData) if el['paramid'] == y_tag][0]
                delta_y = np.array(np.where(np.isnan(np.asarray(delta_y,float)), None, delta_y))
            else:
                delta_t = 0
                delta_y = 0


        if elt['plot_type'] == 'line':

##########################
# LINE PLOT
##########################
            if panel_type == 'line':

                # calculate ranges
                if flag_empty == 0:
                    yrange_hc_tmp = [bn.nanmin(y_data),bn.nanmax(y_data)]
                else:
                    yrange_hc_tmp = [1e+31,-1e+31]

                if sYAxis['range'][0] == 0 and sYAxis['range'][1] == 0 :
                    #yrange,ytype = calc_range(y_data,ytype,elt['plot_type'])
                    yrange = calc_range(y_data,ytype,elt['plot_type'])
                else:
                    yrange = sYAxis['range']

                # multi-line plot
                if flag_first_line == 1:
                    yrange_hc = yrange_hc_tmp
                    yrange_plot = yrange
                    flag_first_line = 0
                else:
                    yrange_hc = [np.nanmin([yrange_hc[0],yrange_hc_tmp[0]]),np.nanmax([yrange_hc[1],yrange_hc_tmp[1]])]
                    if (yrange_plot[0] != 1. or yrange_plot[1] != 10.) and (yrange[0] != 1. or yrange[1] != 10.):
                        yrange_plot = [np.nanmin([yrange[0],yrange_plot[0]]),np.nanmax([yrange[1],yrange_plot[1]])]
                    elif yrange_plot == [1.,10.]:
                        yrange_plot = yrange

                # check if need to switch from log to lin
                # can't be done as part of the calc rang function because of multi-line series ?
                if idx == num_series-1:
                    mini = yrange_plot[0]
                    maxi = yrange_plot[1]
                    if ((mini != 0) and (maxi/mini) < 10.) or ((mini == 0) and (maxi < 1)) or ((maxi == 0) and (mini > -1)):
                        ytype = 'linear'

                # define "empty" spectro related data
                zrange = [0,0]
                ztype = ''

            # filter out negative values for log scale (or gighcharts crashes)
            if ytype == 'logarithmic':
               y_data = np.array(np.where(y_data <= 0, np.nan, y_data))

            # remove consecutive nans to reduce json size 
            nan_spots = np.where(np.isnan(y_data))
            diff = np.diff(nan_spots)[0]
            streaks = np.split(nan_spots[0], np.where(diff != 1)[0]+1)
            if len([len(streak) for streak in streaks if len(streak) > 2]) > 0:
                long_streaks = set(np.hstack([streak[1:] for streak in streaks if len(streak) > 2]))
                mask = [item not in long_streaks for item in range(len(y_data))]
            else:
                mask = np.full(len(y_data), True, dtype=bool)

            nonan_y_data = y_data[mask]
            nonan_x_data = x_data[mask]

            # to avoid echartss changing x axis boundaries add nan at beginning and end
            # TBD: what if y_data multi-dimensional ???
            if flag_empty == 0:
                if nonan_x_data[0] > glb.date_start_milli:
                    nonan_y_data = np.insert(nonan_y_data,0,np.nan,axis=0)
                    nonan_x_data = np.insert(nonan_x_data,0,glb.date_start_milli)
                if nonan_x_data[-1] < glb.date_stop_milli:
                    nonan_y_data = np.insert(nonan_y_data,len(nonan_y_data),np.nan,axis=0)
                    nonan_x_data = np.insert(nonan_x_data,len(nonan_x_data),glb.date_stop_milli)
            else:
                # empty plot
                nonan_x_data = [glb.date_start_milli,glb.date_stop_milli]
                nonan_y_data = [np.nan,np.nan]

            # replace Nan with None for javascript
            nonan_y_data = np.array(np.where(np.isnan(nonan_y_data), None, nonan_y_data))

            # convert time vector to unix time for echarts time axis
            x_plot = ap.Time([(ceflib.milli_to_isotime(x,3)) for x in nonan_x_data], format='isot', scale='utc')
            x_epoch = np.array(x_plot.unix)*1000

            # reshape data for echartss => [[x,y],[x,y],...]
            data_hc = np.column_stack((x_epoch,nonan_y_data))

            color_hc = (elt['sLine'])['color']
            serie_title = (elt['sLine'])['name']
            print("add serie")
            data_div.append({'data': data_hc, 'color':color_hc, 'name':serie_title, 'type': (elt['sLine'])['type'],'thick':(elt['sLine'])['thick'],'legend':(elt['sLine'])['legend']})


##########################
# SPECTRO
##########################

        else: # spectrogram
            panel_type = 'heatmap'


            idx = [ind for (ind,d) in enumerate(sPlot['sAxis']) if d['display'] == 1 and d['type'] == "ZAXIS"][0]
            if idx != -1:
                sZAxis = sPlot['sAxis'][idx]
                zlabel = sZAxis['label']+ '<br/>' +sZAxis['unit']
                ztype = 'linear'
                if sZAxis['log'] == 1:
                    ztype = 'logarithmic'


            z_tag = [d['paramid'] for d in elt['sData'] if d['type'] == "Z"][0]
            z_data = deepcopy(np.array([list(el['arrData']) for (ind,el) in enumerate(arrData) if el['paramid'] == z_tag][0]))

            # get/calculate y and z ranges
            if sYAxis['range'][0] == 0 and sYAxis['range'][1] == 0 :
                yrange = [bn.nanmin(y_data),bn.nanmax(y_data)]
            else:
                yrange = sYAxis['range']

            if ytype == 'logarithmic':
                yrange_plot = [np.log10(yrange[0]),np.log10(yrange[1])]
            else:
                yrange_plot = yrange

            yrange_hc = yrange

            if ztype == 'logarithmic':
                dims = z_data.shape
                z_data_tmp = np.ravel(z_data)

                idx_zero = np.where(z_data_tmp == 0)[0]

		# (remove warning when comparing data to nan)
                with np.errstate(invalid='ignore'):
                    # remove negative values for log scale
                    z_data_tmp = np.array(np.where(z_data_tmp < 0., np.nan, z_data_tmp))
            else:
                z_data_tmp = z_data

            if sZAxis['range'][0] == 0. and sZAxis['range'][1] == 0. :
                zrange = calc_range(z_data_tmp,ztype,elt['plot_type'])
            else:
                zrange = sZAxis['range']

            if ztype == 'logarithmic':
                # put a fill val for zeroes. They will then be plotted in black by echartss (different from white nan)
                z_data_tmp = np.array(np.where(z_data_tmp == 0., 1e-31, z_data_tmp))

                # reshape z_data
                z_data = np.reshape(z_data_tmp,dims)

            #if len(x_data) <= 1:
            if len(z_data) <= 1:
                # empty plot
                nonan_x_data = [glb.date_start_milli,glb.date_stop_milli]
                nonan_z_data = np.empty((2,len(y_data)))
                nonan_z_data[:] = np.nan
                #x_data = [glb.date_start_milli,glb.date_stop_milli]
                #z_data = np.empty((2,len(y_data)))
                #z_data[:] = np.nan
            else:
                # remove records that are not only fill values
                mask = ~np.all(np.isnan(z_data),axis=1)

                nonan_z_data = z_data[mask,:]
                nonan_x_data = x_data[mask]

                # to avoid echartss changing x axis boundaries add nan at beginning and end of the time interval
                delta_t = [el['arrDeltaP'] for (ind,el) in enumerate(arrData) if el['paramid'] == x_tag][0]
                if nonan_x_data[0] > glb.date_start_milli+delta_t/2:
                    print("add start null")
                    nonan_z_data = np.insert(nonan_z_data,0,np.nan,axis=0)
                    nonan_x_data = np.insert(nonan_x_data,0,glb.date_start_milli+delta_t/2)
                    #z_data = np.insert(z_data,0,np.nan,axis=0)
                    #x_data = np.insert(x_data,0,glb.date_start_milli+delta_t/2)
                if nonan_x_data[-1] < glb.date_stop_milli-delta_t/2:
                    nonan_z_data = np.insert(nonan_z_data,len(nonan_z_data),np.nan,axis=0)
                    nonan_x_data = np.insert(nonan_x_data,len(nonan_x_data),glb.date_stop_milli-delta_t/2)
                    #z_data = np.insert(z_data,len(z_data),np.nan,axis=0)
                    #x_data = np.insert(x_data,len(x_data),glb.date_stop_milli-delta_t/2)


            # replace Nan with None for javascript
            nonan_z_data = np.array(np.where(np.isnan(nonan_z_data), None, nonan_z_data))
            #z_data = np.array(np.where(np.isnan(z_data), None, z_data))
            y_data = np.array(np.where(np.isnan(y_data), None, y_data))

            # convert time vector to unix time for echarts time axis
            x_plot = ap.Time([(ceflib.milli_to_isotime(x,3)) for x in nonan_x_data], format='isot', scale='utc')
            #x_plot = ap.Time([(ceflib.milli_to_isotime(x,3)) for x in x_data], format='isot', scale='utc')
            x_epoch = np.ndarray.tolist(np.array(x_plot.unix)*1000)

            # reshape data for echartss => [[x,y,z]]
            data_hc = np.column_stack((np.repeat(x_epoch,len(y_data)),np.tile(y_data,len(nonan_x_data)),np.ravel(nonan_z_data)))
            #data_hc = np.column_stack((np.repeat(x_epoch,len(y_data)),np.tile(y_data,len(x_data)),np.ravel(z_data)))

            print("add spectro")
            data_div.append({'data': data_hc, 'type': 'heatmap'})


        # make sure the ranges have some valid values 
        # (eg if we zoom on a range with no data yrange_hc is set to [NaN,NaN] and the ajax call fails)
        if np.isnan(yrange_hc[0]):
            yrange_hc = [1,10]
        if np.isnan(yrange_plot[0]):
            yrange_plot = [1,10]
        if np.isnan(yrange[0]):
            yrange = [1,10]
        if np.isnan(zrange[0]):
            zrange = [1,10]
       
    return {'order': order, 'size': sSubPanel['rel_size'], 'type': panel_type,  'ytitle': ylabel, 'rotate':sYAxis['rotate'], 'ytickflag':sYAxis['tick_flag'], 'ytickval':sYAxis['tick_val'], 'yticktxt':sYAxis['tick_label'], 'ztitle': zlabel, 'yrange': yrange, 'yrange_caa': yrange_plot, 'yrange_hc': yrange_hc, 'zrange': zrange, 'ytype':ytype, 'ztype':ztype, 'delta_x':delta_t, 'delta_y': delta_y, 'plot': data_div}
 

