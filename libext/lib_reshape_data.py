import make_param as mkp
import numpy as np
import astropy.time as ap
import global_vars as glb
import math
import lib_time as lt
import lib_aux as la
import bottleneck as bn
import ceflib
from copy import deepcopy

#np.warnings.filterwarnings('ignore')

import warnings
warnings.filterwarnings("ignore", "Mean of empty slice")
#warnings.filterwarnings('ignore')





##############################################################################################################
##############################################################################################################

# insert_nans
# insert_nan_dboundary
# ext_comp
# process_2D
# average_2D
# interpolate_2D
# minmax_2D
# none_2D
# filt_dim
# av_dim
# nrj_to_log
# resh_nrj
# reso_nrj
# filter_fixed_nrj
# interpolate_fixed_nrj
# interpolate_3D
# average_3D
# process_3D
# merge_data
# merge_2d
# total_power
# distance
# cluster_distance
# calc_angle
# zero_to_nan
# calc_modulo
# calc_itp_complex
# calc_itp
# param_average
# convert_pef
# edi_code
# edi_bitmask
# efw_bitmask
# rap_int_time
# rap_hv
# get_caveat
# sta_extract_mode
# sta_mode_change
# filter_mode

##############################################################################################################
##############################################################################################################



##############################################################################################################
def insert_nans(val, sNaN):
    # insert nans in the data to show the gaps
    print("in insert_nans")
    nan_ind = sNaN['arrData']
    not_nan_ind = sNaN['arrDeltaP']

    new_length = len(nan_ind)+len(not_nan_ind)
    new_val = -1 * np.ones(new_length)
    if len(not_nan_ind) > 0:
        new_val[not_nan_ind] = val
    if len(nan_ind) > 0 :
        new_val[nan_ind] = np.nan

    return new_val


##############################################################################################################
def insert_nan_dboundary(sProc,lParam,arrData):
    # insert nan at "day boundary" (when data jumps between 0 and 24) to avoid interpolation (MLT panel)

    # INPUT_1 is time vector

    # INPUT_2 is the data vector

    # OUTPUT_1 is the new time vector

    # OUTPUT_2 is the new data vector


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:

        num_data = len(sData['arrData'])

        time = sData['arrData']
        data = sData2['arrData']
        date_time = [ceflib.milli_to_isotime(t,0) for t in time]

        if (num_data > 1 ):
            # calculate the time difference between each points
            time_diff = np.diff(data)

            # find the indexes of the gaps
            # because of the prior averaging can't look for too big of a jump
            # set to 10 hours
            gap_ind = [ind for ind in range(len(time_diff)) if abs(time_diff[ind]) > 10]

            # remove averaged points between 2 consecutive gaps
            if len(gap_ind) > 1:
                double_gap = np.diff(gap_ind+[gap_ind[-1]])
                for i in [ind for ind in range(len(double_gap)) if double_gap[ind] == 1]:
                    x = gap_ind[i]
                    data[x+1] = np.nan 

            new_length = len(time) + len(gap_ind)

            # find nan and not nan indices
            nan_ind = [gap_ind[ind] + ind + 1 for ind in range(len(gap_ind))]
            not_nan_ind = [ind for ind in range(new_length) if ind not in nan_ind]

            # create new time
            new_time = np.empty(new_length)
            new_time[not_nan_ind] = time
            new_time[nan_ind] = [ time[ind] + (time[ind+1] - time[ind])/2.  for ind in gap_ind]

            # create new data
            new_data = np.empty(new_length)
            new_data[not_nan_ind] = data
            new_data[nan_ind] = np.nan 
        else:
            new_time = time
            new_data = data

        


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = new_time
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = new_data
        sDataPlot['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0





##############################################################################################################
def ext_comp(sProc,lParam,arrData,type):
    # Extract the desired component from a multi-dimensional parameter

    # INPUT_1 is the multi_comp data
    # INPUT_2 is the param from which to extract the component (if INPUT_1 == INPUT_2 the comp to extract is not a dependency)
    # VALUE is the idx of the component to extract

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sFilter = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        idx_comp = la.str_to_num(int(sProc['value']))

        data = sData['arrData']
        num_dim = len(data.shape)

        if num_dim == 3: # spectro
            if input_1 == input_2: # comp to extract is not a DEPEND (STA CS x,y,z)
                new_data = np.squeeze(data[:,:,idx_comp])
            else:
                dim = sData['arrDepend'].index(sFilter['paramid'])
                if dim == 1:
                    new_data = np.squeeze(data[:,idx_comp,:])
                elif dim == 2:
                    new_data = np.squeeze(data[:,:,idx_comp])
                else:
                    print("ERROR: ext_comp function doesn't deal with this array dim")
        elif num_dim == 2: # 2D
            new_data = np.squeeze(data[:,idx_comp])
        elif num_dim == 1: # empty array ?
            new_data = data
        else:
            print("ERROR: ext_comp function doesn't deal with this array shape")

        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = new_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

##############################################################################################################
def process_2D(sProc,lParam,arrData,proc_type):
    # for 2D plots if there are more than NUM_DATA_MAX points we reduce
    # the number of points using one of the following methods:
    #   - min/max
    #   - average
    #   - interpolation

    # INPUT_1 is the data to process
    # INPUT_2 is the data time vector (julian time)
    # INPUT_3 is the plot time vector


    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # extract the time lists from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sJulTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sPlotTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        if proc_type == "average":
            sDataPlot = average_2D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        elif proc_type == "interpolate":
            sDataPlot = interpolate_2D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        elif proc_type == "minmax":
            sDataPlot = minmax_2D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        elif proc_type == "none":
            sDataPlot = none_2D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        else:
            print("unknown 2D process type " + proc_type + " / use average")
            sDataPlot = average_2D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)

        arrData.append(deepcopy(sDataPlot))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0

##############################################################################################################
def average_2D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):
    # for 2D plots if there are more than NUM_DATA_MAX points we plot for each 'pixel'
    # the average of the data for the corresponding time interval

    delta_t = sPlotTime['arrDeltaP']
    int_time_min = sJulTime['arrDeltaM']
    int_time_max = sJulTime['arrDeltaP']
    num_point = len(sPlotTime['arrData'])
    num_record = len(sData['arrData'])
    sDataPlot = mkp.make_sParameter()
    flag_proc = sPlotTime['support']

    # initialisation final arrays
    av_data = np.empty(num_point)
    av_data.fill(np.nan)
 
    nan_id = "nan__" + sPlotTime['paramid']

    # check if the data need to be processed
    if flag_proc == 1: 
       # fill in array
        #for i in range(int(glb.NUM_DATA_AVERAGE)):
         for i in range(num_point):
            time_min = i*delta_t - delta_t/2 + glb.date_start_milli
            time_max = i*delta_t + delta_t/2 + glb.date_start_milli

            idx_val_time = np.squeeze(np.logical_and(int_time_min <= time_max , int_time_max > time_min))

            if idx_val_time.any() :
                av_data[i] = bn.nanmean(sData['arrData'][idx_val_time])

    else:
        # we dont' average the data
        # but we look for "long" gaps and insert nans so that they show on the plot
        # the sProc value gives the minimum size for a gap
        print("too few points, no averaging")

        if num_point > 1:
            # check if we already know the position of the gaps else find them
            if not [d['paramid'] for d in lParam if d['paramid'] == nan_id]:
                (new_time, sNaN) = lt.find_gaps(sPlotTime,float(sProc['value']))
                sPlotTime['arrData'] = deepcopy(new_time)
                # add sNaN to the list of parameters
                arrData.append(deepcopy(sNaN))
                pTime = [el for (ind,el) in enumerate(lParam) if el['paramid'] == sPlotTime['paramid']][0]
                last_idx = pTime['last_idx']
                idx_list = pTime['idx_list']
                lParam.append({'paramid':nan_id,'last_idx':last_idx,'idx_list':idx_list,'in_cef':0,'cef':'','in_memory':1})
            else:
                sNaN = [el for (ind,el) in enumerate(arrData) if el['paramid'] == nan_id][0]

            av_data = insert_nans(sData['arrData'],sNaN)
        else:
            av_data = sData['arrData']

    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = av_data
    sDataPlot['paramid'] = outputid

    return sDataPlot



