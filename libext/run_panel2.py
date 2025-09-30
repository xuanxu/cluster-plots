import gen_panels as gp
import sys, os
import getopt
import subprocess
import numpy as np
import os
from os.path import join, dirname
import gzip
from astropy.time import Time, TimeDelta

import threading
import getpass
import time
import json

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

ROOT_PATH= dirname(__file__)

# threading
#-----------
class GetCEFThread(threading.Thread):

    def __init__(self, value):

        threading.Thread.__init__(self)
        self.value = value

    def run(self):
        # notre fonction
        result = 0
        list_arg = self.value
        self.value = get_data(list_arg)

##################################################################################################################
def is_empty_gzip_file(filename):
    with gzip.open(filename, 'rb') as f:
        data = f.read(1)

    return not len(data)

##################################################################################################################

def get_data(list_arg):

    [dataset, file_dir, strDate, n_start, n_stop] = list_arg

    cef_file = join(file_dir, dataset + "__" + strDate + "_V00.cef.gz")
    download_data_csa(dataset, n_start, n_stop, file_dir)

    print("* CEF file:", cef_file);

    return cef_file

#################################################################################################################################

def download_data_csa(ds, start_date, stop_date, file_dir):
    print("DOWNLOADING DATA FROM CSA")
    cmd = ROOT_PATH+"/download_data_csa "+ds+" "+start_date+" "+stop_date+" "+file_dir
    #print(cmd)
    subprocess.call(cmd, shell=True)

#################################################################################################################################

def run_panel2(list_panel, start, stop, date_orig, json_file_name, cef_path, output_type, plot_name, upd_list, list_zeroes):
    file_dir =  join(dirname(__file__), "results", "cef_files")
    xml_dir = join(dirname(__file__), "xml")
    json_file = join(dirname(__file__), "results", "json_charts", json_file_name)

    stopo = (date_orig.split('/'))[1]
    starto = (date_orig.split('/'))[0]

    # find XML files and extract the list of datasets to read
    flag_first = 1
    list_dataset = set()    # set only contain unique values -> duplicates will be ignored

    if list_zeroes is not None:
        z_list = list_zeroes.split(",")
    else:
        z_list = []

    for panel in list_panel.split(","):

        panel = panel.strip()
    
        # check if the zeroes need to be filtered out
        if "zero_Ci"+panel[2:] in z_list:
            panel = panel[:len(panel) - 4] + "_nozeroes_CAA"

        # for FGM panels need to select the XML depending on the input time range
        if '_FGM_BGSE' in panel or '_FGM_BISR2' in panel:
            # check time interval in minutes
            interval = (Time(stop) - Time(start)) * 60 * 24
            tmp = panel.split('FGM')
            if interval <= 10:
                panel_fgm = tmp[0]+'FGM_FULL'+tmp[1]
            elif interval <= 60:
                if panel[0] == 'C':
                    panel_fgm = tmp[0]+'FGM_5VPS'+tmp[1]
                else:
                    panel_fgm = tmp[0]+'FGM_FULL'+tmp[1]
            else:
                panel_fgm = tmp[0]+'FGM_SPIN'+tmp[1]

            xml = join(xml_dir, "fgm", "CAA_PANEL_"+panel_fgm+".XML")    
        else:
            xml = join(xml_dir, "CAA_PANEL_"+panel+".XML")

        with open(xml, 'rt') as f:
            tree = ET.parse(f)

        panel = tree.getroot()

        for did in panel.iter('DATASETID'):
            list_dataset.add(did.text)

        if flag_first == 1:
            list_xml = xml
            flag_first = 0
        else:
            list_xml = list_xml + "," + xml


    # request a file slightly larger (+/- 5 minutes) => would require a better handling of the rebining functions (would have to ignore # points outside of the plot interval ... idem when checking if there are data to plot)
    n_start = (Time(start) - TimeDelta(300.0, format='sec')).isot+'Z'
    n_stop = (Time(stop) + TimeDelta(300.0, format='sec')).isot+'Z'

    n_starto = (Time(starto) - TimeDelta(300.0, format='sec')).isot+'Z'
    n_stopo = (Time(stopo) + TimeDelta(300.0, format='sec')).isot+'Z'

    strDate = n_start[0:4]+n_start[5:7]+n_start[8:10]+"_"+n_start[11:13]+n_start[14:16]+n_start[17:19]+"_"+n_stop[0:4]+n_stop[5:7]+n_stop[8:10]+"_"+n_stop[11:13]+n_stop[14:16]+n_stop[17:19]

    # va stocker les threads qu'on va lancer.
    threadList = []

    for dataset in list_dataset:
        arg_list = [dataset, file_dir, strDate, n_start, n_stop]
        curThread = GetCEFThread(arg_list)
        curThread.start()	# on lance le thread
        threadList.append(curThread)	# on ajoute le thread a la list


    # maintenant qu'on a tout lance, on recupere tout!
    list_cefs = []

    for curThread in threadList :

        curThread.join()	# on attend que le thread ait fini
        result = curThread.value	# on recupere sa valeur
        list_cefs.append(result)


    list_cef = ",".join(list_cefs)

    startTime = time.time()
    res = gp.gen_panels(list_xml,list_cef,list_panel,start,stop,upd_list,json_file,list_zeroes,output_type=output_type,plot_name=plot_name)
    print('LIST_XML: ',list_xml)
    print('LIST_CEF: ',list_cef)
    print('gen_panels:', time.time() - startTime)

    return res


