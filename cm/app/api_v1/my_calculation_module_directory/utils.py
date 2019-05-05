#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 11:24:52 2019

@author: pietro, ggaregnani
"""
import io
import numpy as np
import pandas as pd
from osgeo import osr
from pint import UnitRegistry

ureg = UnitRegistry()

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
    (array([1.e-06, 1.e-03, 1.e+00]), 'MWh', 1e-06)
    >>> best_unit(np.array([1, 1000, 1000000]), "Wh", fstat=np.median)
    (array([1.e-03, 1.e+00, 1.e+03]), 'kWh', 0.001)
    >>> best_unit(np.array([1000, 100000, 1000000]), "kWh", fstat=np.min)
    (array([   1.,  100., 1000.]), 'MWh', 0.001)
    >>> best_unit(np.array([1866686.5, 1905409.8, 1905081.1, 1941486.4]),
    ...           "kWh", fstat=np.min, powershift=-2)
    (array([1866.6865, 1905.4098, 1905.0811, 1941.4864]), 'MWh', 0.001)
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
    factor = (10**nfactor / 10**bfactor)
    return array * factor, bsymb+unit, factor


def xy2latlong(x, y, ds):
    """Return lat long coordinate by x, y

    >>> import gdal
    >>> path = "../../../tests/data/raster_for_test.tif"
    >>> ds = gdal.Open(path)
    >>> xy2latlong(3715171, 2909857, ds)
    (1.7036231518576481, 48.994284431891565)
    """
    old_cs = osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())
    # create the new coordinate system
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    new_cs = osr.SpatialReference()
    new_cs .ImportFromWkt(wgs84_wkt)
    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(old_cs, new_cs)
    # get the coordinates in lat long
    latlong = transform.TransformPoint(x, y)
    return latlong[0], latlong[1]


def search(indicator_list, name):
    """
    Return a value of a name in the list of indicators

    :param indicator_list: list with the dictionaries with the indicators
    :param name: name to search for

    :returns: the value related to the name or None if missing
    >>> ind = [{'unit': 'MWh/year', 'name': 'Total energy production',
    ...         'value': '2887254.54'},
    ...        {'unit': 'Million of currency', 'name': 'Total setup costs',
    ...         'value': '6137'},
    ...        {'unit': '-', 'name': 'Number of installed systems',
    ...         'value': '1022847'},
    ...        {'unit': 'currency/kWh', 'name': 'Levelized Cost of Energy',
    ...         'value': '0.17'}]
    >>> search(ind, 'Total energy production')
    (2887254.54, 'MWh/year')
    """
    for dic in indicator_list:
        if dic['name'] == name:
            return float(dic['value']), dic['unit']
    return None


def production_per_plant(json, kind='PV'):
    """
    Return the value of the production of a single plant

    :param json: json to parse with results

    :returns: the vale
    """
    value, unit = search(json['result']['indicator'],
                         '{} total energy production'.format(kind))
    energy = ureg.Quantity(value, unit)
    n_plants, unit = search(json['result']['indicator'],
                            'Number of installed {} Systems'.format(kind))
    e_plant = energy/n_plants
    e_plant.ito(ureg.kilowatt_hour / ureg.day)
    return e_plant


def diff_raster(raster_in, raster_out):
    """
    Verify the position of the pixel and the consistent with the input file

    :param raster_in: array with the input values
    :param raster_out: array with the putput values

    :returns: the relative error of missing pixels
    >>> raster_in = np.array([[1, 2], [3, 4]])
    >>> raster_out = np.array([[1, 2], [3, 0]])
    >>> diff_raster(raster_in, raster_out)
    0.4
    """
    # count cell of the two rasters
    diff = np.nansum(raster_in) - np.nansum(raster_in[raster_out > 0])
    error = diff/np.nansum(raster_in)
    return error


if __name__ == "__main__":
    import doctest
    doctest.testmod()
