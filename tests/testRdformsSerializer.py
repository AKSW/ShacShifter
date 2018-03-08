import unittest
import rdflib
from os import path
from context import ShacShifter
from ShacShifter.ShapeParser import ShapeParser


class RDFormsSerializerTests(unittest.TestCase):

    def setUp(self):
        self.parser = ShapeParser()
        self.dir = path.abspath('tests/_files')

    def tearDown(self):
        self.parser = None
        self.dir = None


def main():
    unittest.main()


if __name__ == '__main__':
    main()
