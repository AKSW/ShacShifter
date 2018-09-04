#!/usr/bin/env python3

import logging
import rdflib
from .modules.WellFormedShape import WellFormedShape
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .modules.WellFormedShapeConstraintCheck import WellFormedShapeConstraintCheck


class ShapeParser:
    """A parser for SHACL Shapes."""

    logger = logging.getLogger('ShacShifter.ShapeParser')

    def __init__(self):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.g = rdflib.Graph()
        self.wellFormedShapes = {}
        self.propertyShapes = {}

    def parseShape(self, inputFilePath):
        """Parse a Shape given in a file.

        args: string inputFilePath
        returns: list of dictionaries for nodeShapes and propertyShapes
        """
        self.g.parse(inputFilePath, format='turtle')
        wellFormedShapeUris = self.getWellFormedShapeUris()

        for shapeUri in wellFormedShapeUris:
            wellFormedShape = self.parseWellFormedShape(shapeUri)
            self.wellFormedShapes[str(shapeUri)] = wellFormedShape

        return self.wellFormedShapes

    def getWellFormedShapeUris(self):
        """Get URIs of all Root Node shapes.

        returns: list of Node Shape URIs
        """
        wellFormedShapeUris = list()

        qres = self.g.query("""
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            SELECT DISTINCT ?root
            WHERE {{
                ?root ?s ?o .
                FILTER NOT EXISTS {?a ?b ?root .}
                }
                UNION
                {
                ?s sh:node ?root
                }}""")

        for row in qres:
            wellFormedShapeUris.append(row.root)

        return wellFormedShapeUris

    def getPropertyShapeCandidates(self):
        """Get all property shapes.

        The property shapes must not be nodeshape properties or used in sh:not, sh:and,
        sh:or or sh:xor

        returns: list of Property Shape URIs
        """
        propertyShapeUris = set()

        for stmt in self.g.subjects(self.sh.path, None):
            if (self.g.value(predicate=self.sh.property, object=stmt) is None and
                    self.g.value(predicate=self.rdf.first, object=stmt) is None and
                    self.g.value(predicate=self.sh['not'], object=stmt) is None):
                propertyShapeUris.add(stmt)

        return propertyShapeUris

    def parseWellFormedShape(self, shapeUri):
        """Parse a WellFormedShape given by its URI.

        args:    string shapeUri
        returns: object WellFormedShape/NodeShape/PropertyShape
        """
        # consider allowing different rdf predicates like title for headings etc.
        wellFormedShape = WellFormedShape()
        # test for most relevant constraints
        wfscc = WellFormedShapeConstraintCheck(self.g, shapeUri)
        wellFormedShape.errors = wfscc.errors
        # add variable for invalidation, and maybe create "critical errors"
        # if len(wellFormedShape.errors) > 0:
        #     return None
        # if empty "URI's" are bad change it later on to add Blanknodes too
        if shapeUri != rdflib.term.BNode(shapeUri):
            wellFormedShape.isSet['uri'] = True
            wellFormedShape.uri = str(shapeUri)

        for stmt in self.g.objects(shapeUri, self.sh.targetClass):
            wellFormedShape.isSet['targetClass'] = True
            wellFormedShape.targetClass.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetNode):
            wellFormedShape.isSet['targetNode'] = True
            wellFormedShape.targetNode.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetObjectsOf):
            wellFormedShape.isSet['targetObjectsOf'] = True
            wellFormedShape.targetObjectsOf.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.targetSubjectsOf):
            wellFormedShape.isSet['targetSubjectsOf'] = True
            wellFormedShape.targetSubjectsOf.append(str(stmt))

        val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
        if val is not None:
            wellFormedShape.isSet['ignoredProperties'] = True
            properties = val
            lastListEntry = False

            while not lastListEntry:
                wellFormedShape.ignoredProperties.append(
                    str(self.g.value(subject=properties, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=properties, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                properties = self.g.value(subject=properties, predicate=self.rdf.rest)

        for stmt in self.g.objects(shapeUri, self.sh.message):
            wellFormedShape.isSet['message'] = True
            if (stmt.language is None):
                wellFormedShape.message['default'] = str(stmt)
            else:
                wellFormedShape.message[stmt.language] = str(stmt)

        val = self.g.value(subject=shapeUri, predicate=self.sh.nodeKind)
        if val is not None:
            wellFormedShape.isSet['nodeKind'] = True
            wellFormedShape.nodeKind = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.closed)
        if val is not None:
            wellFormedShape.isSet['closed'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.closed = True

        for stmt in self.g.objects(shapeUri, self.sh.property):
            wellFormedShape.isSet['property'] = True
            propertyShape = self.parseWellFormedShape(stmt)
            wellFormedShape.errors += propertyShape.errors
            self.propertyShapes[stmt] = propertyShape
            wellFormedShape.properties.append(propertyShape)

        pathStart = self.g.value(subject=shapeUri, predicate=self.sh.path)
        if pathStart is not None:
            wellFormedShape.isSet['path'] = True
            wellFormedShape.path = self.getPropertyPath(pathStart)

        for stmt in self.g.objects(shapeUri, self.sh['class']):
            wellFormedShape.isSet['classes'] = True
            wellFormedShape.classes.append(str(stmt))

        val = self.g.value(subject=shapeUri, predicate=self.sh['name'])
        if val is not None:
            wellFormedShape.isSet['name'] = True
            wellFormedShape.name = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh['description'])
        if val is not None:
            wellFormedShape.isSet['description'] = True
            wellFormedShape.description = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.datatype)
        if val is not None:
            wellFormedShape.isSet['datatype'] = True
            wellFormedShape.datatype = str(val)

        minCount = self.g.value(subject=shapeUri, predicate=self.sh.minCount)
        if minCount is not None:
            wellFormedShape.isSet['minCount'] = True
            wellFormedShape.minCount = int(minCount)

        maxCount = self.g.value(subject=shapeUri, predicate=self.sh.maxCount)
        if maxCount is not None:
            wellFormedShape.isSet['maxCount'] = True
            wellFormedShape.maxCount = int(maxCount)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive)
        if val is not None:
            wellFormedShape.isSet['minExclusive'] = True
            wellFormedShape.minExclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive)
        if val is not None:
            wellFormedShape.isSet['minInclusive'] = True
            wellFormedShape.minInclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive)
        if val is not None:
            wellFormedShape.isSet['maxExclusive'] = True
            wellFormedShape.maxExclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive)
        if val is not None:
            wellFormedShape.isSet['maxInclusive'] = True
            wellFormedShape.maxInclusive = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minLength)
        if val is not None:
            wellFormedShape.isSet['minLength'] = True
            wellFormedShape.minLength = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength)
        if val is not None:
            wellFormedShape.isSet['maxLength'] = True
            wellFormedShape.maxLength = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.pattern)
        if val is not None:
            wellFormedShape.isSet['pattern'] = True
            wellFormedShape.pattern = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.flags)
        if val is not None:
            wellFormedShape.isSet['flags'] = True
            wellFormedShape.flags = str(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn)
        if val is not None:
            wellFormedShape.isSet['languageIn'] = True
            languages = val
            lastListEntry = False

            while not lastListEntry:
                wellFormedShape.languageIn.append(
                    str(self.g.value(subject=languages, predicate=self.rdf.first))
                )
                # check if this was the last entry in the list
                if self.g.value(subject=languages, predicate=self.rdf.rest) == self.rdf.nil:
                    lastListEntry = True
                languages = self.g.value(subject=languages, predicate=self.rdf.rest)

        val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang)
        if val is not None:
            wellFormedShape.isSet['uniqueLang'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.uniqueLang = True

        for stmt in self.g.objects(shapeUri, self.sh.equals):
            wellFormedShape.isSet['equals'] = True
            wellFormedShape.equals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.disjoint):
            wellFormedShape.isSet['disjoint'] = True
            wellFormedShape.disjoint.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThan):
            wellFormedShape.isSet['lessThan'] = True
            wellFormedShape.lessThan.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.lessThanOrEquals):
            wellFormedShape.isSet['lessThanOrEquals'] = True
            wellFormedShape.lessThanOrEquals.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.node):
            wellFormedShape.isSet['nodes'] = True
            wellFormedShape.nodes.append(str(stmt))

        for stmt in self.g.objects(shapeUri, self.sh.hasValue):
            wellFormedShape.isSet['hasValue'] = True
            wellFormedShape.hasValue.append(stmt)

        val = self.g.value(subject=shapeUri, predicate=self.sh['in'])
        if val is not None:
            wellFormedShape.isSet['shIn'] = True
            lastListEntry = False

            while True:
                first_value = self.g.value(subject=val, predicate=self.rdf.first)
                rest_value = self.g.value(subject=val, predicate=self.rdf.rest)
                wellFormedShape.shIn.append(first_value)
                # check if this was the last entry in the list
                if rest_value == self.rdf.nil:
                    break
                val = rest_value

        val = self.g.value(subject=shapeUri, predicate=self.sh.order)
        if val is not None:
            wellFormedShape.isSet['order'] = True
            wellFormedShape.order = int(val)

        # QVS can have multiple Instances per Path, but every ProperyShape can only have 1
        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape)
        if val is not None:
            wellFormedShape.isSet['qualifiedValueShape'] = True
            wellFormedShape.qualifiedValueShape = self.parseWellFormedShape(val)
            wellFormedShape.errors += wellFormedShape.qualifiedValueShape.errors

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint)
        if val is not None:
            wellFormedShape.isSet['qualifiedValueShapesDisjoint'] = True
            if (str(val).lower() == "true"):
                wellFormedShape.qualifiedValueShapesDisjoint = True
                # TODO check Sibling Shapes

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount)
        if val is not None:
            wellFormedShape.isSet['qualifiedMinCount'] = True
            wellFormedShape.qualifiedMinCount = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount)
        if val is not None:
            wellFormedShape.isSet['qualifiedMaxCount'] = True
            wellFormedShape.qualifiedMaxCount = int(val)

        val = self.g.value(subject=shapeUri, predicate=self.sh.group)
        if val is not None:
            wellFormedShape.isSet['group'] = True
            wellFormedShape.group = self.parseWellFormedShape(val)
            wellFormedShape.errors += wellFormedShape.group.errors
        try:
            propertyShape = PropertyShape()
            propertyShape.fill(wellFormedShape)
            shape = propertyShape
        except TypeError:
            try:
                nodeShape = NodeShape()
                nodeShape.fill(wellFormedShape)
                shape = nodeShape
            except TypeError:
                shape = wellFormedShape

        return shape

    def getPropertyPath(self, pathUri):
        """Parses the Propertypath.

        args:    string pathUri
        returns: dict rdfDict or list rdfList or string pathUri
        """
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
            # newPathUri = altPath
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
        if isinstance(pathUri, rdflib.term.URIRef):
            return str(pathUri)
