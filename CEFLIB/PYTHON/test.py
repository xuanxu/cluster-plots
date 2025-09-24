"""Test celib installation

Display record varying variables size and type
"""
from	__future__ import print_function

import	ceflib as cef
import	os
import	glob

test_dir = "../DATA"

cef.verbosity(0)

os.putenv ("CEFPATH", "/net/rosina1/MSA2060a.CAA2/CAA/INCLUDES")

filenames = glob.glob ("%s/*.cef.gz" % test_dir)

for filename in filenames:

	print ("Reading", os.path.basename(filename))

	cef.read (filename)

	for var in cef.varnames():

		va = cef.vattrs (var)

		if va.get("DEPEND_0") is not None or var.startswith ("time"):
			print (">> ", var, ":", va.get("SIZES", "1"), "x", va["VALUE_TYPE"], ":", va["CATDESC"])
	print()
	
