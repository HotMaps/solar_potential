import tempfile
import unittest
from app import create_app
import os.path
from shutil import copyfile
from .test_client import TestClient
from app.constant import INPUTS_CALCULATION_MODULE

UPLOAD_DIRECTORY = os.path.join(tempfile.gettempdir(),
                                'hotmaps', 'cm_files_uploaded')

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    os.chmod(UPLOAD_DIRECTORY, 0o777)


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
        inputs_raster_selection["solar_optimal_total"]  = save_path
        for inp in INPUTS_CALCULATION_MODULE:
            inputs_parameter_selection[inp['input_parameter_name']]  = inp['input_value']
        # register the calculation module a
        payload = {"inputs_raster_selection": inputs_raster_selection,
                   "inputs_parameter_selection": inputs_parameter_selection}

        rv, json = self.client.post('computation-module/compute/',
                                    data=payload)

        self.assertTrue(rv.status_code == 200)
