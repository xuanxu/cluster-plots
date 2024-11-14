import numpy as np

def make_sParameter():
    """ initialise the sParameter structure """
    sParameter = {'paramid': '',
        'fillval': '',
        'type': '',
        'support': 0,
        'num_depend': 0,
        'arrDepend': [],
        'arrQuality': np.empty(1),
        'arrDeltaP': np.zeros(1),
        'arrDeltaM': np.zeros(1),
        'arrData': np.empty(1)
		}
    (sParameter['arrData'])[0] = np.nan
    return sParameter
