import tempfile
import unittest
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
from app.constant import INPUTS_CALCULATION_MODULE
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import json as js
import resutils.output as ro
import resutils.raster as rr
from pint import UnitRegistry


ureg = UnitRegistry()
UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(), "hotmaps", "cm_files_uploaded")

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)


def load_input():
    """
    Load the input values in the file constant.py

    :return a dictionary with the imput values
    """
    inputs_parameter = {}
    for inp in INPUTS_CALCULATION_MODULE:
        inputs_parameter[inp["input_parameter_name"]] = inp["input_value"]
    return inputs_parameter


def load_raster(suitable_area, solar):
    """
    Load the raster file for testing

    :return a dictionary with the raster file paths
    """
    raster_file_path = os.path.join("tests/data", solar)
    # simulate copy from HTAPI to CM
    save_path_solar = os.path.join(UPLOAD_DIRECTORY, solar)
    copyfile(raster_file_path, save_path_solar)

    raster_file_path = os.path.join("tests/data", suitable_area)
    # simulate copy from HTAPI to CM
    save_path_area = os.path.join(UPLOAD_DIRECTORY, suitable_area)
    copyfile(raster_file_path, save_path_area)

    inputs_raster_selection = {}
    inputs_raster_selection["climate_solar_radiation"] = save_path_solar
    inputs_raster_selection["gross_floor_area"] = save_path_area
    return inputs_raster_selection


def modify_input(inputs_parameter, **kwargs):
    """
    Modify the dictionary of input parameter

    :return a dictionary with input file modified
    """
    for key, value in kwargs.items():
        inputs_parameter[key] = value
    return inputs_parameter


