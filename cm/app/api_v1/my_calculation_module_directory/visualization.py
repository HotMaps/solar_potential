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


def quantile_colors(array, output_suitable, proj, transform,
                    qnumb=6,
                    no_data_value=0,
                    no_data_color=(0, 0, 0, 255),
                    gtype=gdal.GDT_Byte,
                    options='compress=DEFLATE TILED=YES TFW=YES'
                            ' ZLEVEL=9 PREDICTOR=1'):
    """Generate a GTiff categorical raster map based on quantiles
    values.
    """
    # define the quantile limits
    qvalues, qstep = np.linspace(0, 1., qnumb, retstep=True)
    valid = array != no_data_value
    quantiles = np.quantile(array[valid], qvalues)

    # create a categorical derived map
    array_cats = np.zeros_like(array, dtype=np.uint8)
    qv0 = quantiles[0] - 1.
    array_cats[~valid] = 0
    for i, (qk, qv) in enumerate(zip(qvalues[1:], quantiles[1:])):
        print("{}: {} < valid <= {}".format(i+1, qv0, qv))
        qindex = (qv0 < array) & (array <= qv)
        array_cats[qindex] = i + 1
        qv0 = qv

    # create a color table
    ct = gdal.ColorTable()
    ct.SetColorEntry(no_data_value, no_data_color)
    for i, clr in enumerate(CMAP_SUN(qvalues)):
        r, g, b, a = (np.array(clr) * 255).astype(np.uint8)
        ct.SetColorEntry(i+1, (r, g, b, a))

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
    return out_ds

# TODO: fix color map according to raster visualization


def line(x, y_labels, y_values):
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
                    "data": [str(y) for y in y_values[i]]})

    graph = {"xLabel": "Investment costs (10^6 €)",
             "ylabel": "Energy production (GWh)",
             "type": "line",
             "data": {"labels": [str(xx) for xx in x],
                      "datasets": dic}
             }
    return graph
