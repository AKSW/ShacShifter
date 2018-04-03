import unittest
import rdflib
import os
from os import path
from context import ShacShifter
from rdflib.namespace import XSD
from ShacShifter.ShapeParser import ShapeParser
from ShacShifter.modules.NodeShape import NodeShape
from ShacShifter.modules.PropertyShape import PropertyShape


class ShapeParserTests(unittest.TestCase):

    w3c_test_files = 'tests/_files/w3c'
    ex = rdflib.Namespace('http://www.example.org/')

    def setUp(self):
        self.parser = ShapeParser()
        self.dir = path.abspath('tests/_files')

    def tearDown(self):
        self.parser = None
        self.dir = None

    def testParsingW3CFiles(self):
        """Test if all W3C samples are parsed without throwing an error."""
        for root, dirs, files in os.walk(self.w3c_test_files):
            for f in files:
                shapes = ShapeParser().parseShape(path.join(self.w3c_test_files, f))
                self.assertTrue(isinstance(shapes[0], dict))
                self.assertTrue(isinstance(shapes[1], dict))

    def testAddressShape(self):
        """Test Adress Shape example."""
        shapes = ShapeParser().parseShape(path.join(self.w3c_test_files, 'AddressShape.ttl'))
        nodeShapesDict = shapes[0]
        propertyShapesDict = shapes[1]
        addressShape = nodeShapesDict[str(self.ex.AddressShape)]
        personShape = nodeShapesDict[str(self.ex.PersonShape)]
        postalCodeShape = addressShape.properties[0]
        addressPropertyShape = personShape.properties[0]

        self.assertEqual(len(nodeShapesDict), 2)
        self.assertEqual(len(propertyShapesDict), 2)

        self.assertEqual(addressShape.uri, str(self.ex.AddressShape))

        self.assertEqual(personShape.uri, str(self.ex.PersonShape))

        self.assertEqual(postalCodeShape.path, str(self.ex.postalCode))
        self.assertEqual(postalCodeShape.dataType, str(XSD.string))
        self.assertEqual(postalCodeShape.maxCount, 1)

        self.assertEqual(addressPropertyShape.path, str(self.ex.address))
        self.assertEqual(addressPropertyShape.minCount, 1)
        self.assertEqual(addressPropertyShape.nodes[0], str(self.ex.AddressShape))

    def testClassExampleShape(self):
        """Test Class example."""
        shapes = ShapeParser().parseShape(path.join(self.w3c_test_files, 'ClassExampleShape.ttl'))
        nodeShape = shapes[0][str(self.ex.ClassExampleShape)]
        propertyShape = nodeShape.properties[0]

        self.assertEqual(nodeShape.uri, str(self.ex.ClassExampleShape))
        self.assertTrue(str(self.ex.Alice) in nodeShape.targetNode)
        self.assertTrue(str(self.ex.Bob) in nodeShape.targetNode)
        self.assertTrue(str(self.ex.Carol) in nodeShape.targetNode)
        self.assertTrue(len(nodeShape.targetNode), 3)
        self.assertTrue(len(shapes[0]), 1)

        self.assertEqual(propertyShape.path, str(self.ex.address))
        self.assertEqual(propertyShape.classes[0], str(self.ex.PostalAddress))
        self.assertTrue(len(propertyShape.classes), 1)
        self.assertTrue(propertyShape in shapes[1].values())
        self.assertTrue(len(shapes[1]), 1)

    def testHand(self):
        """Test qualifiedValueShapes of Hand example."""
        shapes = ShapeParser().parseShape(path.join(self.w3c_test_files, 'HandShape.ttl'))
        nodeShapesDict = shapes[0]
        propertyShapesDict = shapes[1]
        self.assertEqual(len(nodeShapesDict), 1)
        self.assertEqual(len(propertyShapesDict), 3)
        for id, nodeShape in nodeShapesDict.items():
            values = {'http://www.example.org/Finger': 4, 'http://www.example.org/Thumb': 1}

            for propertyShape in nodeShape.properties:
                if propertyShape.isSet['qualifiedValueShape']:
                    # One thumb and four fingers
                    self.assertTrue(propertyShape.isSet['qualifiedValueShapesDisjoint'])
                    self.assertEqual(propertyShape.path, str(self.ex.digit))
                    self.assertEqual(
                        values[propertyShape.qualifiedValueShape.classes[0]],
                        propertyShape.qualifiedMinCount)
                    self.assertEqual(
                        values[propertyShape.qualifiedValueShape.classes[0]],
                        propertyShape.qualifiedMaxCount)
                else:
                    # Hand
                    self.assertEqual(propertyShape.path, str(self.ex.digit))
                    self.assertFalse(propertyShape.isSet['qualifiedValueShapesDisjoint'])
                    self.assertEqual(propertyShape.maxCount, 5)

    def testMinMaxLogic(self):
        with self.assertRaises(Exception):
            ShapeParser().parseShape(path.join(self.dir, 'minGreaterMax.ttl'))

        with self.assertRaises(Exception):
            ShapeParser().parseShape(path.join(self.dir, 'maxLowerMin.ttl'))

        with self.assertRaises(Exception):
            ShapeParser().parseShape(path.join(self.dir, 'multipleMinCounts.ttl'))

        with self.assertRaises(Exception):
            ShapeParser().parseShape(path.join(self.dir, 'multipleMaxCounts.ttl'))

        shapes = ShapeParser().parseShape(path.join(self.dir, 'minLowerMax.ttl'))
        self.assertEqual(shapes[0]['http://www.example.org/ExampleShape'].properties[0].minCount, 1)
        self.assertEqual(shapes[0]['http://www.example.org/ExampleShape'].properties[0].maxCount, 2)

    def testPositiveNodeShapeParse(self):
        shapes = self.parser.parseShape(self.dir + '/positiveNodeShapeParserExample1.ttl')
        nodeShapes = shapes[0]
        nodeShape = nodeShapes[('http://www.example.org/exampleShape')]
        self.assertEqual(str(nodeShape.uri), 'http://www.example.org/exampleShape')

        targetClasses = [
            'http://www.example.org/Animal',
            'http://www.example.org/Person'
        ]
        self.assertEqual(sorted(nodeShape.targetClass), targetClasses)

        targetNodes = [
            'http://www.example.org/Alice',
            'http://www.example.org/Bob'
        ]
        self.assertEqual(sorted(nodeShape.targetNode), targetNodes)

        relationships = [
            'http://www.example.org/friendship',
            'http://www.example.org/relationship'
        ]
        self.assertEqual(sorted(nodeShape.targetObjectsOf), relationships)
        self.assertEqual(sorted(nodeShape.targetSubjectsOf), relationships)
        self.assertEqual(str(nodeShape.nodeKind), 'http://www.w3.org/ns/shacl#IRI')
        self.assertEqual(nodeShape.closed, True)

        ignoredProperties = [
            'http://www.example.org/A',
            'http://www.example.org/B',
            'http://www.example.org/C'
        ]
        self.assertEqual(sorted(nodeShape.ignoredProperties), ignoredProperties)
        self.assertEqual(str(nodeShape.message['default']), "C")
        self.assertEqual(str(nodeShape.message['en']), "A")
        self.assertEqual(str(nodeShape.message['de']), "B")
        self.assertEqual(len(nodeShape.properties), 2)

    def testPositivePropertyShapeParse(self):
        shapes = self.parser.parseShape(self.dir + '/positivePropertyShapeParserExample1.ttl')
        propertyShapes = shapes[1]
        propertyShape = propertyShapes[
            'http://www.example.org/exampleShapeA'
        ]

        self.assertEqual(str(propertyShape.uri), 'http://www.example.org/exampleShapeA')
        self.assertEqual(str(propertyShape.path), 'http://www.example.org/PathA')

        classes = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShape.classes), classes)
        self.assertEqual(
            propertyShape.dataType,
            'http://www.w3.org/2001/XMLSchema#integer'
        )
        self.assertEqual(int(propertyShape.minCount), 1)
        self.assertEqual(int(propertyShape.maxCount), 2)
        self.assertEqual(int(propertyShape.minExclusive), 1)
        self.assertEqual(int(propertyShape.maxExclusive), 1)
        self.assertEqual(int(propertyShape.minInclusive), 1)
        self.assertEqual(int(propertyShape.maxInclusive), 1)
        self.assertEqual(int(propertyShape.minLength), 1)
        self.assertEqual(int(propertyShape.maxLength), 2)
        self.assertEqual(str(propertyShape.pattern), '[abc]')
        self.assertEqual(str(propertyShape.flags), 'i')

        languageIn = [
            'de',
            'en'
        ]
        self.assertEqual(sorted(propertyShape.languageIn), languageIn)
        self.assertEqual(propertyShape.uniqueLang, True)

        equals = [
            'http://www.example.org/PathB',
            'http://www.example.org/PathC'
        ]
        self.assertEqual(sorted(propertyShape.equals), equals)

        disjoint = [
            'http://www.example.org/PathB',
            'http://www.example.org/PathC'
        ]
        self.assertEqual(sorted(propertyShape.disjoint), disjoint)

        lessThan = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShape.lessThan), lessThan)
        lessThanOrEquals = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShape.lessThanOrEquals), lessThanOrEquals)

        nodes = [
            'http://www.example.org/propertyShapeA',
            'http://www.example.org/propertyShapeB'
        ]
        self.assertEqual(sorted(propertyShape.nodes), nodes)

        qualifiedValueShape = [
            'http://www.example.org/friendship',
            'http://www.example.org/relationship'
        ]
        self.assertEqual(
            str(propertyShape.qualifiedValueShape.path),
            'http://www.example.org/PathC'
        )
        self.assertEqual(propertyShape.qualifiedValueShapesDisjoint, True)
        self.assertEqual(int(propertyShape.qualifiedMinCount), 1)
        self.assertEqual(int(propertyShape.qualifiedMaxCount), 2)

        propertyShape = propertyShapes[
            'http://www.example.org/exampleShapeB'
        ]
        self.assertEqual(str(propertyShape.path), 'http://www.example.org/PathB')

    def testPositiveNodeShapePropertiesParse(self):
        shapes = self.parser.parseShape(self.dir + '/positivePropertyShapeParserExample2.ttl')
        nodeShapes = shapes[0]
        nodeShape = nodeShapes[
            'http://www.example.org/exampleShape'
        ]

        for shape in nodeShape.properties:
            if str(shape.path) == 'http://www.example.org/PathA':
                propertyShapeA = shape
            else:
                propertyShapeB = shape

        classes = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShapeA.classes), classes)
        self.assertEqual(
            propertyShapeA.dataType,
            'http://www.w3.org/2001/XMLSchema#integer'
        )
        self.assertEqual(int(propertyShapeA.minCount), 1)
        self.assertEqual(int(propertyShapeA.maxCount), 2)
        self.assertEqual(int(propertyShapeA.minExclusive), 1)
        self.assertEqual(int(propertyShapeA.maxExclusive), 1)
        self.assertEqual(int(propertyShapeA.minInclusive), 1)
        self.assertEqual(int(propertyShapeA.maxInclusive), 1)
        self.assertEqual(int(propertyShapeA.minLength), 1)
        self.assertEqual(int(propertyShapeA.maxLength), 2)
        self.assertEqual(str(propertyShapeA.pattern), '[abc]')
        self.assertEqual(str(propertyShapeA.flags), 'i')

        languageIn = [
            'de',
            'en'
        ]
        self.assertEqual(sorted(propertyShapeA.languageIn), languageIn)
        self.assertEqual(propertyShapeA.uniqueLang, True)

        equals = [
            'http://www.example.org/PathB',
            'http://www.example.org/PathC'
        ]
        self.assertEqual(sorted(propertyShapeA.equals), equals)

        disjoint = [
            'http://www.example.org/PathB',
            'http://www.example.org/PathC'
        ]
        self.assertEqual(sorted(propertyShapeA.disjoint), disjoint)

        lessThan = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShapeA.lessThan), lessThan)

        lessThanOrEquals = [
            'http://www.example.org/A',
            'http://www.example.org/B'
        ]
        self.assertEqual(sorted(propertyShapeA.lessThanOrEquals), lessThanOrEquals)

        nodes = [
            'http://www.example.org/propertyShapeA',
            'http://www.example.org/propertyShapeB'
        ]
        self.assertEqual(sorted(propertyShapeA.nodes), nodes)

        qualifiedValueShape = [
            'http://www.example.org/friendship',
            'http://www.example.org/relationship'
        ]
        self.assertEqual(
            str(propertyShapeA.qualifiedValueShape.path),
            'http://www.example.org/PathC'
        )
        self.assertEqual(propertyShapeA.qualifiedValueShapesDisjoint, True)
        self.assertEqual(int(propertyShapeA.qualifiedMinCount), 1)
        self.assertEqual(int(propertyShapeA.qualifiedMaxCount), 2)
        self.assertEqual(str(propertyShapeB.path), 'http://www.example.org/PathB')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
