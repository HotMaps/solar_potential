#!/usr/bin/env python
import os
import unittest
import sys
import coverage

from tests import suite


COV = coverage.coverage(
    data_file=os.path.join(os.path.dirname(__file__), ".coverage"),
    branch=True,
    include="cm/*",
)
COV.start()

return_code = not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

COV.stop()
# COV.report()

sys.exit(return_code)
