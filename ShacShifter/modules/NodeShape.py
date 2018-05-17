class NodeShape:
    """The NodeShape class."""

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
        isSet = {}
        for var in vars(self):
            if not var.startswith('__'):
                isSet[var] = False
        self.isSet = isSet

    def fill(self, wellFormedShape):
        # is check for properties necessary? without targets the nodeshape is useless
        if not (wellFormedShape.isSet('targetClass') or
                wellFormedShape.isSet('targetNode') or
                wellFormedShape.isSet('targetObjectsOf') or
                wellFormedShape.isSet('targetSubjectsOf') or
                wellFormedShape.isSet('properties')):
            raise TypeError('Given Shape is no NodeShape')
        for var in vars(self):
            if wellFormedShape.isSet[var]:
                self.isSet[var] = True
                setattr(self, var, getattr(wellFormedShape, var))
