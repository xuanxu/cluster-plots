
import numpy as np
import global_vars as glb
import lib_time as lt
import lib_aux as la
import lib_reshape_data as lrd
import make_param as mkp


from copy import deepcopy

def time_average(sProc,lParam,arrData):
    print("In time_average")
    res=lt.get_time(sProc,lParam,arrData,'average')

def time_spec_average(sProc,lParam,arrData):
    print("In time_spec_average")
    res=lt.get_time(sProc,lParam,arrData,'spec_average')

def time_minmax(sProc,lParam,arrData):
    print("In time_minmax")
    res=lt.get_time(sProc,lParam,arrData,'minmax')

def time_interp_spec(sProc,lParam,arrData):
    print("In time_interp_spec")
    res=lt.get_time(sProc,lParam,arrData,'interp_spec')

def time_none(sProc,lParam,arrData):
    print("In time_none")
    res=lt.get_time(sProc,lParam,arrData,'none')

def data_minmax(sProc,lParam,arrData):
    print("In data_minmax")
    res=lrd.process_2D(sProc,lParam,arrData,'minmax')

def data_interpol(sProc,lParam,arrData):
    print("In data_interpol")
    res=lrd.process_2D(sProc,lParam,arrData,'interpolate')

def data_average(sProc,lParam,arrData):
    print("In data_average")
    res=lrd.process_2D(sProc,lParam,arrData,'average')

def data_none(sProc,lParam,arrData):
    print("In data_none")
    res=lrd.process_2D(sProc,lParam,arrData,'none')

def spectro_average(sProc,lParam,arrData):
    print("In spectro_average")
    #res=lrd.process_3D(sProc,lParam,arrData,'average')
    res=lrd.process_3D(sProc,lParam,arrData,'spec_average')

def extract_comp(sProc,lParam,arrData):
    print("In extract_comp")
    res=lrd.ext_comp(sProc,lParam,arrData,'average')

def spectro_interpol(sProc,lParam,arrData):
    print("In spectro_interpol")
    res=lrd.process_3D(sProc,lParam,arrData,'interpolate')

def average_dim(sProc,lParam,arrData):
    print("In average_dim")
    res=lrd.av_dim(sProc,lParam,arrData)

def resolve_nrj(sProc,lParam,arrData):
    print("In resolve_nrj")
    res=lrd.reso_nrj(sProc,lParam,arrData)

def reshape_nrj(sProc,lParam,arrData):
    print("In reshape_nrj")
    res=lrd.resh_nrj(sProc,lParam,arrData)

def nrj_to_log(sProc,lParam,arrData):
    print("In nrj_to_log")
    res=lrd.nrj_to_log(sProc,lParam,arrData)

def merge(sProc,lParam,arrData):
    print("In merge")
    res=lrd.merge_data(sProc,lParam,arrData)

def merge_2d(sProc,lParam,arrData):
    print("In merge 2D")
    res=lrd.merge_2d(sProc,lParam,arrData)

def efw_potential(sProc,lParam,arrData):
    print("In efw_potential")
    res=sc_potential(sProc,lParam,arrData)

def fgm_gyro(sProc,lParam,arrData):
    print("In fgm_gyro")
    res=gyro_freq(sProc,lParam,arrData)

def filter_fix_nrj(sProc,lParam,arrData):
    print("In filter_fix_nrj")
    res=lrd.filter_fixed_nrj(sProc,lParam,arrData)

def interp_fix_nrj(sProc,lParam,arrData):
    print("In filter_fix_nrj")
    res=lrd.interpolate_fixed_nrj(sProc,lParam,arrData)

def filter_zeroes(sProc,lParam,arrData):
    print("In filter_zeroes")
    res=la.filter_zero(sProc,lParam,arrData)

def filter_dim(sProc,lParam,arrData):
    print("In filter_dim")
    res=lrd.filt_dim(sProc,lParam,arrData)

def calc_angle(sProc,lParam,arrData):
    print("In calc_angle")
    res=lrd.calc_angle(sProc,lParam,arrData)

def total_power(sProc,lParam,arrData):
    print("In total_power")
    res=lrd.total_power(sProc,lParam,arrData)

def distance(sProc,lParam,arrData):
    print("In distance")
    res=lrd.distance(sProc,lParam,arrData)

def cluster_distance(sProc,lParam,arrData):
    print("In cluster distance")
    res=lrd.cluster_distance(sProc,lParam,arrData)

