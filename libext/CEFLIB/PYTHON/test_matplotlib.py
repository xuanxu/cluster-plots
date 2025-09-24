from	matplotlib import pyplot as pp
from	matplotlib.dates import *
import	os

import ceflib as cef

cef.verbosity (0)

cm = 1/2.54

def	plot (filename):

	cef.read (filename)

	t = cef.datetime64 ("time_tags")

	v1 = "B_mag"
	v2 = "B_vec_xyz_gse"

	b = cef.var (v1)
	v = cef.var (v2)

	fig, ax = pp.subplots (2,1, figsize = (25*cm, 15*cm), sharex=True, height_ratios=[0.4, 0.6])

	meta = cef.metadata()

	fig.suptitle (meta["DATASET_TITLE"] + "\n" + meta["FILE_TIME_SPAN"])

	ax[0].plot (t, b, linewidth=0.5)
	ax[0].set_ylabel (v1)

	ax[1].plot (t, v, linewidth=0.5)
	ax[1].set_ylabel (v2)

	ax[1].xaxis.set_major_locator (HourLocator([0,4,8,12,16,20,24]))
	ax[1].xaxis.set_major_formatter (DateFormatter ("%H:%M"))
	ax[1].xaxis.set_minor_locator (HourLocator ())

	pp.show()



if __name__ == "__main__":

	filename = "../DATA/C1_CP_WHI_ELECTRON_DENSITY__20020105_000000_20020106_000000_V071001.cef"

	filename = "../DATA/C1_CP_FGM_SPIN__20030303_000000_20030304_000000_V060926.cef.gz"

	plot (filename)
