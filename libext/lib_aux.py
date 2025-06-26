import numpy as np
import make_param as mkp
from copy import deepcopy

def str_to_num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


##############################################################################################################
def filter_fillval(sData,lParam):

    print("filter_fillvals:", sData['paramid'])
    # if the parameter comes from cef files then replace the fill values by nans
    if [d['paramid'] for d in lParam if d['paramid'] == paramid and d['in_cef'] == 1]:

        if sData['fillval'] != '':
            fillval = str_to_num(sData['fillval'])
            idx_fill = np.where(sData['arrData'] == fillval)
            num_fill = np.count_nonzero(idx_fill)

            if num_fill > 0:
                print("filtering fillvals: " + str(np.count_nonzero(idx_fill)) + " fill values found")
                sData['arrData'][idx_fill]=np.nan
            else:
                print("no fill values found")


##############################################################################################################
def fill_to_nan(data,fillval,data_type):

    if data_type.upper() != 'STRING' and data_type.upper() != 'CHAR' and data_type.upper() != 'ISO_TIME' and data_type.upper() != 'ISO_TIME_RANGE' :
        fillval = float(fillval)

        if data_type.upper() == 'FLOAT':
            idx_fill = np.where(data == fillval)
        else:
            idx_fill = np.where(np.asarray(data,dtype=float) == fillval)

        num_fill = np.count_nonzero(idx_fill)
        if num_fill > 0:
            if data_type.upper() == 'INT':
                # NaN doesn't exist for integers, need to convert to float
                data = data.astype(float)

            print("filtering fillvals: " + str(np.count_nonzero(idx_fill)) + " fill values found")
            data[idx_fill]=np.nan
        else:
            print("no fill values found")

    return data



##############################################################################################################
def filter_zero(sProc,lParam,arrData):
    # Filter zeroes -> replace with NaNs

    # INPUT_1 is the data to filter

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    dims = sData['arrData'].shape
    tmp = np.ravel(sData['arrData'])
    idx_zeroes = np.array(np.where(tmp == 0., np.nan, tmp))
    sData['arrData'] = np.reshape(tmp,dims)



##############################################################################################################
# convert edi qzc data (background electron counts) to counts per seconds
def qzc_counts_per_second(sProc,lParam,arrData):
    # INPUT_1 is the qzc data
    # INPUT_2 is the status
    # OUTPUT_1 is the converted qzc data

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]


    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_2"), -1)
    input_2 = sProc['sArgument'][idx_input]['paramid']
    sStatus = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_2][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        num_data = len(sData['arrData'])
      
        data = sData['arrData']
        status = sStatus['arrData']

        data_out = np.empty((num_data))
        data_out[:] = np.NAN

        for rec in range(num_data):
            # if bit 0 is set, multiply by 1024
	    # otherwise multiply by 512
            bitmask = str(bin(status[rec]))
            if (bitmask[-1] == "1") :
                data_out[rec] = data[rec]*1024
            else:
                data_out[rec] = data[rec]*512


        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_out
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1











