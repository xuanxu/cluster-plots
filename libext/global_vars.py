#import matplotlib.pyplot as plt
import threading
ceflib_lock = threading.Lock()

date_start_iso, date_stop_iso = 2 * [None]
date_start_jul, date_stop_jul = 2 * [None]
date_start_milli, date_stop_milli = 2 * [None]

NUM_SEC_DAY = 86400.
NUM_DATA_MINMAX = 1000.
NUM_DATA_AVERAGE = 1200.
NUM_YDATA_SPEC = 200

NUM_DATA_MINMAX = 500.
NUM_DATA_AVERAGE = 1000.
NUM_YDATA_SPEC = 100

#fig = plt.figure(figsize=(800/80, 600/80), dpi=80)


#NUM_DATA_MINMAX = 800.
#NUM_DATA_AVERAGE = 800.