##############################################################################################################
def interpolate_2D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):
    # for 2D plots if there are more than NUM_DATA_MAX points we interpolate
    # the data on each 'pixel'

    delta_t = sPlotTime['arrDeltaP']
    int_time_min = sJulTime['arrDeltaM']
    int_time_max = sJulTime['arrDeltaP']
    num_point = len(sPlotTime['arrData'])
    num_record = len(sData['arrData'])
    sDataPlot = mkp.make_sParameter()



    # we look for "long" gaps and insert nans so that they show on the plot
    # the sProc value gives the minimum size for a gap

    # check if we already know the position of the gaps else find them
    nan_id = "nan__" + sPlotTime['paramid']
    if not [d['paramid'] for d in lParam if d['paramid'] == nan_id]:
        (new_time, sNaN) = lt.find_gaps(sJulTime,float(sProc['value']))
        sPlotTime['arrData'] = deepcopy(new_time)
        # add sNaN to the list of parameters
        arrData.append(deepcopy(sNaN))
        pTime = [el for (ind,el) in enumerate(lParam) if el['paramid'] == sPlotTime['paramid']][0]
        last_idx = pTime['last_idx']
        idx_list = pTime['idx_list']
        lParam.append({'paramid':nan_id,'last_idx':last_idx,'idx_list':idx_list,'in_cef':0,'cef':'','in_memory':1})
    else:
        sNaN = [el for (ind,el) in enumerate(arrData) if el['paramid'] == nan_id][0]

    itp_data = insert_nans(sData['arrData'],sNaN)

    if num_record > glb.NUM_DATA_AVERAGE:
        itp_data = np.interp(sPlotTime['arrData'],sJulTime['arrData'],sData['arrData'])


    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = itp_data
    sDataPlot['paramid'] = outputid

    return sDataPlot






##############################################################################################################
def minmax_2D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):
    # for 2D plots if there are more than NUM_DATA_MAX points we plot for each 'pixel'
    # the min and max of the data for the corresponding time interval

    delta_t = sPlotTime['arrDeltaP']
    int_time_min = sJulTime['arrDeltaM']
    int_time_max = sJulTime['arrDeltaP']
    num_point = len(sPlotTime['arrData'])
    num_record = len(sData['arrData'])
    flag_proc = sPlotTime['support']
    # initialisation final arrays
    mm_data = np.empty(num_point)
    mm_data.fill(np.nan)

    nan_id = "nan__" + sPlotTime['paramid']

    # check if the data need to be processed (number of records greater than NUM_DATA_MINMAX)
    if flag_proc == 1:
        # fill in array
        #for i in range(int(glb.NUM_DATA_MINMAX)):
         for i in range(int(num_point/2)):
            time_min = i*delta_t - delta_t/2 + glb.date_start_milli
            time_max = i*delta_t + delta_t/2 + glb.date_start_milli

            idx_val_time = np.logical_and(int_time_min <= time_max , int_time_max > time_min)

            if idx_val_time.any() :
                mm_data[2*i] = min(sData['arrData'][idx_val_time])
                mm_data[2*i+1] = max(sData['arrData'][idx_val_time])


    else:
        # we dont' do min/max on the data
        # but we look for "long" gaps and insert nans so that they show on the plot
        # the sProc value gives the minimum size for a gap

        # check if we already know the position of the gaps else find them
        if not [d['paramid'] for d in lParam if d['paramid'] == nan_id]:
            (new_time, sNaN) = lt.find_gaps(sPlotTime,float(sProc['value']))
            sPlotTime['arrData'] = deepcopy(new_time)
            # add sNaN to the list of parameters
            arrData.append(deepcopy(sNaN))
            pTime = [el for (ind,el) in enumerate(lParam) if el['paramid'] == sPlotTime['paramid']][0]
            last_idx = pTime['last_idx']
            idx_list = pTime['idx_list']
            lParam.append({'paramid':nan_id,'last_idx':last_idx,'idx_list':idx_list,'in_cef':0,'cef':'','in_memory':1})
        else:
            sNaN = [el for (ind,el) in enumerate(arrData) if el['paramid'] == nan_id][0]

        mm_data = insert_nans(sData['arrData'],sNaN)

    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = deepcopy(mm_data)
    sDataPlot['paramid'] = outputid


    return sDataPlot

##############################################################################################################
def none_2D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):
    # for 2D plots if we want to keep the initial data (no averaging or min/max)
    # we still want to insert nans to show gaps greater than "value"

    num_point = len(sPlotTime['arrData'])
    sDataPlot = mkp.make_sParameter()

    nan_id = "nan__" + sPlotTime['paramid']

    # but we look for "long" gaps and insert nans so that they show on the plot
    # the sProc value gives the minimum size for a gap

    if num_point > 1:
        # check if we already know the position of the gaps else find them
        if not [d['paramid'] for d in lParam if d['paramid'] == nan_id]:
            (new_time, sNaN) = lt.find_gaps(sPlotTime,float(sProc['value']))
            sPlotTime['arrData'] = deepcopy(new_time)
            # add sNaN to the list of parameters
            arrData.append(deepcopy(sNaN))
            pTime = [el for (ind,el) in enumerate(lParam) if el['paramid'] == sPlotTime['paramid']][0]
            last_idx = pTime['last_idx']
            idx_list = pTime['idx_list']
            lParam.append({'paramid':nan_id,'last_idx':last_idx,'idx_list':idx_list,'in_cef':0,'cef':'','in_memory':1})
        else:
            sNaN = [el for (ind,el) in enumerate(arrData) if el['paramid'] == nan_id][0]

        av_data = insert_nans(sData['arrData'],sNaN)
    else:
        av_data = deepcopy(sData['arrData'])

    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = av_data
    sDataPlot['paramid'] = outputid

    return sDataPlot



