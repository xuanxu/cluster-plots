
import make_param as mkp
import numpy as np
import global_vars as glb
#from astropy.time import Time
import astropy.time as ap
import ceflib as cef
import math
from copy import deepcopy


##############################################################################################################
def find_gaps(sPlotTime, min_gap_length):
    print("in find_gaps")
    time = sPlotTime['arrData']

    # convert second gap time to millisecond to match julian days
    min_gap_length *= 1000

    # calculate the time difference between each points
    time_diff = np.diff(time)

    # find the indexes of the gaps
    gap_ind = [ind for ind in range(len(time_diff)) if time_diff[ind] > min_gap_length]

    if len(gap_ind) > 0:
        print(len(gap_ind)," gap founds - insert nans")
    else:
        print("no gaps found")

    new_length = len(time) + len(gap_ind)

    # find nan and not nan indices
    nan_ind = [gap_ind[ind] + ind + 1 for ind in range(len(gap_ind))]
    not_nan_ind = [ind for ind in range(new_length) if ind not in nan_ind]

    # create new time
    new_time = np.empty(new_length)
    new_time[not_nan_ind] = time
    new_time[nan_ind] = [new_time[ind - 1] + (new_time[ind + 1] - new_time[ind - 1]) / 2 for ind in nan_ind]

    # keep ind of nan and not nan if needed by other panel
    #name,did = sPlotTime['paramid'].split("__")
    sNan = mkp.make_sParameter()
    sNan['arrData'] = nan_ind
    sNan['arrDeltaP'] = not_nan_ind
    #sNan['paramid'] = "nan__" + did
    sNan['paramid'] = "nan__" + sPlotTime['paramid']

    return (new_time, sNan)



##############################################################################################################
def calc_jultime(sTime,paramid):

    delta_min = ((sTime['arrDeltaM']).astype(float) * 1000)
    delta_max = ((sTime['arrDeltaP']).astype(float) * 1000)

    int_time_min = sTime['arrData'] - delta_min
    int_time_max = sTime['arrData'] + delta_max

    sJulTime = mkp.make_sParameter()
    sJulTime['arrData'] = sTime['arrData']
    sJulTime['arrDeltaM'] = np.array(int_time_min)
    sJulTime['arrDeltaP'] = np.array(int_time_max)
    sJulTime['paramid'] = paramid

    return sJulTime


##############################################################################################################
def calc_jultime_range(sTime,paramid):

    if len(sTime['arrData']) == 0:
        int_time_min = [np.nan]
        int_time_max = [np.nan]
    else:
        int_time_min = ((sTime['arrData'][:,0]).astype(float))
        int_time_max = ((sTime['arrData'][:,1]).astype(float))

    sJulTime = mkp.make_sParameter()
    sJulTime['arrData'] = sTime['arrData']
    sJulTime['arrDeltaM'] = np.array(int_time_min)
    sJulTime['arrDeltaP'] = np.array(int_time_max)
    sJulTime['paramid'] = paramid

    return sJulTime

