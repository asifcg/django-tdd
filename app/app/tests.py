"""
Test Sample
"""

from django.test import SimpleTestCase

from app.helpers.utils import *

class UtilTests(SimpleTestCase):
    """ Test All utils """
    
    def test_reverse_string(self):
        """Test return correct string"""
        res = reverse_string("Hello")

        self.assertEqual("olleH",res)