##############################################################################################################
def filt_dim(sProc,lParam,arrData):
    # Filter out part of one dimension

    # INPUT_1 is the multi dimension data
    # INPUT_2 is the dimension to filter
    # INPUT_3 or VALUE gives the filter range (if VALUE has 3 values the 3rd one is a flag to indicate if delta+/- should be used)
    # OUTPUT_1 is the data with filtered data replaced by NaNs

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sFilter = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    if (idx_input != -1):
        input_3 = sProc['sArgument'][idx_input]['paramid']
        sTmp = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]
        yrange = sTmp['arrData']
    else:
        yrange = sProc['value'].split(',')

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        # check which DEPEND data to filter
        new_data = deepcopy(sData['arrData'])
        num_dim = len(sData['arrData'].shape)

        # do I filter a range or a single value ?
        if len(yrange) > 1:
            if len(yrange) == 3:
                flag_delta = float(yrange[2])
            else:
                flag_delta = 1

            if flag_delta == 1:
                filterP = sFilter['arrData'].astype(float) + sFilter['arrDeltaP'].astype(float)
                filterM = sFilter['arrData'].astype(float) - sFilter['arrDeltaM'].astype(float)
                if float(yrange[1]) > float(yrange[0]):
                    idx_inval = np.logical_or((filterP < float(yrange[0])) , (filterM > float(yrange[1])))
                else:
                    idx_inval = np.logical_and((filterP < float(yrange[0])) , (filterM > float(yrange[1])))
            else:
                idx_inval = np.where((sFilter['arrData'].astype(float) < float(yrange[0])) | (sFilter['arrData'].astype(float) > float(yrange[1])))

        else:
            if sFilter['type'] == 'INT' or sFilter['type'] == 'FLOAT':
                filter_val = float(yrange[0])
            else:
                filter_val = str(yrange[0])

            idx_inval = np.where(sFilter['arrData'] != filter_val)

        # dimension to filter is a dependency
        if (sFilter['paramid'] in sData['arrDepend']):
            dim = sData['arrDepend'].index(sFilter['paramid'])
            # replace "invalid" values with NaNs
            if num_dim == 3:
                if dim == 1:
                    new_data[:,idx_inval,:] = np.nan
                elif dim == 2:
                    new_data[:,:,idx_inval] = np.nan
                else:
                    print("ERROR: filter_dim function doesn't deal with this array dim")
            elif num_dim == 4:
                if dim == 1:
                    new_data[:,idx_inval,:,:] = np.nan
                elif dim == 2:
                    new_data[:,:,idx_inval,:] = np.nan
                elif dim == 3:
                    new_data[:,:,:,idx_inval] = np.nan
                else:
                    print("ERROR: filter_dim function doesn't deal with this array dim")
            else:
                print("ERROR: filter_dim function doesn't deal with this array shape")

        else:
        # dimension to filter is not a dependency
            new_data[idx_inval] = np.nan
       
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = new_data
        sDataPlot['arrDepend'] = sData['arrDepend']
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return sDataPlot

##############################################################################################################
def av_dim(sProc,lParam,arrData):
    # Average the data over one dimension
    # eg: to create omni spectro

    # INPUT_1 is the multi dimension data
    # Processing "value" gives the dimension to keep
    # OUTPUT_1 is the averaged data

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        # check which DEPEND data to average
        dim_name = sProc['value']
        data = sData['arrData']

        for i in range(len(sData['arrDepend'])-1):
            # ignore first dim which is time
            dim = i+1
            if sData['arrDepend'][dim] != dim_name:
                data = np.nanmean(data, axis=dim, keepdims=1)

        if len(data) > 1: #non empty input file
            data = np.squeeze(data)

        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        #idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == "OUTPUT_1"), -1)
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return sDataPlot


##############################################################################################################
def nrj_to_log(sProc,lParam,arrData):
    # convert nrj to log
    # don't update the data, this is for input datasets which are logarithmically spaced
    # => the ones produced by TK

    # INPUT_1 is the nrj array
    # Proc VALUE gives axis range
    # OUTPUT_1 is the new nrj vector

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_y = len(sData['arrData'])
        ymin,ymax = sProc['value'].split(',')
        nrj_data = np.linspace(np.log10(float(ymin)),np.log10(float(ymax)),num_y+1,endpoint=True)[:-1]
        # delta_nrj should be fixed so use the first one
        if len(nrj_data) > 1: 
            delta_nrj = nrj_data[1] - nrj_data[0]
        else:
            # no data
            delta_nrj = 1

        # store new nrj vector
        output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
        if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
            sDataPlot = mkp.make_sParameter()
            sDataPlot['arrData'] = nrj_data
            sDataPlot['paramid'] = output_1
            sDataPlot['arrDeltaP'] = delta_nrj
            sDataPlot['arrDeltaM'] = 0
            arrData.append(deepcopy(sDataPlot))

            idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
            lParam[idx_output]['in_memory'] = 1

    return sDataPlot

##############################################################################################################
def resh_nrj(sProc,lParam,arrData):
    # map nrj varying data to a regular grid

    # INPUT_1 is the spectro data
    # INPUT_2 is the nrj array

    # Proc VALUE gives axis type and axis range

    # OUTPUT_1 is the mapped spectro data
    # OUTPUT_2 is the new nrj vector

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sNRJ = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_y = int(glb.NUM_YDATA_SPEC)
        if (sData['arrData']).shape:
            num_record = (sData['arrData']).shape[0]
        else:
            num_record = 0


        resolved_data = np.empty((num_record,num_y))
        resolved_data[:] = np.nan

        ytype,ymin,ymax = sProc['value'].split(',')

        if ytype == 'logarithmic':
            nrj_data = np.linspace(np.log10(float(ymin)),np.log10(float(ymax)),num_y)
            delta_nrj = (np.log10(float(ymax))-np.log10(float(ymin)))/(num_y-1)
        else:
            nrj_data = np.linspace(float(ymin),float(ymax),num_y)
            delta_nrj = (float(ymax)-float(ymin))/(num_y-1)

        # check that there is data to process
        idx_data = np.isfinite(np.array(sData['arrData']))
        num_data = np.count_nonzero(idx_data)
        if num_data > 0:
            if ytype == 'logarithmic':
                nrj_band_min = np.log10(np.array(sNRJ['arrData'] - np.asarray(sNRJ['arrDeltaM'],dtype=float)))
                nrj_band_max = np.log10(np.array(sNRJ['arrData'] + np.asarray(sNRJ['arrDeltaP'],dtype=float)))
                #sNRJ['arrData'] = np.log10(sNRJ['arrData'])
            else:
                nrj_band_min = np.array(sNRJ['arrData'] - np.asarray(sNRJ['arrDeltaM'],dtype=float))
                nrj_band_max = np.array(sNRJ['arrData'] + np.asarray(sNRJ['arrDeltaP'],dtype=float))

            # can't use the logical_and with NaNs (throw a warning and app.py get stuck (?))
            idx_nan_min = np.isnan(nrj_band_min)
            num_nan_min = np.count_nonzero(idx_nan_min)
            min_tmp = nrj_band_min
            if num_nan_min > 0:
                min_tmp[idx_nan_min] = -1

            idx_nan_max = np.isnan(nrj_band_max)
            num_nan_max = np.count_nonzero(idx_nan_max)
            max_tmp = nrj_band_max
            if num_nan_max > 0:
                max_tmp[idx_nan_max] = -1

            if len(nrj_band_min.shape) > 1:

                for t in range(num_record):
                    for n in range(num_y-1):
                        nrj_min = nrj_data[n]
                        nrj_max = nrj_data[n+1]
                        #idx_nrj = np.logical_and(nrj_band_min[t,:] <= nrj_max , nrj_band_max[t,:] >= nrj_min)
                        idx_nrj = np.logical_and(np.squeeze(min_tmp[t,:]) <= nrj_max , np.squeeze(max_tmp[t,:]) >= nrj_min)

 
                        if idx_nrj.any():
                            val_nrj = np.where(idx_nrj)
                            resolved_data[t,n] = bn.nanmean(sData['arrData'][t,val_nrj[0]])
            else:

                for n in range(num_y-1):
                    nrj_min = nrj_data[n]
                    nrj_max = nrj_data[n+1]


                    #idx_nrj = np.logical_and(nrj_band_min <= nrj_max , nrj_band_max >= nrj_min)
                    idx_nrj = np.logical_and(min_tmp <= nrj_max , max_tmp >= nrj_min)

                    if idx_nrj.any():
                        val_nrj = np.where(idx_nrj)
                        for t in range(num_record):
                            resolved_data[t,n] = bn.nanmean(sData['arrData'][t,val_nrj[0]])
        else:
            print("NO DATA - resolve_nrj")

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = resolved_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        # store new nrj vector
        output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
        if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:
            sDataPlot = mkp.make_sParameter()
            sDataPlot['arrData'] = nrj_data
            sDataPlot['paramid'] = output_2
            sDataPlot['arrDeltaP'] = delta_nrj
            arrData.append(deepcopy(sDataPlot))

            idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
            lParam[idx_output]['in_memory'] = 1

    return sDataPlot