def convert_re(sProc,lParam,arrData):
    print("In cluster distance")
    res=convert_re(sProc,lParam,arrData)

def zero_to_nan(sProc,lParam,arrData):
    print("In zero_to_nan")
    res=lrd.zero_to_nan(sProc,lParam,arrData)

def calc_modulo(sProc,lParam,arrData):
    print("In calc_modulo")
    res=lrd.calc_modulo(sProc,lParam,arrData)

def calc_itp_complex(sProc,lParam,arrData):
    print("In calc_itp_complex")
    res=lrd.calc_itp_complex(sProc,lParam,arrData)

def calc_itp(sProc,lParam,arrData):
    print("In calc_itp")
    res=lrd.calc_itp(sProc,lParam,arrData)

def param_average(sProc,lParam,arrData):
    print("In param_average")
    res=lrd.param_average(sProc,lParam,arrData)

def convert_pef(sProc,lParam,arrData):
    print("In cnvert_pef")
    res=lrd.convert_pef(sProc,lParam,arrData) 

def data_offset(sProc,lParam,arrData):
    print("In data_offset")
    res=data_offset(sProc,lParam,arrData)

def edi_code(sProc,lParam,arrData):
    print("In edi_code")
    res=lrd.edi_code(sProc,lParam,arrData)

def edi_bitmask(sProc,lParam,arrData):
    print("In edi_bitmask")
    res=lrd.edi_bitmask(sProc,lParam,arrData)

def efw_bitmask(sProc,lParam,arrData):
    print("In efw_bitmask")
    res=lrd.efw_bitmask(sProc,lParam,arrData)

def rap_mode(sProc,lParam,arrData):
    print("In rap_mode")
    res=rap_mode(sProc,lParam,arrData)

def rap_int_time(sProc,lParam,arrData):
    print("In rap_int_time")
    res=lrd.rap_int_time(sProc,lParam,arrData)

def rap_hv(sProc,lParam,arrData):
    print("In rap_hv")
    res=lrd.rap_hv(sProc,lParam,arrData)

def get_time_range(sProc,lParam,arrData):
    print("In get_time_range")
    res=lt.get_time_range(sProc,lParam,arrData)

def get_caveat(sProc,lParam,arrData):
    print("In get_caveat")
    res=lrd.get_caveat(sProc,lParam,arrData)

def insert_nan_dboundary(sProc,lParam,arrData):
    print("In insert_nan_dboundary")
    res=lrd.insert_nan_dboundary(sProc,lParam,arrData)

def sta_mode_change(sProc,lParam,arrData):
    print("In sta_mode_change")
    res=lrd.sta_mode_change(sProc,lParam,arrData)

def sta_extract_mode(sProc,lParam,arrData):
    print("In sta_extract_mode")
    res=lrd.sta_extract_mode(sProc,lParam,arrData)

def filter_mode(sProc,lParam,arrData):
    print("In filter_mode")
    res=lrd.filter_mode(sProc,lParam,arrData)

def qzc_counts_per_second(sProc,lParam,arrData):
    print("In qzc_counts_per_seconds")
    res=la.qzc_counts_per_second(sProc,lParam,arrData)




