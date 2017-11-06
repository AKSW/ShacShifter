#!/usr/bin/env python3

import rdflib
import argparse
import rdfextras
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


class ShapeParser:

    def __init__(self):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')

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
        for shapeUri in propertyShapeUris:
            propertyShape = self.parsePropertyShape(g, shapeUri)
            propertyShapes[propertyShape.uri] = propertyShape
        return [nodeShapes, propertyShapes]

    def getNodeShapeUris(self, g):
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
        # filter all property shapes that arent nodeshape properties
        # or used in sh:not,and,or,xor
        propertyShapeUris = []
        for stmt in g.subjects(self.sh.path, None):
            if (not(stmt in propertyShapeUris)
                    and not(g.value(predicate=self.sh.property, object=stmt))
                    and not(g.value(predicate=self.rdf.first, object=stmt))
                    and not(g.value(predicate=self.sh['not'], object=stmt))):
                propertyShapeUris.append(stmt)
        return propertyShapeUris

    def parseNodeShape(self, g, shapeUri):
        nodeShape = NodeShape()
        nodeShape.uri = shapeUri
        for stmt in g.objects(shapeUri, self.sh.targetClass):
            nodeShape.targetClass.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.targetNode):
            nodeShape.targetNode.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.targetObjectsOf):
            nodeShape.targetObjectsOf.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.targetSubjectsOf):
            nodeShape.targetSubjectsOf.append(stmt)

        nodeKind = g.value(subject=shapeUri, predicate=self.sh.nodeKind)
        if nodeKind == (not None):
            nodeShape.nodeKind = nodeKind

        if not (g.value(subject=shapeUri, predicate=self.sh.ignoredProperties) is None):
            properties = g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
            lastListEntry = False
            while not lastListEntry:
                nodeShape.ignoredProperties.append(
                    g.value(subject=properties, predicate=self.rdf.first)
                )
                # check if this was the last entry in the list
                if g.value(subject=properties, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                properties = g.value(subject=properties, predicate=self.rdf.rest)

        for stmt in g.objects(shapeUri, self.sh.message):
            if (stmt.language is None):
                nodeShape.message['default'] = stmt
            else:
                nodeShape.message[stmt.language] = stmt

        if not (g.value(subject=shapeUri, predicate=self.sh.nodeKind) is None):
            nodeShape.nodeKind = g.value(subject=shapeUri, predicate=self.sh.nodeKind)

        if not (g.value(subject=shapeUri, predicate=self.sh.closed) is None):
            value = g.value(subject=shapeUri, predicate=self.sh.closed).lower()
            if (value == "true"):
                nodeShape.closed = True

        for stmt in g.objects(shapeUri, self.sh.property):
            propertyShape = self.parsePropertyShape(g, stmt)
            nodeShape.properties.append(propertyShape)

        return nodeShape

    def parsePropertyShape(self, g, shapeUri):
        propertyShape = PropertyShape()
        if shapeUri != rdflib.term.BNode(shapeUri):
            propertyShape.uri = shapeUri
        pathStart = g.value(subject=shapeUri, predicate=self.sh.path)
        propertyShape.path = self.getPropertyPath(g, pathStart)

        for stmt in g.objects(shapeUri, self.sh['class']):
            propertyShape.classes.append(stmt)

        if not (g.value(subject=shapeUri, predicate=self.sh.datatype) is None):
            propertyShape.dataType = g.value(subject=shapeUri, predicate=self.sh.datatype)

        if not (g.value(subject=shapeUri, predicate=self.sh.minCount) is None):
            propertyShape.minCount = g.value(subject=shapeUri, predicate=self.sh.minCount)

        if not (g.value(subject=shapeUri, predicate=self.sh.maxCount) is None):
            propertyShape.maxCount = g.value(subject=shapeUri, predicate=self.sh.maxCount)

        if not (g.value(subject=shapeUri, predicate=self.sh.minExclusive) is None):
            propertyShape.minExclusive = g.value(subject=shapeUri, predicate=self.sh.minExclusive)

        if not (g.value(subject=shapeUri, predicate=self.sh.minInclusive) is None):
            propertyShape.minInclusive = g.value(subject=shapeUri, predicate=self.sh.minInclusive)

        if not (g.value(subject=shapeUri, predicate=self.sh.maxExclusive) is None):
            propertyShape.maxExclusive = g.value(subject=shapeUri, predicate=self.sh.maxExclusive)

        if not (g.value(subject=shapeUri, predicate=self.sh.maxInclusive) is None):
            propertyShape.maxInclusive = g.value(subject=shapeUri, predicate=self.sh.maxInclusive)

        if not (g.value(subject=shapeUri, predicate=self.sh.minLength) is None):
            propertyShape.minLength = g.value(subject=shapeUri, predicate=self.sh.minLength)

        if not (g.value(subject=shapeUri, predicate=self.sh.maxLength) is None):
            propertyShape.maxLength = g.value(subject=shapeUri, predicate=self.sh.maxLength)

        if not (g.value(subject=shapeUri, predicate=self.sh.pattern) is None):
            propertyShape.pattern = g.value(subject=shapeUri, predicate=self.sh.pattern)

        if not (g.value(subject=shapeUri, predicate=self.sh.flags) is None):
            propertyShape.flags = g.value(subject=shapeUri, predicate=self.sh.flags)

        if not (g.value(subject=shapeUri, predicate=self.sh.languageIn) is None):
            languages = g.value(subject=shapeUri, predicate=self.sh.languageIn)
            lastListEntry = False
            while not lastListEntry:
                propertyShape.languageIn.append(
                    g.value(subject=languages, predicate=self.rdf.first)
                )
                # check if this was the last entry in the list
                if g.value(subject=languages, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                languages = g.value(subject=languages, predicate=self.rdf.rest)

        if not (g.value(subject=shapeUri, predicate=self.sh.uniqueLang) is None):
            uniqueLang = g.value(subject=shapeUri, predicate=self.sh.uniqueLang).lower()
            if (uniqueLang == "true"):
                propertyShape.uniqueLang = True

        for stmt in g.objects(shapeUri, self.sh.equals):
            propertyShape.equals.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.disjoint):
            propertyShape.disjoint.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.lessThan):
            propertyShape.lessThan.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.lessThanOrEquals):
            propertyShape.lessThanOrEquals.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.node):
            propertyShape.nodes.append(stmt)

        for stmt in g.objects(shapeUri, self.sh.hasValue):
            propertyShape.hasValue.append(stmt)

        if not (g.value(subject=shapeUri, predicate=self.sh['in']) is None):
            values = g.value(subject=shapeUri, predicate=self.sh['in'])
            lastListEntry = False
            while not lastListEntry:
                propertyShape.shIn.append(g.value(subject=values, predicate=self.rdf.first))
                # check if this was the last entry in the list
                if g.value(subject=values, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                values = g.value(subject=values, predicate=self.rdf.rest)

        if not (g.value(subject=shapeUri, predicate=self.sh.order) is None):
            propertyShape.order = g.value(subject=shapeUri, predicate=self.sh.order)

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape) is None):
            qvsUri = g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape)
            propertyShape.qualifiedValueShape = self.parsePropertyShape(g, qvsUri)

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapeDisjoint) is None):
            qualifiedValueShapeDisjoint = g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedValueShapeDisjoint
            ).lower()
            if (qualifiedValueShapeDisjoint == "true"):
                propertyShape.qualifiedValueShapeDisjoint = True

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount) is None):
            propertyShape.qualifiedMinCount = g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedMinCount
            )

        if not (g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount) is None):
            propertyShape.qualifiedMaxCount = g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedMaxCount
            )

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
            return pathUri
        else:
            raise Exception('Object of sh:path is no URI')