##############################################################################################################
def reso_nrj(sProc,lParam,arrData):
    # if needed (logarithmic) reshape nrj_vector
    # calculate delta_nrj

    # Proc VALUE gives axis type and axis range

    # INPUT_1 is the nrj array
    # OUTPUT_1 is the new nrj vector

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sNRJ = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        ytype,ymin,ymax = sProc['value'].split(',')

        if (np.isfinite(sNRJ['arrData']).any()):
            num_y = len(sNRJ['arrData'][np.isfinite(sNRJ['arrData'])])

            if ytype == 'logarithmic':
                nrj_data = np.log10(sNRJ['arrData'])
                delta_nrj = (np.log10(float(ymax))-np.log10(float(ymin)))/(num_y-1)
            else:
                nrj_data = sNRJ['arrData']
                delta_nrj = (float(ymax)-float(ymin))/num_y
        else:
            nrj_data = sNRJ['arrData']
            delta_nrj = float(ymax)-float(ymin)

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = nrj_data
        sDataPlot['paramid'] = output_1
        sDataPlot['arrDeltaP'] = delta_nrj

        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1


    return sDataPlot

##############################################################################################################
def filter_fixed_nrj(sProc,lParam,arrData):
    # Filter nrjs in the case of non-record-varying data

    # Proc VALUE gives filter range

    # INPUT_1 is the nrj vector
    # INPUT_2 is the data array

    # OUTPUT_1 is the new nrj vector
    # OUTPUT_2 is the new data array

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sNRJ = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        ymin,ymax = sProc['value'].split(',')
        idx_val_nrj = np.where(np.isfinite(sNRJ['arrData']) & (sNRJ['arrData'] >= float(ymin)) & (sNRJ['arrData'] <= float(ymax)))

        new_nrj = sNRJ['arrData'][idx_val_nrj]
        new_data = np.squeeze(sData['arrData'][:,idx_val_nrj])

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = new_data
        sDataPlot['paramid'] = output_2

        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

        sNRJPlot = mkp.make_sParameter()
        sNRJPlot['arrData'] = new_nrj
        sNRJPlot['paramid'] = output_1

        arrData.append(deepcopy(sNRJPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return sDataPlot


##############################################################################################################
def interpolate_fixed_nrj(sProc,lParam,arrData):
    # interpolate over nrjs in the case of non-record-varying data
    # keep gaps longer than a certain length

    # Proc VALUE gives gap length, ymin, ymax

    # INPUT_1 is the nrj vector
    # INPUT_2 is the data array

    # OUTPUT_1 is the interpolated nrj vector
    # OUTPUT_2 is the interpolated data array

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sNRJ = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        interp_factor,ymin, ymax = sProc['value'].split(',')
        ymax = float(ymax)
        ymin = float(ymin)

        num_x = (sData['arrData'].shape)[0]
        num_y = (sData['arrData'].shape)[1]

        itp_data = np.empty((num_x,glb.NUM_YDATA_SPEC))
        itp_data[:] = np.nan

        delta_nrj = (ymax-ymin)/glb.NUM_YDATA_SPEC
        itp_nrj = [x*delta_nrj+ymin for x in range(glb.NUM_YDATA_SPEC)]

        if interp_factor > 1:
            for n in range(num_x):
                # remove gaps smaller than interp_factor NaNs
                values = np.squeeze(sData['arrData'][n,:])
                i = np.arange(values.size)
                valid = np.isfinite(values)
                itp_data_n = np.interp(i, i[valid], values[valid])

                invalid = ~valid
                for t in range(1, int(interp_factor)+1):
                    invalid[:-t] &= invalid[t:]
                    itp_data_n[invalid] = np.nan

                # interpolate over NUM_YDATA_SPEC points
                y_data = np.squeeze(itp_data_n)
                itp_data[n,:] = np.interp(itp_nrj,sNRJ['arrData'],y_data)
        else:
            for n in range(num_x):
                # interpolate over NUM_YDATA_SPEC points
                ydata = np.squeeze(sData['arrData'][n,:])
                itp_data[n,:] = np.interp(itp_nrj,sNRJ['arrData'],y_data)

        #  store interpolated data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = itp_data
        sDataPlot['paramid'] = output_2

        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

        sNRJPlot = mkp.make_sParameter()
        sNRJPlot['arrData'] = itp_nrj
        sNRJPlot['arrDeltaP'] = delta_nrj
        sNRJPlot['paramid'] = output_1

        arrData.append(deepcopy(sNRJPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return sDataPlot



##############################################################################################################
def interpolate_3D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):


# THIS FUNCTION IS PROBLEMATIC AS IT IS NOT IGNORING NANS WHICH CREATES A LOT OF EMPTY DATA WHERE IT SHOULDN'T

    # check if there is data
    if (len(sData['arrData'])) != 1:
        # interpolate data for each energy/frequency bin
        num_y = (sData['arrData'].shape)[1]
        num_x = len(sPlotTime['arrData'])

        if num_x != len(sJulTime['arrData']):

            x_data = sJulTime['arrData']
            z_data = sData['arrData']

            # insert nans at the beginning and end of the data for interpolation
            delta_t = sPlotTime['arrDeltaP']
            if x_data[0] > glb.date_start_milli+delta_t/2:
                z_data = np.insert(z_data,0,np.nan,axis=0)
                x_data = np.insert(x_data,0,glb.date_start_milli+delta_t/2)
            if x_data[-1] < glb.date_stop_milli-delta_t/2:
                z_data = np.insert(z_data,len(z_data),np.nan,axis=0)
                x_data = np.insert(x_data,len(x_data),glb.date_stop_milli-delta_t/2)

            sJulTime['arrData'] = x_data


# DONT'T INSERT NANs FOR SPECTRO ?
# otherwise insert_nan function will have to be updated for multidimensional arrays


            # check if we already know the position of the gaps else find them
            #nan_id = "nan__" + sPlotTime['paramid']
            #if not [d['paramid'] for d in lParam if d['paramid'] == nan_id]:
                #(new_time, sNaN) = lt.find_gaps(sJulTime,float(sProc['value']))
                #sJulTime['arrData'] = deepcopy(new_time)
                # add sNaN to the list of parameters
                #arrData.append(deepcopy(sNaN))
                #pTime = [el for (ind,el) in enumerate(lParam) if el['paramid'] == sJulTime['paramid']][0]
                #last_idx = pTime['last_idx']
                #idx_list = pTime['idx_list']
                #lParam.append({'paramid':nan_id,'last_idx':last_idx,'idx_list':idx_list,'in_cef':0,'cef':'','in_memory':1})
            #else:
                #sNaN = [el for (ind,el) in enumerate(arrData) if el['paramid'] == nan_id][0]

            x_data = sJulTime['arrData']
            itp_data = np.empty((num_x,num_y))
            itp_data[:] = np.nan

            for n in range(num_y):
                #itp_data_n = insert_nans(np.squeeze(z_data[:,n]),sNaN)
                itp_data_n = np.squeeze(z_data[:,n])
                itp_data[:,n] = np.interp(sPlotTime['arrData'],x_data,itp_data_n)

        else:
            itp_data = sData['arrData']

    else:
        itp_data = sData['arrData']

    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = itp_data
    sDataPlot['paramid'] = outputid

    return sDataPlot






##############################################################################################################
def average_3D(sJulTime,sPlotTime,sData,arrData,outputid,sProc,lParam):

    # check if there is data

    #if (sData['arrData'].shape)[0] != 0:
    if np.isfinite(sJulTime['arrData']).any():
        num_y = (sData['arrData'].shape)[1]
        num_x = len(sPlotTime['arrData'])

        delta_t = sPlotTime['arrDeltaP']

        int_time_min = sJulTime['arrDeltaM']
        int_time_max = sJulTime['arrDeltaP']

        if num_x != len(sJulTime['arrData']):

            x_data = sJulTime['arrData']
            z_data = sData['arrData']

            av_data = np.empty((num_x,num_y))
            av_data[:] = np.nan


            # fill in array
            for i in range(num_x):

                time_min = i*delta_t - delta_t/2 + glb.date_start_milli
                time_max = i*delta_t + delta_t/2 + glb.date_start_milli

                idx_val_time = np.logical_and(int_time_min <= time_max , int_time_max > time_min)
               
                if idx_val_time.any() :
                    for n in range(num_y):
                        av_data_n = np.squeeze(z_data[:,n])
                        av_data[i,n] = bn.nanmean(av_data_n[idx_val_time])

        else:
            av_data = sData['arrData']

    else:
        av_data = sData['arrData']


    sDataPlot = mkp.make_sParameter()
    sDataPlot['arrData'] = av_data
    sDataPlot['paramid'] = outputid

    return sDataPlot



#############################################################################################################
def process_3D(sProc,lParam,arrData,proc_type):
    # reduce number of points in the spectrogram => set to a regular grid

    # INPUT_1 is the data to process
    # INPUT_2 is the data time vector (julian time)
    # INPUT_3 is the plot time vector


    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    # extract the time lists from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sJulTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sPlotTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        if proc_type == "average" or proc_type == "spec_average":
            sDataPlot = average_3D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        elif proc_type == "interpolate":
            sDataPlot = interpolate_3D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)
        else:
            print("WARNING: unknown 3D process type " + proc_type + " / use average")
            sDataPlot = average_3D(sJulTime,sPlotTime,sData,arrData,output_1,sProc,lParam)

        arrData.append(deepcopy(sDataPlot))
        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0





##############################################################################################################

def merge_data(sProc,lParam,arrData):
    # merge data from 2 different datasets

    # INPUT_1 is the data to process from dataset 1
    # INPUT_2 is the time vector from dataset 1
    # INPUT_3 is the nrj vector from dataset 1
    # INPUT_4 is the data to process from dataset 2
    # INPUT_5 is the time vector from dataset 2
    # INPUT_6 is the nrj vector from dataset 2

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_4"), -1)
    input_4 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_4][0]

    # extract the time lists from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sTime1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_5"), -1)
    input_5 = sProc['sArgument'][idx_input]['paramid']
    sTime2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_5][0]

    # extract the nrj lists from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sNRJ1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_6"), -1)
    input_6 = sProc['sArgument'][idx_input]['paramid']
    sNRJ2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_6][0]


    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        # check if we have data in both files
        idx_data1 = np.isfinite(np.array(sData1['arrData']))
        idx_data2 = np.isfinite(np.array(sData2['arrData']))

        if idx_data2.any() and idx_data1.any():
            print("DATA in both files to be merged")
            # sort time
            new_time = np.append(sTime1['arrData'],sTime2['arrData'])
            idx_sort = np.argsort(new_time)
            merged_time = new_time[idx_sort]

            if np.array_equal(sNRJ1['arrData'],sNRJ2['arrData']):
                nrj_data = sNRJ1['arrData']
                delta_nrj = sNRJ1['arrDeltaP']
            else:
                print("ERROR: both nrj vector should be identical when merging 3D data")
                exit()


            # merge/sort data
            new_data = np.vstack([sData1['arrData'],sData2['arrData']])
            num_dim = len(new_data.shape)

            if num_dim == 1:
                merged_data = new_data[idx_sort]
            elif num_dim == 2:
                merged_data = new_data[idx_sort,:]
            else:
                print("ERROR: more dimensions than expected in merge_data ... expecting 1 or 2, got "+str(num_dim))
                print("Merging must be done after reducing the number of dims/nrjs for the spectro")
                exit()

        else:
            if idx_data1.any():
                print("DATA only in INPUT_1")

                new_time = sTime1['arrData']
                merged_data = sData1['arrData']
                idx_sort = np.argsort(new_time)
                merged_time = new_time[idx_sort]
                nrj_data = sNRJ1['arrData']
                delta_nrj = sNRJ1['arrDeltaP']
            elif idx_data2.any():
                print("DATA only in INPUT_2")

                new_time = sTime2['arrData']
                merged_data = sData2['arrData']
                idx_sort = np.argsort(new_time)
                merged_time = new_time[idx_sort]
                nrj_data = sNRJ2['arrData']
                delta_nrj = sNRJ2['arrDeltaP']
            else:
                print("NO DATA in any of the files to merge")
                merged_time = np.empty(0)
                merged_data = np.empty(0)
                idx_sort = np.empty(0)
                nrj_data = np.empty(0)
                delta_nrj = np.empty(0)

        #  store merged data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = merged_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
        if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:

            if idx_data2.any() and idx_data1.any():

                # fix delta time
                if sTime1['arrDeltaP'].shape and len(sTime1['arrDeltaP']) > 1:
                    new_time_dp = np.append(sTime1['arrDeltaP'],sTime2['arrDeltaP'])
                    merged_time_dp = new_time_dp[idx_sort]
                else:
                    merged_time_dp = sTime1['arrDeltaP']
                    merged_time_dm = sTime1['arrDeltaM']

                if sTime1['arrDeltaM'].shape and len(sTime1['arrDeltaM']) > 1:
                    new_time_dm = np.append(sTime1['arrDeltaM'],sTime2['arrDeltaM'])
                    merged_time_dm = new_time_dm[idx_sort]
                else:
                    merged_time_dm = sTime1['arrDeltaM']


                name,datasetid = sTime1['paramid'].split("__")
                max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
            else:
                if idx_data1.any():
                    merged_time_dp = sTime1['arrDeltaP']
                    merged_time_dm = sTime1['arrDeltaM']

                    name,datasetid = sTime1['paramid'].split("__")
                    max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                    min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
                elif idx_data2.any():
                    merged_time_dp = sTime2['arrDeltaP']
                    merged_time_dm = sTime2['arrDeltaM']

                    name,datasetid = sTime2['paramid'].split("__")
                    max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                    min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
                else:
                    name,datasetid = sTime1['paramid'].split("__")
                    merged_time_dp = np.array([4])
                    merged_time_dm = np.array([4])

            #  store merged time
            sTimePlot = mkp.make_sParameter()
            sTimePlot['arrData'] = merged_time
            sTimePlot['arrDeltaM'] = merged_time_dm
            sTimePlot['arrDeltaP'] = merged_time_dp
            sTimePlot['paramid'] = output_2
            arrData.append(deepcopy(sTimePlot))

            idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
            lParam[idx_output]['in_memory'] = 1


            # store time resolution for new datasetid
            sMaxRes = mkp.make_sParameter()
            sMaxRes['arrData'] = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
            sMinRes = mkp.make_sParameter()
            sMinRes['arrData'] = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
            name,datasetid = sTimePlot['paramid'].split("__")
            sMaxRes['paramid'] = "MAX_TIME_RESOLUTION__" + datasetid
            sMinRes['paramid'] = "MIN_TIME_RESOLUTION__" + datasetid

            arrData.append(deepcopy(sMaxRes))
            arrData.append(deepcopy(sMinRes))


        output_3 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_3"][0]
        if [d['paramid'] for d in lParam if d['paramid'] == output_3 and d['in_memory'] == 0]:
            #  store nrj data
            sNRJPlot = mkp.make_sParameter()
            sNRJPlot['arrData'] = nrj_data
            sNRJPlot['arrDeltaP'] = delta_nrj
            sNRJPlot['paramid'] = output_3
            arrData.append(deepcopy(sNRJPlot))

            idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_3), -1)
            lParam[idx_output]['in_memory'] = 1


    return 0





