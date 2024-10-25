import make_param as mkp
import lib_aux as la
import ceflib
import os
import numpy as np
from copy import deepcopy

import global_vars as gb

def get_attr(paramid,name):
    # check if attribute is constant or refers to another parameter
    # return the corresponding data
    data = ceflib.vattr(name,paramid)
    if data in ceflib.varnames():
        return deepcopy(np.array(ceflib.var(data)))
    else:
        return deepcopy(np.array(data))

def get_time_param(did):

    # read first parameter
    list_params = ceflib.varnames()
    name = list_params[0]
    paramid = name + '__' + did

    print("read time parameter ", paramid)

    sParameter = mkp.make_sParameter()
    sParameter['paramid'] = paramid

    time_vect = ceflib.var(name)

    # we request a slighlty bigger cef file than the time interval to take into account the record delta+-
    # we now only keep the data contained in the plot time-span
    if ceflib.vattr(name,"VALUE_TYPE") == "ISO_TIME":
        delta_min = (get_attr("DELTA_MINUS",name).astype(float) * 1000)
        delta_max = (get_attr("DELTA_PLUS",name).astype(float) * 1000)

        int_time_min = time_vect - delta_min
        int_time_max = time_vect + delta_max

        idx_valid = np.squeeze(np.logical_and( int_time_min <= gb.date_stop_milli , int_time_max > gb.date_start_milli))
    else:
        idx_valid = np.ones(ceflib.records(), dtype=bool)

    data = time_vect[idx_valid]

    # make sure first/last points times are not outside of time range otherwise highcharts may extend the xaxis boundaries
    if ceflib.vattr(name,"VALUE_TYPE") == "ISO_TIME":
        if data.size > 1:
            data[0] = max([data[0],gb.date_start_milli])
            data[len(data)-1] = min([data[len(data)-1],gb.date_stop_milli])
        elif data.size == 1:
            if data <  gb.date_start_milli:
                data = [gb.date_start_milli]
            elif data > gb.date_stop_milli:
                data = [gb.date_stop_milli]

    # get the attributes
    arrAttr = ceflib.vattributes(name)

    # get the useful metadata for the parameter
    # mandatory metadata:
    sParameter['fillval'] = ceflib.vattr(name,"FILLVAL")
    sParameter['type'] = ceflib.vattr(name,"VALUE_TYPE")
    sParameter['support'] = 1 if ceflib.vattr(name,'PARAMETER_TYPE') == "Support_Data" else 0
    sParameter['arrData'] = data

    # we need to only keep the valid indexes of delta plus/minus too
    delta_p = get_attr("DELTA_PLUS",name)
    if delta_p.size > 1:
        sParameter['arrDeltaP'] = delta_p[idx_valid]
    else:
        sParameter['arrDeltaP'] = delta_p

    delta_m = get_attr("DELTA_MINUS",name)
    if delta_m.size > 1:
        sParameter['arrDeltaM'] = delta_m[idx_valid]
    else:
        sParameter['arrDeltaM'] = delta_m

    return [sParameter,idx_valid,paramid]


