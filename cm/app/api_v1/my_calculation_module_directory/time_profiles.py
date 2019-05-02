#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:51:48 2019

@author: ggaregnani
"""

import requests
import pandas as pd


def pv_profile(lat, lon, capacity, system_loss):
    """
    Return the dataframe with Pv profile
    >>> df = pv_profile(lat=34.125, lon=39.814, capacity=1.0, system_loss=10)
    >>> min(df['output'])
    0.0
    """
    # TODO: this is my personal token, how to manage it
    # TODO: choose the reference year?
    token = 'c5d1b5720336748d23f137ed7f8c9a008057f0c7'
    api_base = 'https://www.renewables.ninja/api/'
    s = requests.session()
    # Send token header with each request
    s.headers = {'Authorization': 'Token ' + token}
    url = api_base + 'data/pv'
    args = {
        'lat': lat,
        'lon': lon,
        'date_from': '2014-01-01',
        'date_to': '2014-12-31',
        'dataset': 'merra2',
        'capacity': capacity,
        'system_loss': system_loss,
        'tracking': 0,
        'tilt': 30,
        'azim': 180,
        'format': 'json',
        'metadata': False,
        'raw': False
    }
    r = s.get(url, params=args)
    # Parse JSON to get a pandas.DataFrame
    df = pd.read_json(r.text, orient='index')

    # modify the labels by deleting the year
    return df


if __name__ == "__main__":
    import doctest
    doctest.testmod()