##############################################################################################################
def calc_plottime(sJulTime,arrData,sProc,paramid,proc_type):

    # calculate the number of points to plot
    #***************************************
    # The number of points to plot is limited by different parameters:
    # We don't plot more than 1400/1000 (average/minmax) points which is approximately the number of pixels for the plot (time axis)
    # However we want to keep the time resolution lower than the one of the file (MIN_TIME_RESOLUTION)

    # The metadata information gives the min and max time resolution of the dataset
    # from which we can determine the number of points to plot


    # number of records is the length of the time vector
    num_data = len(sJulTime['arrData'])

    if proc_type == "minmax":
        num_data_max = glb.NUM_DATA_MINMAX
    elif proc_type == "none":
        num_data_max = num_data
    else:
        num_data_max = glb.NUM_DATA_AVERAGE

    # calculate time range in seconds and delta_t (plot resolution)
    period = math.ceil(glb.date_stop_milli - glb.date_start_milli)
    delta_t = (period/num_data_max)

    # check what the plot resolution should be
    # if -1 use the min of metadata resolutions
    # if 0 use the max of metadata resolutions
    # if 86400 keep the maximum number of points (NUM_DATA_AVERAGE) whatever the time interval and force the averaging
    # else use the resolution given in the xml (if the resolution is negative use it independently of the min/max time res)
    # this is given by the value item of the processing struct
    plot_res = float(sProc['value'])
    name,datasetid = sJulTime['paramid'].split("__")

    if proc_type != 'caveat' and  plot_res >= -1:
        max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
        min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])

    flag_fixed = 0

    if plot_res == -1:
        res = min(max_res,min_res)
    elif plot_res == 0:
        res = max(max_res,min_res)
    elif plot_res < -1:
        res = 0-float(plot_res)
        flag_fixed = 1
    elif plot_res == 86400:
        flag_fixed = 1
        res = delta_t/1000.
    else:
        res = float(plot_res)

    # res in milliseconds
    res *= 1000.

    flag_proc = 0

    if proc_type == "spec_average" :
        # for spectros always do average to use the time delta_plus/delta_minus
        flag_fixed = 1
        # don't go below 500 points
        if (delta_t < res) :
            num_data_max = max([math.ceil(period/res)+1,500])
            delta_t = period/float(num_data_max+1)
    else:
        # we need a round number of points even if we use the dataset time resolution
        if ( (delta_t < res) or (flag_fixed == 1) ):
            num_data_max = max([math.ceil(period/res)+1,1])
            delta_t = period/float(num_data_max+1)

    if proc_type == "average" or proc_type == "interpolate" or proc_type == "spec_average" or proc_type == "caveat":
        if ( num_data > num_data_max or flag_fixed == 1 ):
            print("Too many points: perform reduction")
            vect_time_plot = [x*delta_t+glb.date_start_milli for x in range(int(math.floor(num_data_max)))]
            flag_proc = 1
        else:   # no averaging
            vect_time_plot = sJulTime['arrData']
            
    elif proc_type == "none":
        vect_time_plot = sJulTime['arrData']
    else:
        if ( num_data > num_data_max and flag_fixed == 0 ):
            vect_time_plot = [((2*x+1)*delta_t/4)+glb.date_start_milli for x in range(int(math.floor(2*num_data_max)))]
            flag_proc = 1
        else:   # no minmax
            vect_time_plot = sJulTime['arrData']

    print('delta_t:',delta_t)
    print('num_data_max:',num_data_max)
    print('flag_proc:',flag_proc)

    sPlotTime = mkp.make_sParameter()
    #sPlotTime['arrData'][:] = vect_time_plot
    sPlotTime['arrData'] = vect_time_plot
    sPlotTime['arrDeltaP'] = delta_t
    sPlotTime['arrDeltaM'] = 0
    sPlotTime['paramid'] = paramid

    # use the support holder to store the flag_proc -> do we need to process the data or insert NaNs
    sPlotTime['support'] = flag_proc

    return sPlotTime


##############################################################################################################
def get_time(sProc,lParam,arrData,type):

    # INPUT_1 is the time vector
    # OUTPUT_1 is the time vector in julian days
    # OUTPUT_2 is the time vector used for the plot -> reduced number of points

    # extract the time list from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    # check if outputs already exist in memory otherwise process them
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        sJulTime = calc_jultime(sTime,output_1)
        arrData.append(deepcopy(sJulTime))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1
    else:
        idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "OUTPUT_1"), -1)
        input_1 = sProc['sArgument'][idx_input]['paramid']
        sJulTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == output_1][0]


    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:
        sPlotTime = calc_plottime(sJulTime,arrData,sProc,output_2,type)
        arrData.append(deepcopy(sPlotTime))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0

##############################################################################################################
def get_time_range(sProc,lParam,arrData):

    # INPUT_1 is the time range vector
    # OUTPUT_1 is the start/stop times vector in julian days
    # OUTPUT_2 is the time vector used for the plot -> reduced number of points

    # extract the time list from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    # check if outputs already exist in memory otherwise process them
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        sJulTime = calc_jultime_range(sTime,output_1)
        arrData.append(deepcopy(sJulTime))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1
    else:
        idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "OUTPUT_1"), -1)
        input_1 = sProc['sArgument'][idx_input]['paramid']
        sJulTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == output_1][0]


    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:
        sPlotTime = calc_plottime(sJulTime,arrData,sProc,output_2,'caveat')
        arrData.append(deepcopy(sPlotTime))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1


    return 0