def get_param(paramid,idx_valid):
    """ Get all the necessary data for one parameter from the CEF file """
    sParameter = mkp.make_sParameter()
    sParameter['paramid'] = paramid

    # ceflib parameters shouldn't contain the "__datasetid" extension
    name,datasetid = paramid.split("__")

    # get the parameter data
    data = ceflib.var(name)

    # get the attributes
    arrAttr = ceflib.vattributes(name)

    # if it's a DEPEND_0 parameter, only keep the data within the requested time range
    if ceflib.varnames()[0] == name or "DEPEND_0" in arrAttr:
        num_dim = len(data.shape)
        if num_dim == 1:
            data_valid = data[idx_valid]
        elif num_dim == 2:
            data_valid = data[idx_valid,:]
        elif num_dim ==3:
            data_valid = data[idx_valid,:,:]
        elif num_dim == 4:
            data_valid = data[idx_valid,:,:,:]
        else:
            print("unsupported number of dimensions. Check get_param function")
            data_valid = data
    else:
        data_valid = data

    filtered_data = la.fill_to_nan(np.array(deepcopy(data_valid)),ceflib.vattr(name,"FILLVAL"),ceflib.vattr(name,"VALUE_TYPE"))

    # get the useful metadata for the parameter
    # mandatory metadata:
    sParameter['fillval'] = ceflib.vattr(name,"FILLVAL")
    sParameter['type'] = ceflib.vattr(name,"VALUE_TYPE")
    sParameter['support'] = 1 if ceflib.vattr(name,'PARAMETER_TYPE') == "Support_Data" else 0
    sParameter['arrData'] = filtered_data

    # optional metadata:
    # we need to only keep the valid indexes of delta plus/minus in case they are time-varying
    if "DELTA_PLUS" in arrAttr:
        delta_p = get_attr("DELTA_PLUS",name)
        if "DEPEND_0" in arrAttr:
            sParameter['arrDeltaP'] = delta_p[idx_valid]
        else:
            sParameter['arrDeltaP'] = delta_p
    if "DELTA_MINUS" in arrAttr:
        delta_m = get_attr("DELTA_MINUS",name)
        if "DEPEND_0" in arrAttr:
            sParameter['arrDeltaM'] = delta_m[idx_valid]
        else:
            sParameter['arrDeltaM'] = delta_m


    #Quality q is not defined for "Support_Data"
    if sParameter['support'] == 0:
        sParameter['arrQuality'] = get_attr("QUALITY",name)

    # get list of the parameter dependencies
    depend = [s for s in arrAttr if "DEPEND_" in s]
    sParameter['num_depend'] = len(depend)
    for d in depend:
        if not sParameter['arrDepend']:
            sParameter['arrDepend'] = [ceflib.vattr(name,d)+'__'+datasetid]
        else:
            sParameter['arrDepend'].extend([ceflib.vattr(name,d)+'__'+datasetid])


    return sParameter


