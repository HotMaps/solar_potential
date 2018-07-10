import unittest
from werkzeug.exceptions import NotFound
from app import create_app

from .test_client import TestClient


class TestAPI(unittest.TestCase):


    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()

        self.client = TestClient(self.app,)

    def tearDown(self):

        self.ctx.pop()




    def test_register(self):
        # register the calculation module a
        rv, json = self.client.post('computation-module/register/', data={'name': 'prod1'})

        self.assertTrue(rv.status_code == 200)

        # get list of products


    def test_compute(self):
        # register the calculation module a
        payload = {"filename": "6d998d5c-5139-4f77-b0b3-8ee078e4527c.tif",
                   "url_file": "http://127.0.0.1:5000/api/cm/files/6d998d5c-5139-4f77-b0b3-8ee078e4527c.tif",
                   "reduction_factor": 1}


        rv, json = self.client.post('computation-module/compute/', data=payload)

        self.assertTrue(rv.status_code == 200)



