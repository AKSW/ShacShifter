#!/usr/bin/env python3

import rdflib
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


class ShapeParser:
    """A parser for SHACL Shapes."""

    def __init__(self):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')

    def parseShape(self, inputFilePath):
        """Parse a Shape given in a file.

        args: string inputFilePath
        returns: list of dictionaries for nodeShapes and propertyShapes
        """
        g = rdflib.Graph()
        g.parse(inputFilePath, format='turtle')
        nodeShapeUris = self.getNodeShapeUris(g)
        propertyShapeUris = self.getPropertyShapeUris(g)
        nodeShapes = {}
        propertyShapes = {}

        for shapeUri in nodeShapeUris:
            nodeShape = self.parseNodeShape(g, shapeUri)
            nodeShapes[nodeShape.uri] = nodeShape

        for shapeUri in propertyShapeUris:
            propertyShape = self.parsePropertyShape(g, shapeUri)
            propertyShapes[propertyShape.uri] = propertyShape

        return [nodeShapes, propertyShapes]

    def getNodeShapeUris(self, g):
        """Get URIs of all Node shapes.

        args: graph g
        returns: list of Node Shape URIs
        """
        nodeShapeUris = []

        for stmt in g.subjects(rdflib.RDF.type, self.sh.NodeShape):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.property, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.targetClass, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.targetNode, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.targetObjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.targetSubjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(self.sh.targetSubjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        # actually not exactly a nodeshape
        # for stmt in g.subjects(rdflib.RDF.type, self.sh.PropertyGroup):
        #     if not(stmt in nodeShapeUris):
        #         nodeShapeUris.append(stmt)

        return nodeShapeUris

    def getPropertyShapeUris(self, g):
        """Get all property shapes.

        The property shapes must not be nodeshape properties or used in sh:not, sh:and,
        sh:or or sh:xor

        args: graph g
        returns: list of Property Shape URIs
        """
        propertyShapeUris = []

        for stmt in g.subjects(self.sh.path, None):
            if (not(stmt in propertyShapeUris)
                    and not(g.value(predicate=self.sh.property, object=stmt))
                    and not(g.value(predicate=self.rdf.first, object=stmt))
                    and not(g.value(predicate=self.sh['not'], object=stmt))):
                propertyShapeUris.append(stmt)

        return propertyShapeUris

    def parseNodeShape(self, g, shapeUri):
        """Parse a NodeShape given by its URI.

        args:   graph g
                string shapeUri
        returns: object NodeShape
        """
        nodeShape = NodeShape()
        nodeShape.uri = str(shapeUri)
        for stmt in g.objects(shapeUri, self.sh.targetClass):
            nodeShape.isSet['targetClass'] = True
            nodeShape.targetClass.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.targetNode):
            nodeShape.isSet['targetNode'] = True
            nodeShape.targetNode.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.targetObjectsOf):
            nodeShape.isSet['targetObjectsOf'] = True
            nodeShape.targetObjectsOf.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.targetSubjectsOf):
            nodeShape.isSet['targetSubjectsOf'] = True
            nodeShape.targetSubjectsOf.append(str(stmt))

        if not (g.value(subject=shapeUri, predicate=self.sh.ignoredProperties) is None):
            nodeShape.isSet['ignoredProperties'] = True
            properties = g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
            lastListEntry = False

            while not lastListEntry:
                nodeShape.ignoredProperties.append(
                    str(g.value(subject=properties, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if g.value(subject=properties, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                properties = g.value(subject=properties, predicate=self.rdf.rest)

        for stmt in g.objects(shapeUri, self.sh.message):
            nodeShape.isSet['message'] = True
            if (stmt.language is None):
                nodeShape.message['default'] = str(stmt)
            else:
                nodeShape.message[stmt.language] = str(stmt)

        if not (g.value(subject=shapeUri, predicate=self.sh.nodeKind) is None):
            nodeShape.isSet['nodeKind'] = True
            nodeShape.nodeKind = str(g.value(subject=shapeUri, predicate=self.sh.nodeKind))

        if not (g.value(subject=shapeUri, predicate=self.sh.closed) is None):
            nodeShape.isSet['closed'] = True
            value = g.value(subject=shapeUri, predicate=self.sh.closed).lower()
            if (value == "true"):
                nodeShape.closed = True

        for stmt in g.objects(shapeUri, self.sh.property):
            nodeShape.isSet['property'] = True
            propertyShape = self.parsePropertyShape(g, stmt)
            nodeShape.properties.append(propertyShape)

        return nodeShape

    def parsePropertyShape(self, g, shapeUri):
        """Parse a PropertyShape given by its URI.

        args:   graph g
                string shapeUri
        returns: object PropertyShape
        """
        propertyShape = PropertyShape()

        if shapeUri != rdflib.term.BNode(shapeUri):
            propertyShape.isSet['uri'] = True
            propertyShape.uri = str(shapeUri)
        pathStart = g.value(subject=shapeUri, predicate=self.sh.path)
        propertyShape.path = self.getPropertyPath(g, pathStart)

        for stmt in g.objects(shapeUri, self.sh['class']):
            propertyShape.isSet['classes'] = True
            propertyShape.classes.append(str(stmt))

        if not (g.value(subject=shapeUri, predicate=self.sh.datatype) is None):
            propertyShape.isSet['dataType'] = True
            propertyShape.dataType = str(g.value(subject=shapeUri, predicate=self.sh.datatype))

        if not (g.value(subject=shapeUri, predicate=self.sh.minCount) is None):
            propertyShape.isSet['minCount'] = True
            propertyShape.minCount = int(g.value(subject=shapeUri, predicate=self.sh.minCount))

        if not (g.value(subject=shapeUri, predicate=self.sh.maxCount) is None):
            propertyShape.isSet['maxCount'] = True
            propertyShape.maxCount = int(g.value(subject=shapeUri, predicate=self.sh.maxCount))

        if not (g.value(subject=shapeUri, predicate=self.sh.minExclusive) is None):
            propertyShape.isSet['minExclusive'] = True
            propertyShape.minExclusive = int(
                g.value(subject=shapeUri, predicate=self.sh.minExclusive))

        if not (g.value(subject=shapeUri, predicate=self.sh.minInclusive) is None):
            propertyShape.isSet['minInclusive'] = True
            propertyShape.minInclusive = int(
                g.value(subject=shapeUri, predicate=self.sh.minInclusive))

        if not (g.value(subject=shapeUri, predicate=self.sh.maxExclusive) is None):
            propertyShape.isSet['maxExclusive'] = True
            propertyShape.maxExclusive = int(
                g.value(subject=shapeUri, predicate=self.sh.maxExclusive))

        if not (g.value(subject=shapeUri, predicate=self.sh.maxInclusive) is None):
            propertyShape.isSet['maxInclusive'] = True
            propertyShape.maxInclusive = int(
                g.value(subject=shapeUri, predicate=self.sh.maxInclusive))

        if not (g.value(subject=shapeUri, predicate=self.sh.minLength) is None):
            propertyShape.isSet['minLength'] = True
            propertyShape.minLength = int(g.value(subject=shapeUri, predicate=self.sh.minLength))

        if not (g.value(subject=shapeUri, predicate=self.sh.maxLength) is None):
            propertyShape.isSet['maxLength'] = True
            propertyShape.maxLength = int(g.value(subject=shapeUri, predicate=self.sh.maxLength))

        if not (g.value(subject=shapeUri, predicate=self.sh.pattern) is None):
            propertyShape.isSet['pattern'] = True
            propertyShape.pattern = str(g.value(subject=shapeUri, predicate=self.sh.pattern))

        if not (g.value(subject=shapeUri, predicate=self.sh.flags) is None):
            propertyShape.isSet['flags'] = True
            propertyShape.flags = str(g.value(subject=shapeUri, predicate=self.sh.flags))

        if not (g.value(subject=shapeUri, predicate=self.sh.languageIn) is None):
            propertyShape.isSet['languageIn'] = True
            languages = g.value(subject=shapeUri, predicate=self.sh.languageIn)
            lastListEntry = False

            while not lastListEntry:
                propertyShape.languageIn.append(
                    str(g.value(subject=languages, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if g.value(subject=languages, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                languages = g.value(subject=languages, predicate=self.rdf.rest)

        if not (g.value(subject=shapeUri, predicate=self.sh.uniqueLang) is None):
            propertyShape.isSet['uniqueLang'] = True
            uniqueLang = g.value(subject=shapeUri, predicate=self.sh.uniqueLang).lower()
            if (uniqueLang == "true"):
                propertyShape.uniqueLang = True

        for stmt in g.objects(shapeUri, self.sh.equals):
            propertyShape.isSet['equals'] = True
            propertyShape.equals.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.disjoint):
            propertyShape.isSet['disjoint'] = True
            propertyShape.disjoint.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.lessThan):
            propertyShape.isSet['lessThan'] = True
            propertyShape.lessThan.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.lessThanOrEquals):
            propertyShape.isSet['lessThanOrEquals'] = True
            propertyShape.lessThanOrEquals.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.node):
            propertyShape.isSet['node'] = True
            propertyShape.nodes.append(str(stmt))

        for stmt in g.objects(shapeUri, self.sh.hasValue):
            propertyShape.isSet['hasValue'] = True
            propertyShape.hasValue.append(stmt)

        if not (g.value(subject=shapeUri, predicate=self.sh['in']) is None):
            propertyShape.isSet['shIn'] = True
            values = g.value(subject=shapeUri, predicate=self.sh['in'])
            lastListEntry = False

            while not lastListEntry:
                propertyShape.shIn.append(g.value(subject=values, predicate=self.rdf.first))
                # check if this was the last entry in the list
                if g.value(subject=values, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                values = str(g.value(subject=values, predicate=self.rdf.rest))

        if not (g.value(subject=shapeUri, predicate=self.sh.order) is None):
            propertyShape.isSet['order'] = True
            propertyShape.order = int(g.value(subject=shapeUri, predicate=self.sh.order))

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape) is None):
            propertyShape.isSet['qualifiedValueShape'] = True
            qvsUri = g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape)
            propertyShape.qualifiedValueShape = self.parsePropertyShape(g, qvsUri)

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapeDisjoint) is None):
            propertyShape.isSet['qualifiedValueShapeDisjoint'] = True
            qualifiedValueShapeDisjoint = str(g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedValueShapeDisjoint
            ).lower())
            if (qualifiedValueShapeDisjoint == "true"):
                propertyShape.qualifiedValueShapeDisjoint = True

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount) is None):
            propertyShape.isSet['qualifiedMinCount'] = True
            propertyShape.qualifiedMinCount = int(g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedMinCount
            ))

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount) is None):
            propertyShape.isSet['qualifiedMaxCount'] = True
            propertyShape.qualifiedMaxCount = int(g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedMaxCount
            ))

        for stmt in g.objects(shapeUri, self.sh.message):
            propertyShape.isSet['message'] = True
            if (stmt.language is None):
                propertyShape.message['default'] = str(stmt)
            else:
                propertyShape.message[stmt.language] = str(stmt)

        return propertyShape

    def getPropertyPath(self, g, pathUri):
        # not enforcing blank nodes here, but stripping the link nodes from the data structure
        if not (g.value(subject=pathUri, predicate=self.rdf.first) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.rdf.first)
            rdfList = []
            rdfList.append(self.getPropertyPath(g, newPathUri))

            if not (g.value(subject=pathUri, predicate=self.rdf.rest) == self.rdf.nil):
                newPathUri = g.value(subject=pathUri, predicate=self.rdf.rest)
                rest = self.getPropertyPath(g, newPathUri)
                if (isinstance(rest, list)):
                    rdfList += rest
                else:
                    rdfList.append(rest)

            return rdfList

        if not (g.value(subject=pathUri, predicate=self.sh.alternativePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.sh.alternativePath)
            rdfDict = {self.sh.alternativePath: self.getPropertyPath(g, newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=self.sh.inversePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.sh.inversePath)
            rdfDict = {self.sh.inversePath: self.getPropertyPath(g, newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=self.sh.zeroOrMorePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.sh.zeroOrMorePath)
            rdfDict = {self.sh.zeroOrMorePath: self.getPropertyPath(g, newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=self.sh.oneOrMorePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.sh.oneOrMorePath)
            rdfDict = {self.sh.oneOrMorePath: self.getPropertyPath(g, newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=self.sh.zeroOrOnePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=self.sh.zeroOrOnePath)
            rdfDict = {self.sh.zeroOrOnePath: self.getPropertyPath(g, newPathUri)}
            return rdfDict

        # last Object in this Pathpart, check if its an Uri and return it
        if pathUri == rdflib.term.URIRef(pathUri):
            return str(pathUri)
        else:
            raise Exception('Object of sh:path is no URI')
