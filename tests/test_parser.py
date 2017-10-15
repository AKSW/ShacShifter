import unittest
import rdflib
from os import path
from context import ShacShifter
from ShacShifter.ShacShifter import ShacShifter
from ShacShifter.ShapeParser import ShapeParser
from ShacShifter.modules.NodeShape import NodeShape
from ShacShifter.modules.PropertyShape import PropertyShape


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
        propertyShape = propertyShapes[rdflib.term.URIRef('http://www.example.org/example/exampleShapeA')]

def main():
    unittest.main()

if __name__ == '__main__':
    main()
