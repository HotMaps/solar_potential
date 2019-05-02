#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 08:09:47 2019

@author: ggaregnani
"""

from osgeo import gdal
import numpy as np
from matplotlib import colors

CLRS_SUN = "#F19B03 #F6B13D #F9C774 #FDDBA3 #FFF0CE".split()
CMAP_SUN = colors.LinearSegmentedColormap.from_list('solar', CLRS_SUN)


def colorizeMyOutputRaster(out_ds):
    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0, 0, 0, 255))
    ct.SetColorEntry(1, (110, 220, 110, 255))
    out_ds.SetColorTable(ct)
    return out_ds


def quantile(array, qnumb=6, round_decimals=-2):
    # define the quantile limits
    qvalues, qstep = np.linspace(0, 1., qnumb, retstep=True)

    quantiles = np.quantile(array, qvalues)
    # round the number
    while True:
        q0 = np.round(quantiles, round_decimals)
        if len(set(q0)) != len(quantiles):
            print("Increase decimals")
            round_decimals += 1
        else:
            break

    return qvalues, q0


def quantile_colors(array, output_suitable, proj, transform,
                    qnumb=6,
                    no_data_value=0,
                    no_data_color=(0, 0, 0, 255),
                    gtype=gdal.GDT_Byte,
                    options='compress=DEFLATE TILED=YES TFW=YES'
                            ' ZLEVEL=9 PREDICTOR=1',
                    round_decimals=-2,
                    unit="kWh/year"):
    """Generate a GTiff categorical raster map based on quantiles
    values.

    "symbology": [
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"50","label":"50MWh"},
        {"red":100,"green":150,"blue":10,"opacity":0.5,"value":"150MWh","label":"150MWh"},
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"200MWh","label":"200MWh"},
        {"red":50,"green":50,"blue":50,"opacity":0.5,"value":"250MWh","label":"250MWh"}
    ]
    """
    valid = array != no_data_value
    qvalues, quantiles = quantile(array[valid], qnumb=qnumb,
                                  round_decimals=round_decimals)

    symbology = [
            {"red": no_data_color[0],
             "green": no_data_color[1],
             "blue": no_data_color[2],
             "opacity": no_data_color[3],
             "value": no_data_value,
             "label": "no data"},
            ]

    # create a categorical derived map
    array_cats = np.zeros_like(array, dtype=np.uint8)
    qv0 = quantiles[0] - 1.
    array_cats[~valid] = 0
    for i, (qk, qv) in enumerate(zip(qvalues[1:], quantiles[1:])):
        label = ("{qv0} {unit} < Solar potential <= {qv1} {unit}"
                 "").format(qv0=qv0, qv1=qv, unit=unit)
        print(label)
        qindex = (qv0 < array) & (array <= qv)
        array_cats[qindex] = i + 1
        qv0 = qv
        symbology.append(dict(value=int(i + 1), label=label))

    # create a color table
    ct = gdal.ColorTable()
    ct.SetColorEntry(no_data_value, no_data_color)
    for i, (clr, symb) in enumerate(zip(CMAP_SUN(qvalues), symbology[1:])):
        r, g, b, a = (np.array(clr) * 255).astype(np.uint8)
        ct.SetColorEntry(i+1, (r, g, b, a))
        symb.update(dict(red=int(r), green=int(g), blue=int(b),
                         opacity=int(a)))

    # create a new raster map
    gtiff_driver = gdal.GetDriverByName('GTiff')
    ysize, xsize = array_cats.shape

    out_ds = gtiff_driver.Create(output_suitable,
                                 xsize, ysize,
                                 1, gtype,
                                 options.split())
    out_ds.SetProjection(proj)
    out_ds.SetGeoTransform(transform)

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(no_data_value)
    out_ds_band.SetColorTable(ct)
    out_ds_band.WriteArray(array_cats)
    out_ds.FlushCache()
    return out_ds, symbology

# TODO: fix color map according to raster visualization


def line(x, y_labels, y_values, unit, xLabel="Percentage of buildings",
         yLabel='Energy production [{}]'):
    """
    Define the dictionary for defining a multiline plot
    :param x: list of x data
    :param y_labels: list of strings with y labels of dataset
    :param y_values: lists of dataset with their values
    :returns: the dictionary for the app
    """
    dic = []
    palette = ['#0483a3', '#72898b', '#a38b6f', '#ca8b50', '#ec8729']
    for i, lab in enumerate(y_labels):
        dic.append({
                    "label": lab,
                    "backgroundColor": palette[i],
                    "data": ['{:4.0f}'.format(y) for y in y_values[i]]})

    graph = {"xLabel": xLabel,
             "yLabel": yLabel.format(unit),
             "type": "line",
             "data": {"labels": [str(xx) for xx in x],
                      "datasets": dic}
             }
    return graph


def reducelabels(x, steps=10):
    """
    Insert an empty string in order to better visualize x labels
    :param x: list of x data
    :param steps: integer with the number of x values to visualize

    >>> x = [str(i) for i in range(0,10)]
    >>> reducelabels(x, steps=3)
    ['0', '', '', '3', '', '', '6', '', '', '9']
    """
    x_rep = ["" for i in range(0, len(x))]
    for i in range(0, len(x), round(len(x)/steps)):
        x_rep[i] = x[i]
    return x_rep

if __name__ == "__main__":
    import doctest
    doctest.testmod()