##############################################################################################################
def merge_2d(sProc,lParam,arrData):
    # merge data from 2 different datasets

    # INPUT_1 is the data to process from dataset 1
    # INPUT_2 is the time vector from dataset 1
    # INPUT_3 is the data to process from dataset 2
    # INPUT_4 is the time vector from dataset 2

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    # extract the time lists from the data array
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sTime1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_4"), -1)
    input_4 = sProc['sArgument'][idx_input]['paramid']
    sTime2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_4][0]


    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        # check if we have data in both files
        idx_data1 = np.isfinite(np.array(sData1['arrData']))
        idx_data2 = np.isfinite(np.array(sData2['arrData']))

        if idx_data2.any() and idx_data1.any():
            print("DATA in both files to be merged")
            # sort time
            new_time = np.append(np.squeeze(sTime1['arrData']),np.squeeze(sTime2['arrData']))
            idx_sort = np.argsort(new_time)
            merged_time = new_time[idx_sort]

            # merge/sort data
            new_data = np.append(np.squeeze(sData1['arrData']),np.squeeze(sData2['arrData']))
            num_dim = len(new_data.shape)

            if num_dim == 1:
                merged_data = new_data[idx_sort]
            elif num_dim == 2:
                merged_data = new_data[idx_sort,:]
            else:
                print("ERROR: more dimensions than expected in merge_data ... expecting 1 or 2, got "+str(num_dim))
                exit()

        else:
            if idx_data1.any():
                print("DATA only in INPUT_1")

                new_time = sTime1['arrData']
                merged_data = sData1['arrData']
                idx_sort = np.argsort(new_time)
                merged_time = new_time[idx_sort]
            elif idx_data2.any():
                print("DATA only in INPUT_2")

                new_time = sTime2['arrData']
                merged_data = sData2['arrData']
                idx_sort = np.argsort(new_time)
                merged_time = new_time[idx_sort]
            else:
                print("NO DATA in any of the files to merge")
                merged_time = np.empty(0)
                merged_data = np.empty(0)
                idx_sort = np.empty(0)

        #  store merged data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = merged_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
        if [d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]:

            if idx_data2.any() and idx_data1.any():
                # fix delta time
                if sTime1['arrDeltaP'].shape and len(sTime1['arrDeltaP']) > 1:
                    new_time_dp = np.append(sTime1['arrDeltaP'],sTime2['arrDeltaP'])
                    merged_time_dp = new_time_dp[idx_sort]
                else:
                    merged_time_dp = sTime1['arrDeltaP']
                    merged_time_dm = sTime1['arrDeltaM']

                if sTime1['arrDeltaM'].shape and len(sTime1['arrDeltaM']) > 1:
                    new_time_dm = np.append(sTime1['arrDeltaM'],sTime2['arrDeltaM'])
                    merged_time_dm = new_time_dm[idx_sort]
                else:
                    merged_time_dm = sTime1['arrDeltaM']


                name,datasetid = sTime1['paramid'].split("__")
                max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
            else:
                if idx_data1.any():
                    merged_time_dp = sTime1['arrDeltaP']
                    merged_time_dm = sTime1['arrDeltaM']

                    name,datasetid = sTime1['paramid'].split("__")
                    max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                    min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
                elif idx_data2.any():
                    merged_time_dp = sTime2['arrDeltaP']
                    merged_time_dm = sTime2['arrDeltaM']

                    name,datasetid = sTime2['paramid'].split("__")
                    max_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
                    min_res = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
                else:
                    name,datasetid = sTime1['paramid'].split("__")
                    merged_time_dp = np.array([4])
                    merged_time_dm = np.array([4])

            #  store merged time
            sTimePlot = mkp.make_sParameter()
            sTimePlot['arrData'] = merged_time
            sTimePlot['arrDeltaM'] = merged_time_dm
            sTimePlot['arrDeltaP'] = merged_time_dp
            sTimePlot['paramid'] = output_2
            arrData.append(deepcopy(sTimePlot))

            idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
            lParam[idx_output]['in_memory'] = 1

            # store time resolution for new datasetid
            sMaxRes = mkp.make_sParameter()
            sMaxRes['arrData'] = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MAX_TIME_RESOLUTION__" + datasetid][0])
            sMinRes = mkp.make_sParameter()
            sMinRes['arrData'] = float([el['arrData'] for (ind,el) in enumerate(arrData) if el['paramid'] == "MIN_TIME_RESOLUTION__" + datasetid][0])
            name,datasetid = output_1.split("__")
            sMaxRes['paramid'] = "MAX_TIME_RESOLUTION__" + datasetid
            sMinRes['paramid'] = "MIN_TIME_RESOLUTION__" + datasetid

            arrData.append(deepcopy(sMaxRes))
            arrData.append(deepcopy(sMinRes))


    return 0

