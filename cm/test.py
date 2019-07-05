#!/usr/bin/env python
import unittest
import sys
import coverage

from tests import suite

COV = coverage.coverage(branch=True, include='cm/app/*')
COV.start()

return_code = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

COV.stop()
COV.report()

sys.exit(return_code)