def read_param(ParamList,idx_param_list,sArrData):
    """ Retrieve all necessary data from the CEF files """
    num_param = len(idx_param_list)

    # get list of CEF files to read
    list_cef = set()    # set only contain unique values -> duplicates will be ignored
    for idx in range(num_param):
        list_cef.add(ParamList[idx_param_list[idx]]['cef'])

    # loop on CEF files to read
    for cef in list_cef:
        # check that there is still data to read from the file
        if [el['paramid'] for ind, el in enumerate(ParamList) if el['cef'] == cef and el['in_memory'] == 0]:

            # check that CEF exists
            print(cef)
            if os.path.isfile(cef):
                with gb.ceflib_lock:

                    # read cef file
                    #ceflib.verbosity(0)
                    ret = ceflib.read(cef)
                    datasetid = (ceflib.meta("DATASET_ID"))[0]

                    # read time parameter first
                    # get list of record indexes within the time span (we request a larger time interval to accounts for delta+/delta- but need to only keep the valid data to calculate number of points ...)
                    [sParam_time,idx_valid_record,paramid] = get_time_param(datasetid)
                    sArrData.append(deepcopy(sParam_time))
                    ind = [ind for ind,el in enumerate(ParamList) if el['paramid'] == paramid]
                    ParamList[ind[0]]['in_memory'] = 1

                    # store all the data that will be required for these cef (for any plot)
                    for ind, param in [(ind, el['paramid']) for ind, el in enumerate(ParamList) if el['cef'] == cef and el['in_memory'] == 0]:
                        print("read parameter ", param)
                        sParam = get_param(param,idx_valid_record)
                        sArrData.append(deepcopy(sParam))
                        ParamList[ind]['in_memory'] = 1
	
                        # check if the parameter dependencies are in memory otherwise read them
                        if sParam['num_depend'] > 0:
                            for depend in sParam['arrDepend']:
                                # check if parameter is already in the list otherwise add it and read it
                                if depend not in [el['paramid'] for ind, el in enumerate(ParamList)]:
                                    print("add new parameter to the list: ", depend)
                                    sParam_depend = get_param(depend,idx_valid_record)
                                    sArrData.append(deepcopy(sParam_depend))
                                    ParamList.append({'paramid':depend,'last_idx':ParamList[ind]['last_idx'],'idx_list':ParamList[ind]['idx_list'],'in_cef':1,'cef':cef,'in_memory':1})


                    # if not already done, store the min/max time resolution
                    # ignore caveat parameters (time ranges)
                    if '_CQ_' not in cef and '_CT_' not in cef: # ignore CT for TMMODE dataset but may cause issue for other datasets later on ?
                        for resolution in ["MIN_TIME_RESOLUTION","MAX_TIME_RESOLUTION"]:
                            # get the last_idx and list_idx of all the param using this cef file
                            last_idx = max([el['last_idx'] for (ind,el) in enumerate(ParamList) if el['cef'] == cef])
                            idx_list = np.concatenate([el['idx_list'] for (ind,el) in enumerate(ParamList) if el['cef'] == cef])

                            if not [el['paramid'] for ind, el in enumerate(ParamList) if el['cef'] == cef and el['in_memory'] == 0 and el['paramid'] == resolution+"__"+datasetid]:
                                sParam_res = mkp.make_sParameter()
                                sParam_res['paramid'] = resolution+"__"+datasetid
                                sParam_res['arrData'] = ceflib.meta(resolution)[0]
                                sArrData.append(deepcopy(sParam_res))
                                ParamList.append({'paramid':resolution+"__"+datasetid,'last_idx':last_idx,'idx_list':idx_list,'in_cef':1,'cef':cef,'in_memory':1})

                    # close cef file
                    ceflib.close()

            else:
                print("WARNING: input file doesn't exists ... create empty parameters: " + cef)

                for ind, param in [(ind, el['paramid']) for ind, el in enumerate(ParamList) if el['cef'] == cef and el['in_memory'] == 0]:

                    sParameter = mkp.make_sParameter()
                    sParameter['paramid'] = param
                    sArrData.append(deepcopy(sParameter))
                    ParamList[ind]['in_memory'] = 1

                # add fake min/max time resolution
                name,datasetid = param.split("__")
                for resolution in ["MIN_TIME_RESOLUTION","MAX_TIME_RESOLUTION"]:
                    # get the last_idx and list_idx of all the param using this cef file
                    last_idx = max([el['last_idx'] for (ind,el) in enumerate(ParamList) if el['cef'] == cef])
                    idx_list = np.concatenate([el['idx_list'] for (ind,el) in enumerate(ParamList) if el['cef'] == cef])

                    if not [el['paramid'] for ind, el in enumerate(ParamList) if el['cef'] == cef and el['in_memory'] == 0 and el['paramid'] == resolution+"__"+datasetid]:
                        sParam_res = mkp.make_sParameter()
                        sParam_res['paramid'] = resolution+"__"+datasetid
                        sParam_res['arrData'] = 0
                        sArrData .append(deepcopy(sParam_res))
                        ParamList.append({'paramid':resolution+"__"+datasetid,'last_idx':last_idx,'idx_list':idx_list,'in_cef':1,'cef':cef,'in_memory':1})




def store_values(ParamList,sArrData):
    """ Store all fixed values from the XML files in sArrData """

    #for ind, param in [(ind, el['paramid']) for ind, el in enumerate(ParamList) if el['fix'] == 1 and el['in_memory'] == 0]:
    for ind, param in [(ind, el['paramid']) for ind, el in enumerate(ParamList) if el['in_memory'] == 0 and el['fix'] == 1]:

        sParam = mkp.make_sParameter()
        sParam['paramid'] = param
        sParam['arrData'] = ParamList[ind]['value'] if ParamList[ind]['value'] != '' else ParamList[ind]['range']

        sArrData.append(deepcopy(sParam))
        ParamList[ind]['in_memory'] = 1



def update_values(sArrData,UpdateList):
    ind = 0
    for upd in UpdateList:
        print(upd)
        param = upd['paramid']
        # find position of parameter in sArrData
        idx = [ind2 for (ind2,el) in enumerate(sArrData) if el['paramid'] == param][0]
        # update value - convert to array if needed
        sArrData[idx]['arrData'] = np.array([float(i) for i in UpdateList[ind]['value'].split(",")])
        ind += 1