##############################################################################################################
def total_power(sProc,lParam,arrData):
    # calculate the total power of a 2/3 comp vector

    # INPUT_1 is the data vector

    # OUTPUT_1 is the total power data


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        dim = sData['arrData'].shape
        num_dim = len(dim)

        if num_dim == 1: # no data
            data_tot = sData['arrData']
        elif num_dim == 2:
            data_tot = np.zeros(dim[0])

            # add squared component
            for d in range(dim[1]):
                data_tot += np.square(np.squeeze(sData['arrData'][:,d]))

            # take square root of total
            data_tot = np.sqrt(data_tot)

        elif num_dim == 3: # multi-comp spectro (STA CS)
            if dim[2] == 3:
                data_tot = np.sqrt(np.square(sData['arrData'][:,:,0])+np.square(sData['arrData'][:,:,1])+np.square(sData['arrData'][:,:,2]))
            elif dim[2] == 2:
                data_tot = np.sqrt(np.square(sData['arrData'][:,:,0])+np.square(sData['arrData'][:,:,1]))
        else:
            print("ERROR: more dimensions than expected in tot_power ... expecting 1 or 2, got "+str(num_dim))
            exit()


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_tot
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0


##############################################################################################################
def distance(sProc,lParam,arrData):
    # calculate the distance in Earth radius of a 2/3 comp vector

    # INPUT_1 is the data vector

    # OUTPUT_1 is the total power data


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        dim = sData['arrData'].shape
        data_tot = np.zeros(dim[0])

        # add squared component
        for d in range(dim[1]):
              data_tot += np.square(np.squeeze(sData['arrData'][:,d]))

        # take square root of total
        data_tot = np.sqrt(data_tot)

        # convert to Re
        data_tot /= 6371.2

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_tot
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0




##############################################################################################################
def cluster_distance(sProc,lParam,arrData):
    # calculate the distance in Earth radius for the cluster sc (need to add position of reference spacecraft)

    # INPUT_1 is the position of the reference_spacecraft

    # INPUT_2 is the position of the sc relative to the reference sc

    # OUTPUT_1 is the total power data


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        dim = sData['arrData'].shape
        data_tot = np.zeros(dim[0])

        data_sc = sData['arrData'] + sData2['arrData']

        # add squared component
        for d in range(dim[1]):
              data_tot += np.square(np.squeeze(data_sc[:,d]))

        # take square root of total
        data_tot = np.sqrt(data_tot)

        # convert to Re
        data_tot /= 6371.2

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_tot
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0






