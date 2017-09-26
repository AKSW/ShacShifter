import unittest
import rdflib
from .ShacShifter import ShacShifter
from .modules.ShapeParser import ShapeParser
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


class ShapeParserTests(unittest.TestCase):


    def setUp(self):
        self.parser = ShapeParser()
        self.dir = path.abspath('../_files')

    def tearDown(self):
        self.parser = None
        self.dir = None

    def testPositiveNodeShapeParse(self):
        shapes = self.parser.parseShape(self.dir + '/positiveShapeParserExample1.ttl')[0]
        shape = shapes[0]
        self.assertEqual(str(shape.targetClass[0]), 'http://www.example.org/example/Person')

def main():
    unittest.main()

if __name__ == '__main__':
    main()