def test_graph(graph):
    """
    Print a graph with matplot lib by reading the dictionary with graph info
    """
    for n, g in enumerate(graph):
        graph_file_path = os.path.join("tests/data", "plot{}.png".format(n))
        # simulate copy from HTAPI to CM
        x = [i for i in range(0, len(g["data"]["labels"]))]
        # TODO loop in datasets to plot more lines
        y = [float(i) for i in g["data"]["datasets"][0]["data"]]
        plt.plot(x, y, label=g["data"]["datasets"][0]["label"])
        plt.xlabel(g["xLabel"])
        plt.ylabel(g["yLabel"])
        plt.xticks(rotation=90)
        ax = plt.gca()
        axes = plt.axes()
        axes.set_xticks(x)
        ax.set_xticklabels(g["data"]["labels"])
        #        locs, labels = plt.xticks()
        #        plt.xticks(locs, g['data']['labels'])
        plt.savefig(graph_file_path)
        plt.clf()


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(os.environ.get("FLASK_CONFIG", "development"))
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app)

    def tearDown(self):
        self.ctx.pop()

    def test_compute(self):
        """
        Test of the default values from app.constat by
        1) asserting the production per platn between 5 and 15 kWh/day
        2) asserting the value of lcoe between 0.02 and 0.2 euro/kWh
        """
        print("\n" "------------------------------------------------------")
        inputs_raster_selection = load_raster("area_for_test.tif", "solar_for_test.tif")
        inputs_parameter_selection = load_input()
        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_parameter_selection": inputs_parameter_selection,
        }
        rv, json = self.client.post("computation-module/compute/", data=payload)

        # 0) print graphs
        test_graph(json["result"]["graphics"])
        # 1) assert that the production is beetween 5 and 15 kWh/day per plant
        e_plant = ro.production_per_plant(json)
        e_plant.ito(ureg.kilowatt_hour / ureg.day)
        self.assertGreaterEqual(e_plant.magnitude, 5)
        self.assertLessEqual(e_plant.magnitude, 15)
        # 2) assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = ro.search(
            json["result"]["indicator"], "Levelized Cost of PV Energy"
        )
        self.assertGreaterEqual(lcoe, 0.02)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)
        # 3) assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = ro.search(
            json["result"]["indicator"], "Levelized Cost of ST Energy"
        )
        self.assertGreaterEqual(lcoe, 0.01)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)
        # 4) assert that the production is beetween 5 and 20 kWh/day per plant
        e_plant = ro.production_per_plant(json)
        e_plant.ito(ureg.kilowatt_hour / ureg.day)
        self.assertGreaterEqual(e_plant.magnitude, 5)
        self.assertLessEqual(e_plant.magnitude, 20)

    def test_raster(self):
        """
        Test the output raster
        1) the consistent between input file and output file in the case
        of using the total surface of the buildings
        """
        print("\n" "------------------------------------------------------")
        inputs_raster_selection = load_raster("area_for_test.tif", "solar_for_test.tif")
        inputs_parameter_selection = load_input()
        inputs_parameter_selection = modify_input(
            inputs_parameter_selection, reduction_factor=100
        )
        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_parameter_selection": inputs_parameter_selection,
        }

        rv, json = self.client.post("computation-module/compute/", data=payload)

        # 1) the consistent between input file and output file in the case
        # of using the total surface of the buildings
        path_output = json["result"]["raster_layers"][0]["path"]
        ds = gdal.Open(path_output)
        raster_out = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = gdal.Open(inputs_raster_selection["climate_solar_radiation"])
        irradiation = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = gdal.Open(inputs_raster_selection["gross_floor_area"])
        area = np.array(ds.GetRasterBand(1).ReadAsArray())
        error = rr.diff_raster(irradiation[area > 0], irradiation[raster_out > 0])
        with open("data.json", "w") as outfile:
            js.dump(json["result"], outfile)
        self.assertLessEqual(error, 0.01)

    def test_noresults(self):
        """
        Test the message when no output file are produced
        """
        print("\n" "------------------------------------------------------")
        inputs_raster_selection = load_raster("area_for_test.tif", "solar_for_test.tif")
        inputs_parameter_selection = load_input()
        inputs_parameter_selection = modify_input(
            inputs_parameter_selection, roof_use_factor=0.1
        )
        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_parameter_selection": inputs_parameter_selection,
        }

        rv, json = self.client.post("computation-module/compute/", data=payload)
        self.assertTrue(rv.status_code == 200)

    def test_sumPVST(self):
        print("\n" "------------------------------------------------------")
        """
        Test of the default values from app.constat by changing PV and
        ST share greater than one
        1) asserting the production per plant between 5 and 15 kWh/day
        2) asserting the value of LCOE between 0.02 and 0.2 euro/kWh
        """
        inputs_raster_selection = load_raster("area_for_test.tif", "solar_for_test.tif")
        inputs_parameter_selection = load_input()
        #        inputs_parameter_selection = modify_input(inputs_parameter_selection,
        #                                                  roof_use_factor_pv=0.6,
        #                                                  roof_use_factor_st=0.6)
        # register the calculation module a
        payload = {
            "inputs_raster_selection": inputs_raster_selection,
            "inputs_parameter_selection": inputs_parameter_selection,
        }
        from pprint import pprint

        pprint(payload)
        rv, json = self.client.post("computation-module/compute/", data=payload)

        # 1) assert that the production is beetween 5 and 15 kWh/day per plant
        e_plant = ro.production_per_plant(json, kind="PV")
        e_plant.ito(ureg.kilowatt_hour / ureg.day)
        self.assertGreaterEqual(e_plant.magnitude, 5)
        self.assertLessEqual(e_plant.magnitude, 15)

        # 2) assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = ro.search(
            json["result"]["indicator"], "Levelized Cost of PV Energy"
        )
        self.assertGreaterEqual(lcoe, 0.02)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)

        # 3) assert that the value of lcoe is between 0.02 and 0.2 euro/kWh
        lcoe, unit = ro.search(
            json["result"]["indicator"], "Levelized Cost of ST Energy"
        )
        self.assertGreaterEqual(lcoe, 0.01)
        self.assertLessEqual(lcoe, 0.2)
        self.assertTrue(rv.status_code == 200)

        # 4) assert that the production is beetween 5 and 20 kWh/day per plant
        e_plant = ro.production_per_plant(json, kind="ST")
        e_plant.ito(ureg.kilowatt_hour / ureg.day)
        self.assertGreaterEqual(e_plant.magnitude, 5)
        self.assertLessEqual(e_plant.magnitude, 20)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