##############################################################################################################
def calc_angle(sProc,lParam,arrData):

    # calculate Theta/Phi angle of coordinate vector

    # INPUT_1 is the cartesian data

    # OUTPUT_1 is the theta data
    # OUTPUT_2 is the phi data

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if ( ([d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]) or ([d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]) ):

        xyz = sData['arrData']
        num_dim = len(xyz.shape)

        if num_dim == 1: # no data
            theta = xyz
            phi = xyz
        elif num_dim == 2:
            xy = np.square(xyz[:,0]) + np.square(xyz[:,1])
            theta = np.arctan2(np.sqrt(xy), xyz[:,2]) # for elevation angle defined from Z-axis down
            theta = np.arctan2(xyz[:,2], np.sqrt(xy)) # for elevation angle defined from XY-plane up
            phi = np.arctan2(xyz[:,1], xyz[:,0])
        else:
            print("ERROR: more dimensions than expected in calc_angle ... expecting 1 or 2, got "+str(num_dim))
            exit()
        
        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = theta
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = phi
        sDataPlot['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1


    return 0



##############################################################################################################
def zero_to_nan(sProc,lParam,arrData):

    # replace zeros by nan in data array

    # INPUT_1 is the data

    # OUTPUT_1 is the filtered data

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if ([d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]) :

        data = deepcopy(sData['arrData'])
        idx_zero = np.where(data == 0)
        if np.count_nonzero(idx_zero) > 0:
            data[idx_zero] = np.nan

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        # keep the dependencies info
        sDataPlot['arrDepend'] = deepcopy(sData['arrDepend'])
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0


##############################################################################################################
def calc_modulo(sProc,lParam,arrData):
    # calculate the modulo of STAFF complex spectra

    # INPUT_1 is the complex spectra data

    # OUTPUT_1 is the modulo of the complex data


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        data = deepcopy(sData['arrData'])
        #data[data < -1] = np.nan

        data_modulo = np.sqrt(np.squeeze(np.square(data[:,:,:,0])+np.square(data[:,:,:,1])))

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_modulo
        sDataPlot['paramid'] = output_1
        # keep the dependencies info
        sDataPlot['arrDepend'] = deepcopy(sData['arrDepend'])
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0



##############################################################################################################
def calc_itp_complex(sProc,lParam,arrData):
    # calculate the integrated power of STAFF complex spectra

    # INPUT_1 is the complex spectra data

    # OUTPUT_1 is the itp of the complex data


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:


        data = deepcopy(sData['arrData'])
        # filter out negative values
        #data[data < 0] = np.nan

        # the current CS files are in nT2 and not nT2/ Hz so for the time being we don't multiply by the bandwidth
        data_itp = np.nansum(np.squeeze((np.square(data[:,:,0,0])+np.square(data[:,:,0,1]) + np.square(data[:,:,1,0])+np.square(data[:,:,1,1]) + np.square(data[:,:,2,0])+np.square(data[:,:,2,1]))),axis=1)

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_itp
        sDataPlot['paramid'] = output_1
        # keep the dependencies info
        sDataPlot['arrDepend'] = deepcopy(sData['arrDepend'])
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0



##############################################################################################################
def calc_itp(sProc,lParam,arrData):
    # calculate the integrated power

    # INPUT_1 is the data to integrate

    # INPUT_2 is the frequency vector

    # proc VALUE is the band number

    # OUTPUT_1 is the itp of the data

    # itp = SUM(SUM(X[i]2+Y[i]2+Z[i]2)*2Delta_freq[i]))


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sFreq = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        #ymin,ymax = sProc['value'].split(',')
        band = int(sProc['value'])

        data = deepcopy(sData['arrData'])
        # filter out negative values
        #data[data < 0] = np.nan

#        data_itp = np.nansum(np.sqrt(np.square(data[:,:,0]) + np.square(data[:,:,1]) + np.square(data[:,:,2])),axis=1)
#        data_itp *= (float(ymax) - float(ymin))

        for i in range(9):
            data[:,i+band*9,:] = data[:,i+band*9,:] * np.sqrt(2*int(sFreq['arrDeltaP'][i+band*9])) 

        print(data.shape[2])
        if data.shape[2] == 3: 
            data_itp = np.nansum(np.squeeze(np.square(data[:,:,0]) + np.square(data[:,:,1]) + np.square(data[:,:,2])),axis=1)
        else:
            data_itp = np.nansum(np.squeeze(np.square(data[:,:,0]) + np.square(data[:,:,1])),axis=1)


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_itp
        sDataPlot['paramid'] = output_1
        # keep the dependencies info
        sDataPlot['arrDepend'] = deepcopy(sData['arrDepend'])
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0



##############################################################################################################
def param_average(sProc,lParam,arrData):
    # average 2 parameter from the same dataset

    # INPUT_1 is the first parameter

    # INPUT_2 is the second parameter

    # OUTPUT_1 is the averaged parameter


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        data_av = np.squeeze(np.nanmean(np.dstack((sData1['arrData'],sData2['arrData'])),2))

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_av
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0



##############################################################################################################
def convert_pef(sProc,lParam,arrData):
    # convert spectro data from count to pef (multiply by center energy)

    # INPUT_1 is the spectro data

    # INPUT_2 is the energy array/vector

    # OUTPUT_1 is the pef spectro

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        spectro_pef = sData1['arrData'] * sData2['arrData']
        

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = spectro_pef
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1



    return 0


##############################################################################################################
def edi_code(sProc,lParam,arrData):

    # decode edi freq flag:
    # 0 or 2 => 0.5 keV
    # 1 or 3 => 1 keV

    # INPUT_1 is the flag

    # OUTPUT_1 is the short freq
    # OUTPUT_2 is the long freq

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if ( ([d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]) or ([d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]) ):

        code = sData['arrData']
        num_data = len(sData['arrData'])

        data = deepcopy(sData['arrData'])

        short_freq = np.empty(num_data)
        short_freq[:] = np.nan

        long_freq = np.empty(num_data)
        long_freq[:] = np.nan

        idx_short = np.where((data == 0) | (data == 2))
        short_freq[idx_short] = 1

        idx_long = np.where((data == 1) | (data == 3))
        long_freq[idx_long] = 1


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = short_freq
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = long_freq
        sDataPlot['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1


    return 0

##############################################################################################################
def edi_bitmask(sProc,lParam,arrData):

    # decode edi bitmask

    # INPUT_1 is the bitmask

    # OUTPUT_1 is a 13 component array with the status/bits decoded


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if ( ([d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]) or ([d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]) ):

        status = deepcopy(sData['arrData'])
        bitmask = np.squeeze(status[:,3])
        num_data = len(sData['arrData'][:,0])
        num_comp = 13
        num_bits = 7

        data = np.empty((num_data,num_comp))
        data[:] = np.nan

        for bit in range(num_bits):
            bm = num_bits-bit-1

            n = np.floor(np.log(bitmask)/np.log(2))
            ind_bit = np.where(n == bm)

            data[ind_bit,bm] = 1
            bitmask[ind_bit] = bitmask[ind_bit] - 2**bm

        data[:,7] = np.squeeze(status[:,0])
        data[:,8] = np.squeeze(status[:,1]/100.)
        data[:,9] = np.squeeze(status[:,2]/100.)
        data[:,10] = np.squeeze(status[:,4]/100.)
        data[:,11] = np.squeeze(status[:,5])
        data[:,12] = np.squeeze(status[:,6]/90.)


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0




##############################################################################################################
def efw_bitmask(sProc,lParam,arrData):

    # decode edi bitmask

    # INPUT_1 is the bitmask

    # OUTPUT_1 is a 16 component array with the bits decoded


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if ( ([d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]) or ([d['paramid'] for d in lParam if d['paramid'] == output_2 and d['in_memory'] == 0]) ):

        bitmask = deepcopy(sData['arrData'])
        num_data = len(bitmask)
        num_bits = 16

        data = np.empty((num_data,num_bits))
        data[:] = np.nan

        for bit in range(num_bits):
            bm = num_bits-bit-1

            n = np.floor(np.log(bitmask)/np.log(2))
            ind_bit = np.where(n == bm)

            data[ind_bit,bm] = 1
            bitmask[ind_bit] = bitmask[ind_bit] - 2**bm

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

    return 0

##################################################################################################################################

def rap_int_time(sProc,lParam,arrData):

    # INPUT_1 is the int time data
    # INPUT_2 is the hist data
    # INPUT_3 is the auto_sw data

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sData3 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    output_3 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_3"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_data = len(sData1['arrData'])

        data = deepcopy(sData1['arrData'])

        data_on = np.empty((num_data))
        data_off = np.empty((num_data))
        data_hist = np.empty((num_data))
        data_on[:] = np.nan
        data_off[:] = np.nan
        data_hist[:] = np.nan

        ind_on = np.where(sData3['arrData'] == 1)
        ind_off = np.where(sData3['arrData'] == 0)
        ind_hist = np.where(sData2['arrData'] == 3)

        # for better scaling match int time values to simple index
        data[np.where(data == 2)] = 0
        data[np.where(data == 5)] = 1
        data[np.where(data == 15)] = 2
        data[np.where(data == 50)] = 3

        data_off[ind_off] = data[ind_off]
        data_on[ind_on] = data[ind_on]
        data_hist[ind_hist] = data[ind_hist]

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_on
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot2 = mkp.make_sParameter()
        sDataPlot2['arrData'] = data_off
        sDataPlot2['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot2))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot3 = mkp.make_sParameter()
        sDataPlot3['arrData'] = data_hist
        sDataPlot3['paramid'] = output_3
        arrData.append(deepcopy(sDataPlot3))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_3), -1)
        lParam[idx_output]['in_memory'] = 1



##################################################################################################################################

def rap_hv(sProc,lParam,arrData):

    # INPUT_1 is the start volt data
    # INPUT_2 is the stop volt data
    # INPUT_3 is the def volt data

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData1 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData2 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sData3 = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    output_3 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_3"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_data = len(sData1['arrData'])

        data1 = (deepcopy(sData1['arrData']))/1000.
        data2 = (deepcopy(sData2['arrData'])+20)/1000.
        data3 = (deepcopy(sData3['arrData'])+40)/1000.

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data1
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot2 = mkp.make_sParameter()
        sDataPlot2['arrData'] = data2
        sDataPlot2['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot2))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot3 = mkp.make_sParameter()
        sDataPlot3['arrData'] = data3
        sDataPlot3['paramid'] = output_3
        arrData.append(deepcopy(sDataPlot3))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_3), -1)
        lParam[idx_output]['in_memory'] = 1





