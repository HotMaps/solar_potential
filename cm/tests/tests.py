import tempfile
import unittest
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
from app.constant import INPUTS_CALCULATION_MODULE
from pint import UnitRegistry
from osgeo import gdal
import numpy as np

UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(),
                                'hotmaps', 'cm_files_uploaded')

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)

ureg = UnitRegistry()

# function searching values


def search(indicator, name):
    """
    Return a value of a name in the list of indicators

    :param indicator: dictionary with the indicators
    :param name: name to search for

    :returns: the value related to the name or None if missing
    """
    for dic in indicator:
        if dic['name'] == name:
            return float(dic['value']), dic['unit']
    return None


def production_per_plant(json):
    """
    Return the value of the production of a single plant

    :param json: json to parse with results

    :returns: the vale
    """
    value, unit = search(json['result']['indicator'],
                         'Total energy production')
    energy = ureg.Quantity(value, unit)
    n_plants, unit = search(json['result']['indicator'],
                            'Number of installed systems')
    e_plant = energy/n_plants
    e_plant.ito(ureg.kilowatt_hour / ureg.day)
    return e_plant


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app,)

    def tearDown(self):

        self.ctx.pop()

    def test_compute(self):
        # load the raster test file and the default values
        # from app.constant
        raster_file_path = 'tests/data/raster_for_test.tif'
        # simulate copy from HTAPI to CM
        save_path = UPLOAD_DIRECTORY+"/raster_for_test.tif"
        copyfile(raster_file_path, save_path)
        inputs_raster_selection = {}
        inputs_parameter_selection = {}
        inputs_raster_selection["solar_optimal_total"] = save_path
        for inp in INPUTS_CALCULATION_MODULE:
            inputs_parameter_selection[inp['input_parameter_name']]  = inp['input_value']
        # register the calculation module a
        payload = {"inputs_raster_selection": inputs_raster_selection,
                   "inputs_parameter_selection": inputs_parameter_selection}
        rv, json = self.client.post('computation-module/compute/',
                                    data=payload)
        # assert that the production is beetween 5 and 15 kWh/day per plant
        e_plant = production_per_plant(json)
        self.assertGreaterEqual(e_plant.magnitude, 5)
        self.assertLessEqual(e_plant.magnitude, 15)
        # assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = search(json['result']['indicator'],
                            'Levelized Cost of Energy')
        self.assertGreaterEqual(lcoe, 0.02)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)

    def test_raster(self):
        # load the raster test file and the percentage of building 100%
        # from app.constant
        raster_file_path = 'tests/data/raster_for_test.tif'
        # simulate copy from HTAPI to CM
        save_path = UPLOAD_DIRECTORY+"/raster_for_test.tif"
        copyfile(raster_file_path, save_path)
        inputs_raster_selection = {}
        inputs_parameter_selection = {}
        inputs_raster_selection["solar_optimal_total"]  = save_path
        for inp in INPUTS_CALCULATION_MODULE:
            inputs_parameter_selection[inp['input_parameter_name']]  = inp['input_value']
        
        # register the calculation module a
        inputs_parameter_selection['reduction_factor'] = 100
        payload = {"inputs_raster_selection": inputs_raster_selection,
                   "inputs_parameter_selection": inputs_parameter_selection}

        rv, json = self.client.post('computation-module/compute/',
                                    data=payload)
        # path of the output file
        path_output = json['result']['raster_layers'][0]['path']
        ds = gdal.Open(path_output)
        raster_out = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = gdal.Open(save_path)
        raster_in = np.array(ds.GetRasterBand(1).ReadAsArray())
        # count cell of the two rasters
        diff = np.nansum(raster_in) - np.nansum(raster_in[raster_out > 0])
        error = diff/np.nansum(raster_in)
        print(error)
        self.assertLessEqual(error, 0.01)
