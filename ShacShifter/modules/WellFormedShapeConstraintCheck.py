import logging
import rdflib
from rdflib.exceptions import UniquenessError
from .modules.WellFormedShape import WellFormedShape
from .modules.NodeShape import NodeShape
from .modules.PropertyShape import PropertyShape
from .modules.Exceptions import *
from .modules.NodeKindType import NodeKindType
class WellFormedShapeConstraintCheck:
    """A parser for Welformed Shapes Constraint Checks.

    This Class checks various of the constraints listed in:
        https://www.w3.org/TR/shacl/#syntax-rules
    Not all Constraints are necessary, some are implicitely checked in the parse process.
    A number of constraints are left out, because they have no relevance for this parser.
    It follows a list of explicitally implemented constraints, some grouped into big constraints:
        https://www.w3.org/TR/shacl/#syntax-rule-targetNode-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-targetClass-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-targetSubjectsOf-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-targetObjectsOf-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-message-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-path-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-class-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-datatype-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-datatype-maxCount
                                https://www.w3.org/TR/shacl/#syntax-rule-nodeKind-in
        https://www.w3.org/TR/shacl/#syntax-rule-nodeKind-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-minCount-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-minCount-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-maxCount-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-maxCount-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-minExclusive-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-minExclusive-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-minInclusive-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-minInclusive-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-maxExclusive-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-maxExclusive-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-maxInclusive-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-maxInclusive-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-minLength-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-minLength-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-maxLength-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-maxLength-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-pattern-datatype
                                 https://www.w3.org/TR/shacl/#syntax-rule-pattern-regex
        https://www.w3.org/TR/shacl/#syntax-rule-flags-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-languageIn-node
        https://www.w3.org/TR/shacl/#syntax-rule-languageIn-members-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-languageIn-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-uniqueLang-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-uniqueLang-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-equals-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-disjoint-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-lessThan-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-lessThanOrEquals-nodeKind
                                https://www.w3.org/TR/shacl/#syntax-rule-and-node
                                https://www.w3.org/TR/shacl/#syntax-rule-or-node
                                https://www.w3.org/TR/shacl/#syntax-rule-xone-node
        https://www.w3.org/TR/shacl/#syntax-rule-qualifiedValueShapesDisjoint-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-qualifiedMinCount-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-qualifiedMaxCount-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-closed-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-ignoredProperties-node
        https://www.w3.org/TR/shacl/#syntax-rule-ignoredProperties-members-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-in-node
        https://www.w3.org/TR/shacl/#syntax-rule-in-maxCount

    It follows a list of implicitely implemented constraints:
    # scope still needs to be implemnted in NodeShape.py
        https://www.w3.org/TR/shacl/#syntax-rule-SHACL-list
        https://www.w3.org/TR/shacl/#syntax-rule-shape
        https://www.w3.org/TR/shacl/#syntax-rule-multiple-parameters
        https://www.w3.org/TR/shacl/#syntax-rule-implicit-targetClass-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-NodeShape-path-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-PropertyShape
        https://www.w3.org/TR/shacl/#syntax-rule-path-node
        https://www.w3.org/TR/shacl/#syntax-rule-PropertyShape-path-minCount
        https://www.w3.org/TR/shacl/#syntax-rule-path-metarule
                             https://www.w3.org/TR/shacl/#syntax-rule-path-non-recursive
        https://www.w3.org/TR/shacl/#syntax-rule-path-sequence
        https://www.w3.org/TR/shacl/#syntax-rule-path-alternative
        https://www.w3.org/TR/shacl/#syntax-rule-path-inverse
        https://www.w3.org/TR/shacl/#syntax-rule-path-zero-or-more
        https://www.w3.org/TR/shacl/#syntax-rule-path-one-or-more
        https://www.w3.org/TR/shacl/#syntax-rule-path-zero-or-one
        https://www.w3.org/TR/shacl/#syntax-rule-minCount-scope
        https://www.w3.org/TR/shacl/#syntax-rule-maxCount-scope
        https://www.w3.org/TR/shacl/#syntax-rule-uniqueLang-scope
        https://www.w3.org/TR/shacl/#syntax-rule-lessThan-scope
        https://www.w3.org/TR/shacl/#syntax-rule-lessThanOrEquals-scope
        https://www.w3.org/TR/shacl/#syntax-rule-not-node
        https://www.w3.org/TR/shacl/#syntax-rule-and-members-node
        https://www.w3.org/TR/shacl/#syntax-rule-or-members-node
        https://www.w3.org/TR/shacl/#syntax-rule-xone-members-node
        https://www.w3.org/TR/shacl/#syntax-rule-node-node
        https://www.w3.org/TR/shacl/#syntax-rule-property-node
        https://www.w3.org/TR/shacl/#syntax-rule-qualifiedValueShape-node

    All Sparql-Shacl constraints are ignored, as this isnt implemented in Shachshifter.
    It follows a list of other unimplemented constraints, mostly unused predicates:
        https://www.w3.org/TR/shacl/#syntax-rule-entailment-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-severity-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-severity-nodeKind
        https://www.w3.org/TR/shacl/#syntax-rule-deactivated-maxCount
        https://www.w3.org/TR/shacl/#syntax-rule-deactivated-datatype
        https://www.w3.org/TR/shacl/#syntax-rule-shapesGraph-nodeKind
    """
    def __init__(self, graph, shapeUri):
        self.rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.sh = rdflib.Namespace('http://www.w3.org/ns/shacl#')
        self.xsd = rdflib.NameSpace('http://www.w3.org/2001/XMLSchema#')
        self.g = graph
        self.shapeUri = shapeUri
        self.errors = list()
        self.checkConstraints()

    def shaclListConstraint(self, listUri, nodeKindType=None, datatype=None):
        """Checks for the Shacllist Constraints.

        args:    rdflib.term.URIRef or rdflib.term.BNode listUri
        returns: None
        """
        shaclList = list()
        uri = listUri
        lastListEntry = False

         while not lastListEntry:
            if not (type(uri) == rdflib.term.URIRef or type(uri) == rdflib.term.Bnode):
                self.errors.append('Wrong Type in shacllist:{}'.format(uri))
            if uri in shaclList:
                self.errors.append('Loop in the shacllist:{}'.format(uri))
            shaclList.append(uri)
            if not nodeKind is None:
                val = str(self.g.value(subject=uri, predicate=self.rdf.first))
                self.nodeKindConstraint(
                    val, nodeKindType.isUri, nodeKindType.isBNode, nodeKindType.isLiteral
                )
            if not datatype is None:
                val = str(self.g.value(subject=uri, predicate=self.rdf.first))
                self.datatypeConstraint(val, datatype)
            # check if this was the last entry in the list
            if self.g.value(subject=uri, predicate=self.rdf.rest) == self.rdf.nil:
                lastListEntry = True
            properties = self.g.value(subject=uri, predicate=self.rdf.rest)

    def nodeKindConstraint(self, object, nodeKindType):
        """Checks for the nodekind Constraints.

        args:    list or rdflib.term.URIRef or rdflib.term.BNode or rdflib.term.literal object
                 boolean isUri
                 boolean isBNode
                 boolean isLiteral
        returns: None
        """
        correctType = False
        if nodeKindType.isUri and type(object) is rdflib.term.URIRef:
            correctType = True
        if nodeKindType.isBNode and type(object) is rdflib.term.BNode:
            correctType = True
        if nodeKindType.isLiteral and type(object) is rdflib.term.literal:
            correctType = True
        if not correctType:
            self.errors.append(NodeKindConstraintError(
                'Conflict found. Object has the wrong type:{}'.format(object))
            )

    def datatypeConstraint(self, object, datatype):
        """Checks for the datatype Constraints.

        args:    list or rdflib.term.URIRef or rdflib.term.BNode or rdflib.term.literal object
                 boolean isUri
                 boolean isBNode
                 boolean isLiteral
        returns: None
        """
        if type(object) is rdflib.term.literal:
            if object.datatype is not datatype:
                self.errors.append(DataTyepConstraintError(
                    'Conflict found. Object has the wrong datatype:{}'.format(object))
            )
        else:
            self.errors.append(DataTyepConstraintError(
                'Conflict found. Object has the wrong datatype:{}'.format(object))
            )

    def maxConstraint(self):
        """Checks for the max Constraints.

        args:    None
        returns: None
        """
        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.ignoredProperties))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.nodekind, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.nodekind))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.closed, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.closed)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.path, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.path)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.datatype, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.data)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minCount, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.minCount))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxCount, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.maxCount))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.minExclusive))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.minInclusive))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.maxExclusive))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.maxInclusive))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.minLength, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.minLength))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.maxLength))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.pattern, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.pattern)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.flags, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.flags)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.uniqueLang))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh['in'], any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh['in'])))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.order, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.order)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShape, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.qualifiedValueShape))
            )

        try:
            val = self.g.value(
                subject=shapeUri,
                predicate=self.sh.qualifiedValueShapesDisjoint,
                any=False
            )
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.qualifiedValueShapesDisjoint))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.qualifiedMinCount))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.qualifiedMaxCount))
            )

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.group, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError('Conflict found for {}'.format(self.sh.group)))

        try:
            val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn, any=False)
        except UniquenessError:
            self.errors.append(MaxConstraintError(
                'Conflict found for {}'.format(self.sh.languageIn))
            )

    def checkConstraints(self):
        """Checks for the nodekind Constraints

        args:    None
        returns: None
        """
        # TODO add full constraint check (e.g. sh:A and sh:B can't be in the
        # same Shape or sh:C can only be in Propertyshapes)
        # sh:entailment is ignored (should we add it?)
        # shape constraint is tested through the whole process?
        # how to check pattern regex being sparql valid?
        # ignoring a check for min and max of ranges so far, its no constraint
        # is closed relevant?
        # path parsing shacl list checks?
        # list constraints

        val = self.g.value(subject=shapeUri, predicate=self.sh.languageIn)
        if val is not None:
            self.shaclListConstraint(val, None, self.xsd.string)

        val = self.g.value(subject=shapeUri, predicate=self.sh.ignoredProperties)
        if val is not None:
            self.shaclListConstraint(val, NodeKindType(True, False, False), None)

        val = self.g.value(subject=shapeUri, predicate=self.sh['in'])
        if val is not None:
            self.shaclListConstraint(val, None, None)

        # node kind constraints with multiple values:
        for stmt in self.g.objects(shapeUri, self.sh.targetNode)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, True))

        for stmt in self.g.objects(shapeUri, self.sh.targetClass)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.targetSubjectsOf)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.targetObjectsOf)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh['class'])
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.equals)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.disjoint)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.lessThan)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        for stmt in self.g.objects(shapeUri, self.sh.lessThanOrEquals)
            self.nodeKindConstraint(stmt, NodeKindType(True, False, False))

        # node kind constraints with single values
        val = self.g.value(subject=shapeUri, predicate=self.sh.datatype)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(True, False, False))

        val = self.g.value(subject=shapeUri, predicate=self.sh.minCount)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxCount)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.minExclusive)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.minInclusive)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxExclusive)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxInclusive)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.flags)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.pattern)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        val = self.g.value(subject=shapeUri, predicate=self.sh.closed)
        if val is not None:
            self.nodeKindConstraint(val, NodeKindType(False, False, True))

        # max constraints
        self.maxConstraint()

        # datatype constraints with multiple values:
        for stmt in self.g.objects(shapeUri, self.sh.message)
            if stmt.language is None:
                self.datatypeConstraint(stmt, xsd.string)

        # datatype constraints with single values:
        val = self.g.value(subject=shapeUri, predicate=self.sh.minCount)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxCount)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.minLength)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.maxLength)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.pattern)
        if val is not None:
            self.datatypeConstraint(val, xsd.string)

        val = self.g.value(subject=shapeUri, predicate=self.sh.flags)
        if val is not None:
            self.datatypeConstraint(val, xsd.string)

        val = self.g.value(subject=shapeUri, predicate=self.sh.uniqueLang)
        if val is not None:
            self.datatypeConstraint(val, xsd.boolean)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedValueShapesDisjoint)
        if val is not None:
            self.datatypeConstraint(val, xsd.boolean)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMinCount)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.qualifiedMaxCount)
        if val is not None:
            self.datatypeConstraint(val, xsd.integer)

        val = self.g.value(subject=shapeUri, predicate=self.sh.closed)
        if val is not None:
            self.datatypeConstraint(val, xsd.boolean)
