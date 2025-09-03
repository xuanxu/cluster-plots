import sys
import os
from os.path import join, dirname
import getopt
import subprocess
import numpy as np
import ceflib
import json
from datetime import datetime, timedelta
from astropy.utils.misc import JsonCustomEncoder


def str_to_num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def run_sc_info(list_ticks, list_info, sc, missionID, start, stop, date_orig, json_file):
    if missionID == '1':
        list_dataset = ['C'+str(sc)+'_JP_AUX_PMP', 'CL_SP_AUX', 'C'+str(sc)+'_CP_AUX_POSGSE_1M']
    else:
        list_dataset = ['D'+str(sc)+'_JP_AUX_PMP', 'D'+str(sc)+'_SP_AUX']

    EarthRadius = 6371.2

    ROOT_PATH = dirname(__file__)
    file_dir = join(ROOT_PATH, "results", "cef_files")
    json_file_path = join(ROOT_PATH, "results", "json_charts", json_file)

    strDate = start[0:4]+start[5:7]+start[8:10]+"_"+start[11:13]+start[14:16]+start[17:19]+"_"+stop[0:4]+stop[5:7]+stop[8:10]+"_"+stop[11:13]+stop[14:16]+stop[17:19]
    stopo = (date_orig.split('/'))[1]
    starto = (date_orig.split('/'))[0]
    strDate_orig = starto[0:4]+starto[5:7]+starto[8:10]+"_"+starto[11:13]+starto[14:16]+starto[17:19]+"_"+stopo[0:4]+stopo[5:7]+stopo[8:10]+"_"+stopo[11:13]+stopo[14:16]+stopo[17:19]

    # calculate time range in seconds
    date_start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
    date_stop = datetime.strptime(stop, "%Y-%m-%dT%H:%M:%SZ")
    delta_sec = (date_stop-date_start).total_seconds()

    # get list of possible ticks for the saved images (as it can be different to the ones displayed on screen)
    if delta_sec > 492480:  # > 5j 16h 48 min => 24h
        delta_t = 86400
    elif delta_sec > 273600:  # > 3j 4h => 12h
        delta_t = 43200
    elif delta_sec > 191520:  # > 2j 5h 12 min => 8h
        delta_t = 28800
    elif delta_sec > 136800:  # > 1j 14h => 6h
        delta_t = 21600
    elif delta_sec > 93636:  # > 1j 2h 36 min => 4h
        delta_t = 14400
    elif delta_sec > 68400:  # > 19h => 3h
        delta_t = 10800
    elif delta_sec > 41040:  # > 11h 24 min => 2h
        delta_t = 7200
    elif delta_sec > 20520:  # > 5h 42 min => 1h
        delta_t = 3600
    elif delta_sec > 10260:  # > 2h 51 min => 30 min
        delta_t = 1800
    elif delta_sec > 5700:  # > 1h 35 min => 15 min
        delta_t = 900
    elif delta_sec > 3420:  # > 57h => 10 min
        delta_t = 600
    elif delta_sec > 1596:  # > 26 min 36s => 5 min
        delta_t = 300
    elif delta_sec > 685:  # > 11 min 25s => 2 min
        delta_t = 120
    elif delta_sec > 342:  # > 5 min 42s => 1 min
        delta_t = 60
    elif delta_sec > 171:  # > 2 min 51 s => 30s
        delta_t = 30
    elif delta_sec > 95:  # > 1 min 35s => 15s
        delta_t = 15
    elif delta_sec > 57:  # > 57s => 10s
        delta_t = 10
    elif delta_sec > 26:
        delta_t = 5
    else:
        delta_t = 2

    # ticks list
    start_day = datetime.strptime(start[0:4]+start[5:7]+start[8:10], "%Y%m%d")
    delta = timedelta(seconds=delta_t)

    start_dt = date_start

    ticks = [ceflib.isotime_to_milli(i) for i in list_ticks]
    while start_dt <= date_stop:
        # add current date to list by converting  it to iso format
        if ceflib.isotime_to_milli(start_dt.isoformat()+"Z") not in ticks:
            ticks.append(ceflib.isotime_to_milli(start_dt.isoformat()+"Z"))
        # increment start date by timedelta
        start_dt += delta

    ticks.sort()

    # retrieve the CEF files
    list_cef = []
    for dataset in list_dataset:
        # check if a "larger" CEF file exists
        cef_file_orig = join(file_dir, dataset + "__" + strDate_orig + "_V00.cef.gz")
        cefmerge_file = dataset + "__" + strDate + "_V00"  # cefmerge adds the .cef"

        if os.path.isfile(cef_file_orig):
            # extract only relevant time interval
            cmd = os.getenv("CEFMERGE") + " " + cef_file_orig + " -t " + start + "/" + stop + " -o " + cefmerge_file + " -O " + file_dir
            subprocess.call(cmd, shell=True)

            cef_file = join(file_dir, cefmerge_file + ".cef")
        else:
            # request file from csa
            cef_file = join(file_dir, dataset + "__" + strDate + "_V00.cef.gz")
            if os.path.isfile(cef_file) is False:
                cmd = ROOT_PATH + "/download_data_csa " + dataset + " " + start + " " + stop + " " + file_dir
                subprocess.call(cmd, shell=True)

        list_cef.append(cef_file)

    # remove Z from ISO time for js conversion
    # sc_info = [{'name': 'axis_ticks', 'data': [(ceflib.milli_to_isotime(x,3))[:-1] for x in ticks]}]
    sc_info = [{'name': 'axis_ticks', 'data': [(ceflib.milli_to_isotime(x, 3)) for x in ticks]}]

    if 'X' in list_info or 'Y' in list_info or 'Z' in list_info:
        # get SC position info from POSGSE
        sc_pos_tag = 'sc_r_xyz_gse'
        time_tag = 'time_tags'

        # read cef file
        cef = list_cef[2]
        itp_data = np.empty((len(ticks), 3))
        itp_data[:] = np.nan

        if os.path.isfile(cef):
            # read cef file
            ceflib.verbosity(0)
            ceflib.read(cef)

            data = np.array([el/EarthRadius for el in ceflib.var(sc_pos_tag)])
            time = np.array(ceflib.var(time_tag))
            fillval = str_to_num(ceflib.vattr(sc_pos_tag, "FILLVAL"))
            idx_fill = np.where(data == fillval)
            if idx_fill[0].any():
                data[idx_fill] = np.nan

            # interpolate to match ticks
            for n in range(3):
                # itp_data[:,n] = 10*(np.around(np.interp(ticks,time,np.squeeze(data[:,n])))/10)
                itp_data[:, n] = np.interp(ticks, time, np.squeeze(data[:, n]))

                ceflib.close()

        # replace Nan with None for javascript
        itp_data = np.array(np.where(np.isnan(itp_data), None, itp_data))
        if 'X' in list_info:
            sc_info.append({'name': 'X (GSE,Re)', 'data': itp_data[:, 0]})
        if 'Y' in list_info:
            sc_info.append({'name': 'Y (GSE,Re)', 'data': itp_data[:, 1]})
        if 'Z' in list_info:
            sc_info.append({'name': 'Z (GSE,Re)', 'data': itp_data[:, 2]})

    if 'r' in list_info:
        # get SC distance info from SP
        sc_pos_tag = 'sc_r_xyz_gse'
        sc_diff_tag = 'sc_dr'+str(sc)+'_xyz_gse'
        time_tag = 'time_tags'

        # get SC min/max distance info from SP
        sc_min_tag = 'sc_dr_min'
        sc_max_tag = 'sc_dr_max'

        # read cef file
        cef = list_cef[1]
        itp_data = np.empty(len(ticks))
        itp_data[:] = np.nan

        if os.path.isfile(cef):
            # read cef file
            ceflib.verbosity(0)
            ceflib.read(cef)

            data1 = np.array(ceflib.var(sc_pos_tag))

            time = np.array(ceflib.var(time_tag))

            fillval = str_to_num(ceflib.vattr(sc_pos_tag, "FILLVAL"))
            idx_fill = np.where(data1 == fillval)
            if idx_fill[0].any():
                data1[idx_fill] = np.nan

            if missionID == 1:
                data_min = np.array(ceflib.var(sc_min_tag))
                fillval = str_to_num(ceflib.vattr(sc_min_tag, "FILLVAL"))
                idx_fill = np.where(data_min == fillval)
                if idx_fill[0].any():
                    data_min[idx_fill] = np.nan

                data_max = np.array(ceflib.var(sc_max_tag))
                fillval = str_to_num(ceflib.vattr(sc_max_tag, "FILLVAL"))
                idx_fill = np.where(data_max == fillval)
                if idx_fill[0].any():
                    data_max[idx_fill] = np.nan

                data2 = np.array(ceflib.var(sc_diff_tag))
                fillval = str_to_num(ceflib.vattr(sc_diff_tag, "FILLVAL"))
                idx_fill = np.where(data2 == fillval)
                if idx_fill[0].any():
                    data2[idx_fill] = np.nan

            # calculate distance:
            if missionID == 1:
                data = data1+data2
            else:
                data = data1

            data = np.sqrt(np.power(data[:, 0], 2)+np.power(data[:, 1], 2)+np.power(data[:, 2], 2))/EarthRadius

            # interpolate to match ticks
            itp_data = np.around(np.interp(ticks, time, data), decimals=1)

            if missionID == 1:
                data_min = np.around(np.interp(ticks, time, data_min), decimals=1)
                data_max = np.around(np.interp(ticks, time, data_max), decimals=1)

            ceflib.close()

        # replace Nan with None for javascript
        itp_data = np.array(np.where(np.isnan(itp_data), None, itp_data))
        sc_info.append({'name': 'r', 'data': itp_data})

    if 'il' in list_info or 'mlt' in list_info or 'l' in list_info:

        # get IL/MLT/L info from PMP
        il_tag = 'Invar_Lat'
        mlt_tag = 'Mag_Local_time'
        l_tag = 'L_value'
        time_tag = 'time_tags'

        # read cef file
        cef = list_cef[0]
        itp_il_data = np.empty(len(ticks))
        itp_il_data[:] = np.nan
        itp_mlt_data = np.empty(len(ticks))
        itp_mlt_data[:] = np.nan
        itp_l_data = np.empty(len(ticks))
        itp_l_data[:] = np.nan

        if os.path.isfile(cef):
            # read cef file
            ceflib.verbosity(0)
            ceflib.read(cef)

            time = np.array(ceflib.var(time_tag))

            il_data = np.array(ceflib.var(il_tag))
            fillval = str_to_num(ceflib.vattr(il_tag, "FILLVAL"))
            idx_fill = np.where(il_data == fillval)
            if idx_fill[0].any():
                il_data[idx_fill] = np.nan

            mlt_data = np.array(ceflib.var(mlt_tag))
            fillval = str_to_num(ceflib.vattr(mlt_tag, "FILLVAL"))
            idx_fill = np.where(mlt_data == fillval)
            if idx_fill[0].any():
                mlt_data[idx_fill] = np.nan

            l_data = np.array(ceflib.var(l_tag))
            fillval = str_to_num(ceflib.vattr(l_tag, "FILLVAL"))
            idx_fill = np.where(l_data == fillval)
            if idx_fill[0].any():
                l_data[idx_fill] = np.nan

            # interpolate to match ticks
            itp_il_data = np.around(np.interp(ticks, time, il_data), decimals=1)
            itp_mlt_data = np.around(np.interp(ticks, time, mlt_data), decimals=1)
            itp_l_data = np.around(np.interp(ticks, time, l_data), decimals=1)

            ceflib.close()

        # replace Nan with None for javascript
        if 'il' in list_info:
            itp_il_data = np.array(np.where(np.isnan(itp_il_data), None, itp_il_data))
            sc_info.append({'name': 'IL', 'data': itp_il_data})
        if 'mlt' in list_info:
            itp_mlt_data = np.array(np.where(np.isnan(itp_mlt_data), None, itp_mlt_data))
            sc_info.append({'name': 'MLT', 'data': itp_mlt_data})
        if 'l' in list_info:
            itp_l_data = np.array(np.where(np.isnan(itp_l_data), None, itp_l_data))
            sc_info.append({'name': 'L shell', 'data': itp_l_data})

    if 'sc_max' in list_info or 'sc_min' in list_info:
        # get SC min/max distance info from SP
        sc_min_tag = 'sc_dr_min'
        sc_max_tag = 'sc_dr_max'
        time_tag = 'time_tags'

        # read cef file
        cef = list_cef[1]
        data_max = np.empty(len(ticks))
        data_max[:] = np.nan
        data_min = np.empty(len(ticks))
        data_min[:] = np.nan

        if os.path.isfile(cef):
            # read cef file
            ceflib.verbosity(0)
            ceflib.read(cef)

            time = np.array(ceflib.var(time_tag))

            data_min = np.array(ceflib.var(sc_min_tag))
            fillval = str_to_num(ceflib.vattr(sc_min_tag, "FILLVAL"))
            idx_fill = np.where(data_min == fillval)
            if idx_fill[0].any():
                data_min[idx_fill] = np.nan

            data_max = np.array(ceflib.var(sc_max_tag))
            fillval = str_to_num(ceflib.vattr(sc_max_tag, "FILLVAL"))
            idx_fill = np.where(data_max == fillval)
            if idx_fill[0].any():
                data_max[idx_fill] = np.nan

            # interpolate to match ticks
            data_max = np.around(np.interp(ticks, time, data_max), decimals=1)
            data_min = np.around(np.interp(ticks, time, data_min), decimals=1)

            ceflib.close()

        # replace Nan with None for javascript
        if 'sc_min' in list_info:
            data_min = np.array(np.where(np.isnan(data_min), None, data_min))
            sc_info.append({'name': 'min SC dist', 'data': data_min})
        if 'sc_max' in list_info:
            data_max = np.array(np.where(np.isnan(data_max), None, data_max))
            sc_info.append({'name': 'max SC dist', 'data': data_max})

    with open(json_file_path, 'w') as f:
        json.dump({'sc_info': sc_info}, f, sort_keys=True, indent=4, cls=JsonCustomEncoder)


