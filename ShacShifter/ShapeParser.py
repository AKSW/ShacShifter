#!/usr/bin/env python3

import logging
import rdflib
from rdflib.exceptions import UniquenessError
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


class ShapeParser:
    """A parser for SHACL Shapes."""

    logger = logging.getLogger('ShacShifter.ShapeParser')

    def __init__(self):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.g = rdflib.Graph()
        self.nodeShapes = {}
        self.propertyShapes = {}

    def parseShape(self, inputFilePath):
        """Parse a Shape given in a file.

        args: string inputFilePath
        returns: list of dictionaries for nodeShapes and propertyShapes
        """
        self.g.parse(inputFilePath, format='turtle')
        nodeShapeUris = self.getNodeShapeUris()
        propertyShapeUris = self.getPropertyShapeUris()

        for shapeUri in nodeShapeUris:
            nodeShape = self.parseNodeShape(shapeUri)
            self.nodeShapes[nodeShape.uri] = nodeShape

        for shapeUri in propertyShapeUris:
            if shapeUri not in self.propertyShapes:
                propertyShape = self.parsePropertyShape(shapeUri)
                self.propertyShapes[propertyShape.uri] = propertyShape

        return [self.nodeShapes, self.propertyShapes]

    def getNodeShapeUris(self):
        """Get URIs of all Node shapes.

        returns: list of Node Shape URIs
        """
        nodeShapeUris = set()

        for stmt in self.g.subjects(rdflib.RDF.type, self.sh.NodeShape):
            if stmt not in nodeShapeUris:
                nodeShapeUris.add(stmt)

        for stmt in self.g.subjects(self.sh.property, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.add(stmt)

        for stmt in self.g.subjects(self.sh.targetClass, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.add(stmt)

        for stmt in self.g.subjects(self.sh.targetNode, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.add(stmt)

        for stmt in self.g.subjects(self.sh.targetObjectsOf, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.add(stmt)

        for stmt in self.g.subjects(self.sh.targetSubjectsOf, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.append(stmt)

        for stmt in self.g.subjects(self.sh.targetSubjectsOf, None):
            if stmt not in nodeShapeUris:
                nodeShapeUris.append(stmt)

        # actually not exactly a nodeshape
        # for stmt in self.g.subjects(rdflib.RDF.type, self.sh.PropertyGroup):
        #     if not(stmt in nodeShapeUris):
        #         nodeShapeUris.append(stmt)

        return set(list(nodeShapeUris))

    def getPropertyShapeUris(self):
        """Get all property shapes.

        The property shapes must not be nodeshape properties or used in sh:not, sh:and,
        sh:or or sh:xor

        returns: list of Property Shape URIs
        """
        propertyShapeUris = []

        for stmt in self.g.subjects(self.sh.path, None):
            if (not(stmt in propertyShapeUris)
                    and not(self.g.value(predicate=self.sh.property, object=stmt))
                    and not(self.g.value(predicate=self.rdf.first, object=stmt))
                    and not(self.g.value(predicate=self.sh['not'], object=stmt))):
                propertyShapeUris.append(stmt)

        return propertyShapeUris

    def parseNodeShape(self, shapeUri):
        """Parse a NodeShape given by its URI.

        args:   graph g
                string shapeUri
        returns: object NodeShape
        """
        nodeShape = NodeShape()
        nodeShape.uri = str(shapeUri)

        for stmt in self.g.objects(shapeUri, self.sh.targetClass):
            nodeShape.isSet['targetClass'] = True
            nodeShape.targetClass.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetNode):
            nodeShape.isSet['targetNode'] = True
            nodeShape.targetNode.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetObjectsOf):
            nodeShape.isSet['targetObjectsOf'] = True
            nodeShape.targetObjectsOf.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetSubjectsOf):
            nodeShape.isSet['targetSubjectsOf'] = True
            nodeShape.targetSubjectsOf.append(str(stmt))

        val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
        if val is not None:
            nodeShape.isSet['ignoredProperties'] = True
            properties = val
            lastListEntry = False

            while not lastListEntry:
                nodeShape.ignoredProperties.append(
                    str(self.g.value(subject=properties, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=properties, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                properties = self.g.value(subject=properties, predicate=self.rdf.rest)

        for stmt in self.g.objects(shapeUri, self.sh.message):
            nodeShape.isSet['message'] = True
            if (stmt.language is None):
                nodeShape.message['default'] = str(stmt)
            else:
                nodeShape.message[stmt.language] = str(stmt)

        val = self.g.value(subject=shapeUri, predicate=self.sh.nodeKind)
        if val is not None:
            nodeShape.isSet['nodeKind'] = True
            nodeShape.nodeKind = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.closed)
        if val is not None:
            nodeShape.isSet['closed'] = True
            if (str(val).lower() == "true"):
                nodeShape.closed = True

        for stmt in self.g.objects(shapeUri, self.sh.property):
            nodeShape.isSet['property'] = True
            propertyShape = self.parsePropertyShape(stmt)
            self.propertyShapes[stmt] = propertyShape
            nodeShape.properties.append(propertyShape)

        return nodeShape

    def parsePropertyShape(self, shapeUri):
        """Parse a PropertyShape given by its URI.

        args:   graph g
                string shapeUri
        returns: object PropertyShape
        """
        propertyShape = PropertyShape()
        self.logger.debug('Parsing PropertyShape with URI {}'.format(shapeUri))

        if shapeUri != rdflib.term.BNode(shapeUri):
            propertyShape.isSet['uri'] = True
            propertyShape.uri = str(shapeUri)
        pathStart = self.g.value(subject=shapeUri, predicate=self.sh.path)
        propertyShape.path = self.getPropertyPath(pathStart)

        for stmt in self.g.objects(shapeUri, self.sh['class']):
            propertyShape.isSet['classes'] = True
            propertyShape.classes.append(str(stmt))

        val = self.g.value(subject=shapeUri, predicate=self.sh['name'])
        if val is not None:
            propertyShape.isSet['name'] = True
            propertyShape.name = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh['description'])
        if val is not None:
            propertyShape.isSet['description'] = True
            propertyShape.description = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.datatype)
        if val is not None:
            propertyShape.isSet['dataType'] = True
            propertyShape.dataType = str(val)

        try:
            minCount = self.g.value(subject=shapeUri, predicate=self.sh.minCount, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.minCount))

        if minCount is not None:
            propertyShape.isSet['minCount'] = True
            propertyShape.minCount = int(minCount)

        try:
            maxCount = self.g.value(subject=shapeUri, predicate=self.sh.maxCount, any=False)
        except UniquenessError:
            raise Exception('Conflict found. More than one value for {}'.format(self.sh.maxCount))

        if maxCount is not None:
            propertyShape.isSet['maxCount'] = True
            propertyShape.maxCount = int(maxCount)
            if (propertyShape.isSet['minCount'] and
                    propertyShape.minCount > propertyShape.maxCount):
                raise Exception(
                    'Conflict found. sh:maxCount {} must be greater or eqal sh:minCount {}'
                    .format(propertyShape.maxCount, propertyShape.minCount))

        val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive)
        if val is not None:
            propertyShape.isSet['minExclusive'] = True
            propertyShape.minExclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive)
        if val is not None:
            propertyShape.isSet['minInclusive'] = True
            propertyShape.minInclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive)
        if val is not None:
            propertyShape.isSet['maxExclusive'] = True
            propertyShape.maxExclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive)
        if val is not None:
            propertyShape.isSet['maxInclusive'] = True
            propertyShape.maxInclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minLength)
        if val is not None:
            propertyShape.isSet['minLength'] = True
            propertyShape.minLength = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength)
        if val is not None:
            propertyShape.isSet['maxLength'] = True
            propertyShape.maxLength = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.pattern)
        if val is not None:
            propertyShape.isSet['pattern'] = True
            propertyShape.pattern = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.flags)
        if val is not None:
            propertyShape.isSet['flags'] = True
            propertyShape.flags = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn)
        if val is not None:
            propertyShape.isSet['languageIn'] = True
            languages = val
            lastListEntry = False

            while not lastListEntry:
                propertyShape.languageIn.append(
                    str(self.g.value(subject=languages, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=languages, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                languages = self.g.value(subject=languages, predicate=self.rdf.rest)

        val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang)
        if val is not None:
            propertyShape.isSet['uniqueLang'] = True
            if (str(val).lower() == "true"):
                propertyShape.uniqueLang = True

        for stmt in self.g.objects(shapeUri, self.sh.equals):
            propertyShape.isSet['equals'] = True
            propertyShape.equals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.disjoint):
            propertyShape.isSet['disjoint'] = True
            propertyShape.disjoint.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThan):
            propertyShape.isSet['lessThan'] = True
            propertyShape.lessThan.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThanOrEquals):
            propertyShape.isSet['lessThanOrEquals'] = True
            propertyShape.lessThanOrEquals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.node):
            propertyShape.isSet['node'] = True
            propertyShape.nodes.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.hasValue):
            propertyShape.isSet['hasValue'] = True
            propertyShape.hasValue.append(stmt)

        val = self.g.value(subject=shapeUri, predicate=self.sh['in'])
        if val is not None:
            propertyShape.isSet['shIn'] = True
            lastListEntry = False

            while not lastListEntry:
                propertyShape.shIn.append(self.g.value(subject=val, predicate=self.rdf.first))
                # check if this was the last entry in the list
                if self.g.value(subject=val, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                val = str(self.g.value(subject=val, predicate=self.rdf.rest))

        val = self.g.value(subject=shapeUri, predicate=self.sh.order)
        if val is not None:
            propertyShape.isSet['order'] = True
            propertyShape.order = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape)
        if val is not None:
            propertyShape.isSet['qualifiedValueShape'] = True
            propertyShape.qualifiedValueShape = self.parsePropertyShape(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapeDisjoint)
        if val is not None:
            propertyShape.isSet['qualifiedValueShapeDisjoint'] = True
            if (str(val).lower() == "true"):
                propertyShape.qualifiedValueShapeDisjoint = True

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount)
        if val is not None:
            propertyShape.isSet['qualifiedMinCount'] = True
            propertyShape.qualifiedMinCount = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount)
        if val is not None:
            propertyShape.isSet['qualifiedMaxCount'] = True
            propertyShape.qualifiedMaxCount = int(val)

        for stmt in self.g.objects(shapeUri, self.sh.message):
            propertyShape.isSet['message'] = True
            if (stmt.language is None):
                propertyShape.message['default'] = str(stmt)
            else:
                propertyShape.message[stmt.language] = str(stmt)

        return propertyShape

    def getPropertyPath(self, pathUri):
        # not enforcing blank nodes here, but stripping the link nodes from the data structure
        newPathUri = self.g.value(subject=pathUri, predicate=self.rdf.first)
        if newPathUri is not None:
            rdfList = []
            rdfList.append(self.getPropertyPath(newPathUri))

            if not (self.g.value(subject=pathUri, predicate=self.rdf.rest) == self.rdf.nil):
                newPathUri = self.g.value(subject=pathUri, predicate=self.rdf.rest)
                rest = self.getPropertyPath(newPathUri)
                if (isinstance(rest, list)):
                    rdfList += rest
                else:
                    rdfList.append(rest)

            return rdfList

        altPath = self.g.value(subject=pathUri, predicate=self.sh.alternativePath)
        if altPath is not None:
            newPathUri = altPath
            rdfDict = {self.sh.alternativePath: self.getPropertyPath(altPath)}
            return rdfDict

        invPath = self.g.value(subject=pathUri, predicate=self.sh.inversePath)
        if invPath is not None:
            rdfDict = {self.sh.inversePath: self.getPropertyPath(invPath)}
            return rdfDict

        zeroOrMorePath = self.g.value(subject=pathUri, predicate=self.sh.zeroOrMorePath)
        if zeroOrMorePath is not None:
            rdfDict = {self.sh.zeroOrMorePath: self.getPropertyPath(zeroOrMorePath)}
            return rdfDict

        oneOrMorePath = self.g.value(subject=pathUri, predicate=self.sh.oneOrMorePath)
        if oneOrMorePath is not None:
            rdfDict = {self.sh.oneOrMorePath: self.getPropertyPath(oneOrMorePath)}
            return rdfDict

        zeroOrOnePath = self.g.value(subject=pathUri, predicate=self.sh.zeroOrOnePath)
        if zeroOrOnePath is not None:
            rdfDict = {self.sh.zeroOrOnePath: self.getPropertyPath(zeroOrOnePath)}
            return rdfDict

        # last Object in this Pathpart, check if its an Uri and return it
        if pathUri == rdflib.term.URIRef(pathUri):
            return str(pathUri)
        else:
            raise Exception('Object of sh:path is no URI')