##################################################################################################################################
# get caveat coverage ... if there's a record covering an interval, data set to 1
#
##################################################################################################################################
def get_caveat(sProc,lParam,arrData):

    # INPUT_1 is the time range vector
    # INPUT_2 is the plot time vector

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sPlotTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_data = len(sPlotTime['arrData'])
      
        int_time_min = np.array(sPlotTime['arrData']) - sPlotTime['arrDeltaM']
        int_time_max = np.array(sPlotTime['arrData']) + sPlotTime['arrDeltaP']

        data = np.empty((num_data))
        data[:] = np.nan

        cav_time_min = sTime['arrDeltaM']
        cav_time_max = sTime['arrDeltaP']

        num_record = len(cav_time_min)

        for rec in range(num_record):
            time_min = cav_time_min[rec]
            time_max = cav_time_max[rec]

            # check to which plot point the caveat range belongs to
            idx_val_time = np.squeeze(np.logical_and(int_time_min <= time_max , int_time_max >= time_min))            
            if idx_val_time.any() :
                data[idx_val_time] = 1

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1




##################################################################################################################################
# look for the changes of modes in the STAFF status word
# for SC info comes from bit 5:
#       NM = 0
#       FM = 1
# for SA info comes from bit 4:
#       NM = 0,1,2,4,5,6,7
#       FM = 8,9,a,c
# the passive mode (f) needs to be ignored => NM1/passive/FM1 is considered has a change of mode but
# NM1/passive/NM2 is not

def sta_extract_mode(sProc,lParam,arrData):
    # INPUT_1 is the status
    # value gives the instrument SC/SA
    # OUTPUT_1 is the mode change time vector

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        num_data = len(sData['arrData'])

        instrument = sProc['value']

        if instrument == 'SC':
            mode_data = [float(status[4]) for status in sData['arrData']]
        else:
            mode_data = np.full(num_data,np.nan)
            # SA NM/FM/other modes indexes
            #nm_sa = ['0','1','2','4','5','6','7']
            # Patrick Canu 34/03/2022 -> ignore special and emergency mode
            nm_sa = ['0','1','2','6','7']
            fm_sa = ['8','9','a','c']

            for i in range(num_data):
                if sData['arrData'][i][3] in nm_sa:
                    mode_data[i] = 0
                elif sData['arrData'][i][3] in fm_sa:
                    mode_data[i] = 1

        #  store data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = mode_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1


##################################################################################################################################
# look for the changes of modes in the STAFF status word

def sta_mode_change(sProc,lParam,arrData):
    # INPUT_1 is the time 
    # INPUT_2 is the status
    # value gives the instrument SC/SA
    # OUTPUT_1 is the mode change time vector
    # OUTPUT_2 is the mode change data vector

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    output_2 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_2"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        instrument = sProc['value']

        out_time = []
        out_data = []

        if len(sData['arrData']) > 1:
            status = np.append(sData['arrData'],[sData['arrData'][-1]])
            mode_change = np.where(np.abs(np.diff(status)) == 1)
            out_time = sTime['arrData'][mode_change]
            out_data = np.ones(len(out_time))

            # insert nans between mode changes so that they appear as individual points
            if len(out_data) > 1:
                num_data = len(out_data)
                for x in range(1,num_data):
                    idx = num_data - x
                    out_data=np.insert(out_data,idx,np.nan)
                    out_time=np.insert(out_time,idx,(out_time[idx-1]+(out_time[idx]-out_time[idx-1])/2.))

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = out_time
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1

        sDataPlot2 = mkp.make_sParameter()
        sDataPlot2['arrData'] = out_data
        sDataPlot2['paramid'] = output_2
        arrData.append(deepcopy(sDataPlot2))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_2), -1)
        lParam[idx_output]['in_memory'] = 1


##################################################################################################################################
# filter out interval for a specific TM mode

def filter_mode(sProc,lParam,arrData):
    # INPUT_1 is the data time
    # INPUT_2 is the data to filter
    # INPUT_3 is the tm time
    # INPUT_4 is the tm data
    # value gives the mode to filter (eg BM3)
    # OUTPUT_1 is the filtered data

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sTime = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_3"), -1)
    input_3 = sProc['sArgument'][idx_input]['paramid']
    sTimeTM = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_3][0]

    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_4"), -1)
    input_4 = sProc['sArgument'][idx_input]['paramid']
    sDataTM = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_4][0]


    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        mode = sProc['value']
        idx_mode = np.where(sDataTM['arrData'] == mode)

        out_data = np.array(deepcopy(sData['arrData']))

        int_time_min = np.array(((sTimeTM['arrData'][:,0]).astype(float)))
        int_time_max = np.array(((sTimeTM['arrData'][:,1]).astype(float)))

        # loop on intervals to filter
        time_min = int_time_min[idx_mode]
        time_max = int_time_max[idx_mode]

        status_min = sTime['arrData'] 
        status_max = sTime['arrData'] + sTime['arrDeltaP']

        for t in range(len(time_min)):
            t_min = time_min[t]
            t_max = time_max[t]

            idx_filter = np.logical_and(status_min >= t_min , status_max <= t_max)
            if idx_filter.any():
                out_data[idx_filter] = np.nan


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = out_data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1