def process_data(sProc,lParam,arrData):

    # list of implemented functions:
    list_process = {'data_average':         data_average,
                    'data_minmax':          data_minmax,
                    'data_interpol':        data_interpol,
                    'data_none':            data_none,
                    'time_minmax':          time_minmax,
                    'time_average':         time_average,
                    'time_spec_average':    time_spec_average,
                    'time_interp_spec':     time_interp_spec,
                    'get_time':             time_none,
                    'spectro_average':      spectro_average,
                    'extract_comp':         extract_comp,
                    'spectro_interpol':     spectro_interpol,
                    'average_dim':          average_dim,
                    'merge':                merge,
                    'merge_2d':             merge_2d,
                    'resolve_nrj':          resolve_nrj,
                    'reshape_nrj':          reshape_nrj,
                    'nrj_to_log':           nrj_to_log,
                    'efw_potential':        efw_potential,
                    'fgm_gyro':             fgm_gyro,
                    'filter_fix_nrj':       filter_fix_nrj,
                    'interp_fix_nrj':       interp_fix_nrj,
                    'filter_zeroes':        filter_zeroes,
                    'filter_dim':           filter_dim,
                    'calc_angle':           calc_angle,
                    'total_power':          total_power,
                    'distance':             distance,
                    'convert_re':           convert_re,
                    'cluster_distance':     cluster_distance,
                    'zero_to_nan':          zero_to_nan,
                    'calc_modulo':          calc_modulo,
                    'calc_itp_complex':     calc_itp_complex,
                    'calc_itp':             calc_itp,
                    'param_average':        param_average,
                    'convert_pef':          convert_pef,
                    'data_offset':          data_offset,
                    'edi_code':             edi_code,
                    'edi_bitmask':          edi_bitmask,
                    'efw_bitmask':          efw_bitmask,
                    'rap_mode':             rap_mode,
                    'rap_int_time':         rap_int_time,
                    'rap_hv':               rap_hv,
                    'get_time_range':       get_time_range,
                    'get_caveat':           get_caveat,
                    'sta_mode_change':      sta_mode_change,
                    'sta_extract_mode':     sta_extract_mode,
                    'filter_mode':          filter_mode,
                    'insert_nan_dboundary': insert_nan_dboundary,
                    'qzc_counts_per_second': qzc_counts_per_second

                }

    # make sure processing hasn't already been performed => all output arguments already in memory
    list_output = [d['paramid'] for d in sProc['sArgument'] if d['type'].lower() == "output"]
    list_inmem = [d['paramid'] for d in lParam if d['in_memory'] == 1]

    if not all(item in list_inmem for item in list_output):
        # check if processing is in the list and run the corresponding function
        if (sProc['name']).lower() in list_process:
            list_process[(sProc['name']).lower()](sProc,lParam,arrData)
        else:
            raise Exception("Method %s not implemented" % (sProc['name']).lower())



##################################################################################################################################


def sc_potential(sProc,lParam,arrData):
    # calculate EFW modified spacecraft potential
    # 0.86-1.24*SCPOT

    # INPUT_1 is the EFW data to process


    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        data_sc = np.log10(0.86-1.24*sData['arrData'])

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_sc
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1




##################################################################################################################################

def gyro_freq(sProc,lParam,arrData):
    # calculate fgm gyrofrequency
    # (Bmag*1e-9*1.602e-19)/(2*Pi*9.109e-31)
    # data overplotted on log scale so take log of data

    # INPUT_1 is the FGM data to process


    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        data_gyro = np.log10((1e-9*1.602e-19*sData['arrData'])/(2*np.pi*9.109e-31))

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data_gyro
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1



##################################################################################################################################

def data_offset(sProc,lParam,arrData):
    # apply offset to parameter

    # INPUT_1 is the data to process
    # value gives the offset to apply

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:
        offset = float(sProc['value'])
        data = sData['arrData'] + offset

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1


##################################################################################################################################

def rap_mode(sProc,lParam,arrData):
    # rapid mode

    # INPUT_1 is the rap data to process
    # value is A or B

    # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        if sProc['value'] == 'A':
            data = deepcopy(sData['arrData'])
            data[np.where(data > 3)] = 3
        else:
            data = deepcopy(sData['arrData'])-1
            data[np.where(data < 1)] = 0
            data[np.where(data > 2)] -= 1

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1



##################################################################################################################################

def convert_re(sProc,lParam,arrData):
    # convert position from km to earth radii

    # INPUT_1 is the data to convert

   # extract data to process
    idx_input = next((ind for (ind, el) in enumerate(sProc['sArgument']) if el['alias'] == "INPUT_1"), -1)
    input_1 = sProc['sArgument'][idx_input]['paramid']
    sData = [el for (ind,el) in enumerate(arrData) if el['paramid'] == input_1][0]

    # check if output already exists in memory otherwise process it
    output_1 = [d['paramid'] for d in sProc['sArgument'] if d['alias'] == "OUTPUT_1"][0]
    if [d['paramid'] for d in lParam if d['paramid'] == output_1 and d['in_memory'] == 0]:

        data = deepcopy(sData['arrData'])
        data /= 6371.2

        #  store resolved data
        sDataPlot = mkp.make_sParameter()
        sDataPlot['arrData'] = data
        sDataPlot['paramid'] = output_1
        arrData.append(deepcopy(sDataPlot))

        idx_output = next((ind for (ind, el) in enumerate(lParam) if el['paramid'] == output_1), -1)
        lParam[idx_output]['in_memory'] = 1






