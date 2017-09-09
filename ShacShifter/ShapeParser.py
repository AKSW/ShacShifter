#!/usr/bin/env python3

import rdflib
import argparse
import rdfextras
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape


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
            for property in shape.properties:
                print(property.path)
            print('-------------------------------------------------------------')

    def getNodeShapeUris(self, g):

        sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        nodeShapeUris = []
        #probably not a full list, as long as no Grammar exists, its probably staying incomplete
        #shacl-shacl could be analyzed for that
        #ignores sh:or/and/not/xone for now, they can be in node and property shapes, and can contain both as shacl list
        for stmt in g.subjects(rdflib.RDF.type, sh.NodeShape):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.property, None): #or/and/xor lists filtered, shouldnt be added here either way
            if not(stmt in nodeShapeUris) and stmt != rdflib.term.BNode(stmt): #todo check for the Subject being the Object of a sh:property instead
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.targetClass, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.targetNode, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.targetObjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.targetSubjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        for stmt in g.subjects(sh.targetSubjectsOf, None):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        #actually not exactly a nodeshape
        for stmt in g.subjects(rdflib.RDF.type, sh.PropertyGroup):
            if not(stmt in nodeShapeUris):
                nodeShapeUris.append(stmt)

        return nodeShapeUris

    def getPropertyShapeUris(self, g):
        return []

    def parseNodeShape(self, g, shapeUri):
        sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        nodeShape = NodeShape()
        nodeShape.uri = shapeUri
        for stmt in g.objects(shapeUri, sh.targetClass):
            nodeShape.targetClass.append(stmt)

        for stmt in g.objects(shapeUri, sh.targetNode):
            nodeShape.targetNode.append(stmt)

        for stmt in g.objects(shapeUri, sh.targetObjectsOf):
            nodeShape.targetObjectsOf.append(stmt)

        for stmt in g.objects(shapeUri, sh.targetSubjectsOf):
            nodeShape.targetSubjectsOf.append(stmt)

        nodeKind = g.value(subject=shapeUri, predicate=sh.nodeKind)
        if nodeKind != None:
            nodeShape.nodeKind = nodeKind

        for stmt in g.objects(shapeUri, sh.message):
            if (stmt.lang == None):
                nodeShape.message['general'] = stmt
            else:
                nodeShape.message[stmt.lang] = stmt

        for bn in g.objects(shapeUri, sh.property):
            propertyShape = self.parsePropertyShape(g, bn)
            nodeShape.properties.append(propertyShape)

        return nodeShape

    def parsePropertyShape(self, g, shapeUri):
        sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        propertyShape = PropertyShape()
        if shapeUri != rdflib.term.BNode(shapeUri):
            propertyShape.uri = shapeUri
        pathStart = g.value(subject=shapeUri, predicate=sh.path)
        propertyShape.path = self.getPropertyPath(g, pathStart)
        
        return propertyShape

    def getPropertyPath(self, g, pathUri):
        rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        #not enforcing blank nodes here, but stripping the link nodes from the data structure
        if not (g.value(subject=pathUri, predicate=rdf.first) is None):
            newPathUri = g.value(subject=pathUri, predicate=rdf.first)
            rdfList = []
            rdfList.append(self.getPropertyPath(g, newPathUri))
            if not (g.value(subject=pathUri, predicate=rdf.rest) == rdf.nil):
                newPathUri = g.value(subject=pathUri, predicate=rdf.rest)
                rest = self.getPropertyPath(g, newPathUri)
                if (isinstance(rest, list)):
                    rdfList += rest
                else:
                    rdfList.append(rest)
            return rdfList

        if not (g.value(subject=pathUri, predicate=sh.alternativePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=sh.alternativePath)
            rdfDict = {sh.alternativePath: self.getPropertyPath(g,newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=sh.inversePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=sh.inversePath)
            rdfDict = {sh.inversePath: self.getPropertyPath(g,newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=sh.zeroOrMorePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=sh.zeroOrMorePath)
            rdfDict = {sh.zeroOrMorePath: self.getPropertyPath(g,newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=sh.oneOrMorePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=sh.oneOrMorePath)
            rdfDict = {sh.oneOrMorePath: self.getPropertyPath(g,newPathUri)}
            return rdfDict

        if not (g.value(subject=pathUri, predicate=sh.zeroOrOnePath) is None):
            newPathUri = g.value(subject=pathUri, predicate=sh.zeroOrOnePath)
            rdfDict = {sh.zeroOrOnePath: self.getPropertyPath(g,newPathUri)}
            return rdfDict

        #last Object in this Pathpart, check if its a Uri and return it
        if pathUri == rdflib.term.URIRef(pathUri):
            return pathUri
        else:
            raise Exception('Object of sh:path is no URI')

# class Shape:
