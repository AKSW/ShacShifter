import rdflib
import argparse
import rdfextras
class ShapeParser:
    def parseShape(self, inputFilePath):
        g = rdflib.Graph()
        g.parse(inputFilePath, format='turtle')
        nodeShapeUris = self.getNodeShapeUris(g)
        propertyShapeUris = self.getPropertyShapeUris(g)
        nodeShapes = {}
        propertyShapes = {}
        for shapeUri in nodeShapeUris:
            nodeShape = self.parseNodeShape(g, shapeUri)
            nodeShapes[nodeShape.uri] = nodeShape
        for uri, shape in nodeShapes.items():
            print(uri)
            print('targets:')
            for target in (shape.targetClass + shape.targetNode + shape.targetSubjectsOf + shape.targetObjectsOf):
                print(target)
            print('nodeKind:')
            print(shape.nodeKind)
            for message in shape.message:
                print(message.lang + ':' + message)
            print('-------------------------------------------------------------')

    def getNodeShapeUris(self, g):
        nodeShapeUris = []
        #probably not a full list, as long as no Grammar exists, its probably staying incomplete
        #shacl-shacl could be analyzed for that
        #ignores sh:or/and/not/xone for now, they can be in node and property shapes, and can contain both as shacl list
        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
            rdflib.term.URIRef('http://www.w3.org/ns/shacl#NodeShape')):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#property'), None): #or/and/xor lists filtered, shouldnt be added here either way
            if not(stmt in nodeShapeUris) and stmt != rdflib.term.BNode(stmt):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetClass'), None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetNode'), None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetObjectsOf'), None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetSubjectsOf'), None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetSubjectsOf'), None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        #actually not exactly a nodeshape
        for stmt in g.subjects(rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
            rdflib.term.URIRef('http://www.w3.org/ns/shacl#PropertyGroup')):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        return nodeShapeUris

    def getPropertyShapeUris(self, g):
        return []

    def parseNodeShape(self, g, shapeUri):
        nodeShape = NodeShape()
        nodeShape.uri = shapeUri
        for stmt in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetClass')):
            nodeShape.targetClass.append(stmt)

        for stmt in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetNode')):
            nodeShape.targetNode.append(stmt)

        for stmt in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetObjectsOf')):
            nodeShape.targetObjectsOf.append(stmt)

        for stmt in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#targetSubjectsOf')):
            nodeShape.targetSubjectsOf.append(stmt)

        nodeKind = g.value(subject=shapeUri, predicate=rdflib.term.URIRef('http://www.w3.org/ns/shacl#nodeKind'))
        if nodeKind != None:
            nodeShape.nodeKind = nodeKind

        for stmt in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#message')):
            if (stmt.lang == None):
                nodeShape.message['general'] = stmt
            else:
                nodeShape.message[stmt.lang] = stmt

        for bn in g.objects(shapeUri, rdflib.term.URIRef('http://www.w3.org/ns/shacl#property')):
            propertyShape = self.parsePropertyShape(g, bn)
            nodeShape.properties.append(propertyShape)

        return nodeShape

    def parsePropertyShape(self, g, shapeUri):
        propertyShape = PropertyShape()
        return propertyShape

class NodeShape:
    def __init__(self):
        self.uri = ''
        self.targetClass = []
        self.targetNode = []
        self.targetObjectsOf = []
        self.targetSubjectsOf = []
        self.nodeKind = ''
        self.properties = []
        self.closed = False
        self.ignoredProperties = []
        self.sOr = []
        self.sNot = []
        self.sAnd = []
        self.sXone = []
        self.message = {}
        self.severity = -1
    #self.sparql used for non core constraints
    #can have obviously more properties, but we need to filter the relevant ones
    #closed probably irrelevant for forms, ignoredProperties too, the logical operators are probably tricky to evaluate
    #everything that doesnt contain sh:path is a nodeshape -> groups (sh:PropertyGroup) are kind of nodeshapes, 
    #though they could be seen as another class
class PropertyShape:
    def __init__(self):
        self.uri = '' #stays empty if its a blank node/in the nodeshape
        self.path = ''
    #everything that has sh:path as predicate
#2 is way slower (about 1,9 whole seconds for a single result)
#class ShapeParser2:
#    def __init__ (self, inputFilePath):
#        g = rdflib.Graph()
#        result = g.parse(inputFilePath, format='turtle')
#        print(len(g))
#        for row in g.query("""Select ?s where { ?s a <http://www.w3.org/ns/shacl#NodeShape> .}"""):
#            print(row);

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--shacl', type=str, help="The input SHACL file")
args = parser.parse_args()
sparser = ShapeParser()
sparser.parseShape(args.shacl)