def main(argv):

    USAGE = """\nUSAGE: \n
           python run_sc_info.py (-m | --mission) mission_id (-s | --spacecraft) spacecraft_id (-i | --info) list_info (-t | --ticks) list_ticks (-b | --begin) start_date (-e | --end) end_date (-o | --orig) orig_dates (-j | --json) json_file \n
           eg: python run_sc_info.py -i 'l,mlt,r,X,Y,Z' -t '10,11,12,13' -m '1' -s '3' -b '2001-03-17T00:00:00Z' -e '2001-03-18T00:00:00Z' -j 'test.json' -o '2001-03-17T00:00:00Z/2001-03-18T00:00:00Z'\n
             mission :     id of the requested mission (1 = cluster, 2 = double star)
             spacecraft:   id of the requested spacecraft (1-4 for cluster, 1-2 for double star)
             list_info :   parameters to retrieve from the spacecraft data
             list_ticks :  time marks in the X axis
             begin/end :   interval of the plot
             orig :        interval of the input cef file to request (the app adds 5 minutes at the beginning/end of the requested interval)
             json_file :   name of the file to write with the data \n  """

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'm:s:i:t:b:e:j:o:h', ['mission=', 'spacecraft=', 'info=', 'ticks=', 'begin=', 'end=', 'orig=', 'json=', 'help'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        print(USAGE)
        sys.exit(2)

    missionID = ""
    sc = ""
    list_info = ""
    list_ticks = ""
    start = ""
    stop = ""
    date_orig = ""
    json_file = ""

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(USAGE)
            sys.exit(2)
        elif opt in ('-m', '--mission'):
            missionID = arg
        elif opt in ('-s', '--spacecraft'):
            sc = arg
        elif opt in ('-i', '--info'):
            list_info = arg
        elif opt in ('-t', '--ticks'):
            list_ticks = arg
        elif opt in ('-b', '--begin'):
            start = arg
        elif opt in ('-e', '--end'):
            stop = arg
        elif opt in ('-o', '--orig'):
            date_orig = arg
        elif opt in ('-j', '--json'):
            json_file = arg
        else:
            print(USAGE)
            sys.exit(2)

    if date_orig == '':
        date_orig = start + '/' + stop

    run_sc_info(list_ticks, list_info, sc, missionID, start, stop, date_orig, json_file)


if __name__ == "__main__":
    main(sys.argv[1:])
