import numpy as np
import read_panel_xml as rpx
import read_param_cef as rpc
import process_data as prd
import ceflib
import astropy.time as ap
#import matplotlib.pyplot as plt
import plot_data as pld
import lib_highcharts as lhc
from matplotlib.dates import DateFormatter
import getopt, sys
from astropy.utils.misc import JsonCustomEncoder
import os, os.path

import json
#import ujson as json
#import simplejson as json

import time

import global_vars as glb



def gen_panels(list_xml,list_cef,list_panels,start,stop,upd_list,json_file,list_zeroes,output_type,plot_name):
    """ Main routine for panel generation """

    if len(upd_list) > 0:
        flag_update = 1
    else:
        flag_update = 0

    glb.date_start_iso = start
    glb.date_stop_iso = stop

    glb.date_start_jul = (ap.Time(glb.date_start_iso, format='isot')).mjd
    glb.date_stop_jul = (ap.Time(glb.date_stop_iso, format='isot')).mjd

    glb.date_start_milli = ceflib.isotime_to_milli(glb.date_start_iso)
    glb.date_stop_milli = ceflib.isotime_to_milli(glb.date_stop_iso)

#**********************
#*** READ XML FILES ***
#**********************
    # create array of xml and cef files
    arrXML = [i for i in list_xml.split(",")]
    num_panels = len(arrXML)
    arrCEF = [i for i in list_cef.split(",")]
    num_cef = len(arrCEF)

    print("num_panels: ",num_panels)
    print("num_cef: ", num_cef)

    # create array of structures panel -> sArrPanel
    # create list of parameters to read and last panel the parameter appears in -> sArrParam
    sArrPanel = [dict() for x in range(num_panels)]
    sArrParam = []

    #sArrParam = [{'paramid':'Spacecraft_potential_minmax__C1_CP_EFW_L3_P','last_idx':8,'idx_list':[8],'in_cef':0,'cef':'cef'}]

    # read all xml files and populate sArrPanel and sArrParam
    for pan_idx in range(num_panels):
        sArrPanel[pan_idx],paramlist = rpx.read_panel_xml(arrXML[pan_idx],arrCEF)
        # if the parameter is not yet in the sArrParam append it to the list
        # otherwise update the id of the last panel
        num_param = len(paramlist)
        for p in range(num_param):
            param = paramlist[p]['paramid']
            idx = next((ind for (ind, el) in enumerate(sArrParam) if el['paramid'] == param), -1)
            if idx == -1:
                sArrParam.append({'paramid':param,'last_idx':pan_idx,'idx_list':np.array([pan_idx]),'in_cef':paramlist[p]['in_cef'],'cef':paramlist[p]['cef'],'in_memory':0,'fix':paramlist[p]['fix'],'value':paramlist[p]['value'],'range':paramlist[p]['range']})
            else:
                sArrParam[idx]['last_idx'] = pan_idx
                sArrParam[idx]['idx_list'] = np.append(sArrParam[idx]['idx_list'],[pan_idx])

    sArrData = []


    # store constant range/values for processing
    rpc.store_values(sArrParam,sArrData)

    # update values if required
    # check if we have some updates (button) to do
    print(upd_list)
    if flag_update == 1:
        print('update')
        rpc.update_values(sArrData,upd_list)
    else:
        print('no update to be performed')

#*****************************
#*** START PLOT PRODUCTION ***
#*****************************


