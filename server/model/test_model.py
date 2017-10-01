#! /usr/bin/env python

"""general model unit tests"""

import unittest

from . import timeToMin


class TestTimeToMin(unittest.TestCase):

    def test_time(self):
        self.assertEqual(timeToMin('16:25'), 16*60+25)
        self.assertEqual(timeToMin('23:5'), 23*60+5)

if __name__ == '__main__':
    unittest.main()
