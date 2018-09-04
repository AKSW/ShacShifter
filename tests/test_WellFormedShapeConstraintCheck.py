import unittest
import rdflib
import os
from os import path
from context import ShacShifter
from rdflib.namespace import XSD
from ShacShifter.modules.WellFormedShapeConstraintCheck import WellFormedShapeConstraintCheck
from ShacShifter.modules.NodeShape import NodeShape
from ShacShifter.modules.PropertyShape import PropertyShape



class WellFormedShapeConstraintCheckTests(unittest.TestCase):

    w3c_test_files = 'tests/_files/w3c'
    ex = rdflib.Namespace('http://www.example.org/')

    def setUp(self):
        self.g = rdflib.Graph()
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.dir = path.abspath('tests/_files')

    def tearDown(self):
        self.parser = None
        self.dir = None

    def testNegativeFullConstraintCheck(self):
        """Test if the WellFormedShapeConstraintCheck correctly applies negative Results"""
        # should this be tested in testWellFormedShapeConstraintCheck.py instead?
        self.g.parse(path.join(self.dir, 'negativeFullFailureCount.ttl'), format='turtle')
        wfscc = WellFormedShapeConstraintCheck(self.g, self.ex.FullNegativeExampleShape)
        self.assertEqual(len(wfscc.errors), 10)
        for stmt in self.g.objects(self.ex.FullNegativeExampleShape, self.sh.property):
            wfscc = WellFormedShapeConstraintCheck(self.g, stmt)
            self.assertEqual(len(wfscc.errors), 44)



def main():
    unittest.main()


if __name__ == '__main__':
    main()