#**********************
#*** LOOP ON PANELS ***
#**********************

    json_panel_arr = []

    for pan_idx in range(num_panels):
        sPanel = sArrPanel[pan_idx]
        label = sPanel["info"]

        # get list of CEF params necessary to produce the panel
        idx_param_list = [ind for ind, el in enumerate(sArrParam) if (pan_idx in el['idx_list']) and (el['in_cef'] == 1)]

        # read CEF and get params data/metadata
        rpc.read_param(sArrParam,idx_param_list,sArrData) if len(idx_param_list) >= 0 else []


        # LOOP ON SUBPANELS
        num_subpan = sPanel['num_subpan']
        json_subpan_arr = []
        sub_number = 1
        for subp_idx in range(num_subpan):
            sSubpanel = sPanel['sSubpanel'][subp_idx]
            order = sSubpanel['order']
            pos = str(num_panels)+'1'+str(sub_number)

            #LOOP ON PLOTS
            num_plots = sSubpanel['num_plots']
            for plot_idx in range(num_plots):
                sPlot = sSubpanel['sPlot'][plot_idx]

                # LOOP ON PROCESSINGS
                num_proc = sPlot['num_proc']

                print('NUM_PROC: ', num_proc)

                #sorted_sPlot = sorted(sPlot['sProcessing'],key=lambda k: k['order'])
                for proc_idx in range(num_proc):
                    startTime = time.time()
                    sProc = sPlot['sProcessing'][proc_idx]
                    prd.process_data(sProc,sArrParam,sArrData)
                    print('process:', time.time() - startTime)

                if output_type == "xwindow" or output_type == "png":
                    #plot data
                    pld.plot_data(sPlot,sArrData,pos)

            startTime = time.time()
            if output_type == "highcharts":
                json_subpan_arr.append(lhc.create_json(sSubpanel,sArrData))
            sub_number = sub_number+1
            print('lib_highcharts:', time.time() - startTime)

        if output_type == "highcharts":
            # add json to panel array
            div = 'div'+str(pan_idx)

            if len(sPanel['sButton']) > 0:
                # add button info
                sPanel['sButton'][0]['div'] = div
                #json_subpan_arr.append({'button':sPanel['sButton'][0]})           
                json_panel_arr.append({'div': 'div'+str(pan_idx), 'num_subpanels': num_subpan, 'label': label, 'panel_type': sPanel['panel_type'], 'xtitle': 'UT', 'subpanels':json_subpan_arr, 'button':sPanel['sButton'][0]})
            else:
                json_panel_arr.append({'div': 'div'+str(pan_idx), 'num_subpanels': num_subpan, 'label': label, 'panel_type': sPanel['panel_type'], 'xtitle': 'UT', 'subpanels':json_subpan_arr})



    # add the time labels to the x axis of the last panel
    if output_type == "xwindow" or output_type == "png":
        formatter = DateFormatter('%y-%m-%d\n%H:%M')
        plt.gcf().axes[-1].xaxis.set_major_formatter(formatter)
        labels = plt.gcf().axes[-1].get_xticklabels()
        plt.setp(labels, rotation=30)


    if output_type == "highcharts":
        startTime = time.time()

        json_data = {'start':glb.date_start_iso,'stop':glb.date_stop_iso,'panels':list_panels,'zeroes':list_zeroes,'num_panels':num_panels,'panels_arr':json_panel_arr,'list_cef':list_cef}

        print(json_file)

        json_chart_path = os.path.dirname(json_file)
        os.makedirs(json_chart_path, exist_ok=True)

        with open (json_file,'w') as f:
            json.dump(json_data,f,sort_keys=True, indent=4, cls=JsonCustomEncoder)
            #json.dump(json_data,f)

        print('create json:', time.time() - startTime)

    print('output_type:', output_type)

    # create the plot
    if output_type == "xwindow":
        plt.show()
    elif output_type == "png":
        glb.fig.savefig(plot_name)

    return num_panels





####################################################################################################################################

def main(argv):

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'x:c:b:e:o:n:u:h', ['xml=', 'cef=', 'begin=', 'end=', 'output_type=', 'name=', 'update=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-b', '--begin'):
            start = arg
        elif opt in ('-e', '--end'):
            stop = arg
        elif opt in ('-x', '--xml'):
            xml_path = arg
        elif opt in ('-c', '--cef'):
            cef_path = arg
        elif opt in ('-o', '--output_type'):
            output_type = arg
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-u', '--update'):
            upd_list = arg
        else:
            usage()
            sys.exit(2)

    gen_panels(xml_path,cef_path,start,stop,upd_list,output_type,name)


if __name__ == "__main__":
    main(sys.argv[1:])
