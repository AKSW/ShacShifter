from context import ShacShifter
import unittest
import os
from os import path
from ShacShifter.ShapeParser import ShapeParser
from ShacShifter.RDFormsSerializer import RDFormsSerializer, RDFormsTemplateBundle


class RDFormsSerializerTests(unittest.TestCase):

    def setUp(self):
        self.dir = 'tests/_files'

    def tearDown(self):
        self.dir = None

    def testSerializationOfAllFiles(self):
        """Test if all valid Shape files are serialized without throwing an error."""
        exceptions = ['maxLowerMin.ttl', 'minGreaterMax.ttl', 'multipleMaxCounts.ttl', 'multipleMinCounts.ttl']

        for f in os.listdir(self.dir):
                if not os.path.isfile(f) or file in exceptions:
                    continue
                print(f)
                shapes = ShapeParser().parseShape(path.join(self.dir, f))
                serializer = RDFormsSerializer(shapes)
                bundles = serializer.templateBundles
                for bundle in bundles:
                    self.assertTrue(isinstance(bundle, RDFormsTemplateBundle))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