####################################################################################################################################


def main(argv):

    USAGE = """\nUSAGE: \n
           python run_panel2.py (-p | --panel) panel (-b | --begin) begin (-e | --end) stop (-n | --name) name  (-u | --update) upd (-o | --orig) orig  (-t | --output-type) type (-f | --cef-path) tmp_path  (-z | --zeroes) zeroes \n
           eg: python run_panel2.py -b '2001-03-17T00:00:00Z' -e '2001-03-18T00:00:00Z' -p 'C1_CG_EFW_L3_P_CAA' -n 'test.ps' -t 'echarts' -j 'test.json' -o '2001-03-17T00:00:00Z/2001-03-18T00:00:00Z' -u '[{"paramid":"Sweep_Energy_medium__C3_CP_PEA_PITCH_FIX_DEFlux","value":"58.2,800"}]'\n
             begin/end :   interval of the plot
             orig :        interval of the input cef file to request (the app adds 5 minutes at the beginning/end of the requested interval)
             tmp_path:	   path to store the cef file
             output_type : for now only 'hc' (echarts -> json output) is implemented
             name :        ignored, ps plotting not implemented 
             zeroes:	   filter zeroes for corresponding panel ?
             upd :         list in JSON format of params and values sent by the server when updating filter information \n  """

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:b:e:o:n:t:f:j:u:z:h', ['panel=', 'begin=', 'end=', 'orig=', 'name=', 'output_type=', 'cef_path=', 'json=', 'update=', 'zeroes=', 'help'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        print(USAGE)
        sys.exit(2)

    output_type = 'echarts'
    upd_list = []
    zeroes_list = ''
    name = ''
    json_file = 'test.json'
    date_orig = ''
    cef_path = '/tmp/'

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE)
            sys.exit(2)
        elif opt in ('-b', '--begin'):
            start = arg
        elif opt in ('-e', '--end'):
            stop = arg
        elif opt in ('-o', '--orig'):
           date_orig = arg
        elif opt in ('-p', '--panel'):
            list_panel = arg
        elif opt in ('-t', '--output_type'):
            output_type = arg
        elif opt in ('-f', '--cef-path'):
            cef_path = arg
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-j', '--json'):
            json_file = arg
        elif opt in ('-u', '--update'):
            upd_list = json.loads(arg)
        elif opt in ('-z', '--zeroes'):
            zeroes_list = arg
        else:
            print(USAGE)
            sys.exit(2)

    if date_orig == '':
        date_orig = start + '/' + stop 

    run_panel2(list_panel, start, stop, date_orig, json_file, cef_path, output_type, name, upd_list, zeroes_list)


if __name__ == "__main__":
    main(sys.argv[1:])
