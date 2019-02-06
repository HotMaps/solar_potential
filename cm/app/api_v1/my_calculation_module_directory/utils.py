#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 11:24:52 2019

@author: pietro
"""
import io
import numpy as np
import pandas as pd


UNIT_CSV = io.StringIO("""text,symbol,power_exp
yotta,Y,24
zetta,Z,21
exa,E,18
peta,P,15
tera,T,12
giga,G,9
mega,M,6
kilo,k,3
#hecto,h,2
#deca,da,1
,,0
#deci,d,-1
#centi,c,-2
milli,m,-3
micro,μ,-6
nano,n,-9
pico,p,-12
femto,f,-15
atto,a,-18
zepto,z,-21
yocto,y,-24
""")
UNIT_PREFIX = pd.read_csv(UNIT_CSV, comment="#").fillna("").set_index("text")


def split_prefix(unit):
    """Return a unit prefix.

    >>> split_prefix("Wh")
    ('', 'Wh')
    >>> split_prefix("kWh")
    ('kilo', 'Wh')
    >>> split_prefix("kiloWh")
    ('kilo', 'Wh')
    >>> split_prefix("kilo Wh")
    ('kilo', 'Wh')
    >>> split_prefix("μWh")
    ('micro', 'Wh')
    """
    for index in UNIT_PREFIX.index:
        if index and unit.startswith(index):
            return index, unit[len(index):].strip()
    for index, prefix in UNIT_PREFIX["symbol"].items():
        if index and unit.startswith(prefix):
            return index, unit[len(prefix):].strip()
    return "", unit


def best_prefix(value, powershift=0):
    """Return the best prefix of a number.

    >>> best_prefix(1)
    ''
    >>> best_prefix(10)
    ''
    >>> best_prefix(100)
    ''
    >>> best_prefix(1000)
    'kilo'
    >>> best_prefix(10000)
    'kilo'
    >>> best_prefix(100000)
    'kilo'
    >>> best_prefix(1000000)
    'mega'
    >>> best_prefix(0.1)
    'milli'
    >>> best_prefix(0.01)
    'milli'
    >>> best_prefix(0.001)
    'milli'
    >>> best_prefix(0.0001)
    'micro'
    >>> best_prefix(1866686.5, powershift=-1)
    'kilo'
    """
    power_exp = int("{:E}".format(value)[-3:]) + powershift
    for index, power in UNIT_PREFIX['power_exp'].items():
        if power_exp >= power:
            return index


def best_unit(array, current_unit, no_data=0, fstat=np.median, powershift=0):
    """Return a tuple with a new array with the transformed value and the unit.

    >>> best_unit(np.array([1, 1000, 1000000]), "Wh", fstat=np.max)
    (array([1.e-06, 1.e-03, 1.e+00]), 'MWh')
    >>> best_unit(np.array([1, 1000, 1000000]), "Wh", fstat=np.median)
    (array([1.e-03, 1.e+00, 1.e+03]), 'kWh')
    >>> best_unit(np.array([1000, 100000, 1000000]), "kWh", fstat=np.min)
    (array([   1.,  100., 1000.]), 'MWh')
    >>> best_unit(np.array([1866686.5, 1905409.8, 1905081.1, 1941486.4]),
    ...           "kWh", fstat=np.min, powershift=-2)
    (array([1866.6865, 1905.4098, 1905.0811, 1941.4864]), 'MWh')
    """
    prefix, unit = split_prefix(current_unit)
    index = ~np.isnan(array) if np.isnan(no_data) else array != no_data
    value = fstat(array[index])
    nfactor = UNIT_PREFIX.at[prefix, 'power_exp']
    nvalue = value * 10**nfactor
    # print("nvalue:", nvalue)
    bprefx = best_prefix(nvalue, powershift=powershift)
    bfactor = UNIT_PREFIX.at[bprefx, 'power_exp']
    bsymb = UNIT_PREFIX.at[bprefx, 'symbol']
    return array * (10**nfactor / 10**bfactor), bsymb+unit


if __name__ == "__main__":
    import doctest
    doctest.testmod()
