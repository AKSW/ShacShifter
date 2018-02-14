import unittest
import rdflib
from os import path
from context import ShacShifter
from ShacShifter.ShapeParser import ShapeParser


class ShapeParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = ShapeParser()
        self.dir = path.abspath('tests/_files')

    def tearDown(self):
        self.parser = None
        self.dir = None

    def testPositiveNodeShapeParse(self):
        shapes = self.parser.parseShape(self.dir + '/positiveNodeShapeParserExample1.ttl')
        nodeShapes = shapes[0]
        nodeShape = nodeShapes[rdflib.term.URIRef('http://www.example.org/example/exampleShape')]
        self.assertEqual(str(nodeShape.uri), 'http://www.example.org/example/exampleShape')

        targetClasses = [
            rdflib.term.URIRef('http://www.example.org/example/Animal'),
            rdflib.term.URIRef('http://www.example.org/example/Person')
        ]
        self.assertEqual(sorted(nodeShape.targetClass), targetClasses)

        targetNodes = [
            rdflib.term.URIRef('http://www.example.org/example/Alice'),
            rdflib.term.URIRef('http://www.example.org/example/Bob')
        ]
        self.assertEqual(sorted(nodeShape.targetNode), targetNodes)

        relationships = [
            rdflib.term.URIRef('http://www.example.org/example/friendship'),
            rdflib.term.URIRef('http://www.example.org/example/relationship')
        ]
        self.assertEqual(sorted(nodeShape.targetObjectsOf), relationships)
        self.assertEqual(sorted(nodeShape.targetSubjectsOf), relationships)
        self.assertEqual(str(nodeShape.nodeKind), 'http://www.w3.org/ns/shacl#IRI')
        self.assertEqual(nodeShape.closed, True)

        ignoredProperties = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B'),
            rdflib.term.URIRef('http://www.example.org/example/C')
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
            rdflib.term.URIRef('http://www.example.org/example/exampleShapeA')
        ]

        self.assertEqual(str(propertyShape.uri), 'http://www.example.org/example/exampleShapeA')
        self.assertEqual(str(propertyShape.path), 'http://www.example.org/example/PathA')

        classes = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShape.classes), classes)
        self.assertEqual(
            propertyShape.dataType,
            rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')
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
            rdflib.term.Literal('de'),
            rdflib.term.Literal('en')
        ]
        self.assertEqual(sorted(propertyShape.languageIn), languageIn)
        self.assertEqual(propertyShape.uniqueLang, True)

        equals = [
            rdflib.term.URIRef('http://www.example.org/example/PathB'),
            rdflib.term.URIRef('http://www.example.org/example/PathC')
        ]
        self.assertEqual(sorted(propertyShape.equals), equals)

        disjoint = [
            rdflib.term.URIRef('http://www.example.org/example/PathB'),
            rdflib.term.URIRef('http://www.example.org/example/PathC')
        ]
        self.assertEqual(sorted(propertyShape.disjoint), disjoint)

        lessThan = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShape.lessThan), lessThan)
        lessThanOrEquals = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShape.lessThanOrEquals), lessThanOrEquals)

        nodes = [
            rdflib.term.URIRef('http://www.example.org/example/propertyShapeA'),
            rdflib.term.URIRef('http://www.example.org/example/propertyShapeB')
        ]
        self.assertEqual(sorted(propertyShape.nodes), nodes)

        qualifiedValueShape = [
            rdflib.term.URIRef('http://www.example.org/example/friendship'),
            rdflib.term.URIRef('http://www.example.org/example/relationship')
        ]
        self.assertEqual(
            str(propertyShape.qualifiedValueShape.path),
            'http://www.example.org/example/PathC'
        )
        self.assertEqual(propertyShape.qualifiedValueShapeDisjoint, True)
        self.assertEqual(int(propertyShape.qualifiedMinCount), 1)
        self.assertEqual(int(propertyShape.qualifiedMaxCount), 2)

        propertyShape = propertyShapes[
            rdflib.term.URIRef('http://www.example.org/example/exampleShapeB')
        ]
        self.assertEqual(str(propertyShape.path), 'http://www.example.org/example/PathB')

    def testPositiveNodeShapePropertiesParse(self):
        shapes = self.parser.parseShape(self.dir + '/positivePropertyShapeParserExample2.ttl')
        nodeShapes = shapes[0]
        nodeShape = nodeShapes[
            rdflib.term.URIRef('http://www.example.org/example/exampleShape')
        ]

        for shape in nodeShape.properties:
            if str(shape.path) == 'http://www.example.org/example/PathA':
                propertyShapeA = shape
            else:
                propertyShapeB = shape

        classes = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShapeA.classes), classes)
        self.assertEqual(
            propertyShapeA.dataType,
            rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')
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
            rdflib.term.Literal('de'),
            rdflib.term.Literal('en')
        ]
        self.assertEqual(sorted(propertyShapeA.languageIn), languageIn)
        self.assertEqual(propertyShapeA.uniqueLang, True)

        equals = [
            rdflib.term.URIRef('http://www.example.org/example/PathB'),
            rdflib.term.URIRef('http://www.example.org/example/PathC')
        ]
        self.assertEqual(sorted(propertyShapeA.equals), equals)

        disjoint = [
            rdflib.term.URIRef('http://www.example.org/example/PathB'),
            rdflib.term.URIRef('http://www.example.org/example/PathC')
        ]
        self.assertEqual(sorted(propertyShapeA.disjoint), disjoint)

        lessThan = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShapeA.lessThan), lessThan)

        lessThanOrEquals = [
            rdflib.term.URIRef('http://www.example.org/example/A'),
            rdflib.term.URIRef('http://www.example.org/example/B')
        ]
        self.assertEqual(sorted(propertyShapeA.lessThanOrEquals), lessThanOrEquals)

        nodes = [
            rdflib.term.URIRef('http://www.example.org/example/propertyShapeA'),
            rdflib.term.URIRef('http://www.example.org/example/propertyShapeB')
        ]
        self.assertEqual(sorted(propertyShapeA.nodes), nodes)

        qualifiedValueShape = [
            rdflib.term.URIRef('http://www.example.org/example/friendship'),
            rdflib.term.URIRef('http://www.example.org/example/relationship')
        ]
        self.assertEqual(
            str(propertyShapeA.qualifiedValueShape.path),
            'http://www.example.org/example/PathC'
        )
        self.assertEqual(propertyShapeA.qualifiedValueShapeDisjoint, True)
        self.assertEqual(int(propertyShapeA.qualifiedMinCount), 1)
        self.assertEqual(int(propertyShapeA.qualifiedMaxCount), 2)
        self.assertEqual(str(propertyShapeB.path), 'http://www.example.org/example/PathB')


def main():
    unittest.main()


if __name__ == '__main__':
    main()
