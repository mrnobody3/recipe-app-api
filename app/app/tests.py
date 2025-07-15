"""
Sample tests
"""
from django.test import SimpleTestCase
from app import calc


class CalcTests(SimpleTestCase):
    '''Test the calc module'''

    def test_add_number(self):
        res = calc.add(5, 6)
        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        res = calc.subtract(15, 9)
        self.assertEqual(res, 6)
