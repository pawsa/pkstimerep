#! /usr/bin/env python

"""memorymodel unit tests"""

import unittest

import memorymodel


class TestTimeToMin(unittest.TestCase):

    def test_time(self):
        self.assertEqual(memorymodel.timeToMin('16:25'), 16*60+25)
        self.assertEqual(memorymodel.timeToMin('23:5'), 23*60+5)

if __name__ == '__main__':
    unittest.main()
