#!/usr/bin/env python
import unittest

import coverage

from tests import suite

COV = coverage.coverage(branch=True, include='cm/app/*')
COV.start()

unittest.TextTestRunner(verbosity=2).run(suite)

COV.stop()
COV.report()
