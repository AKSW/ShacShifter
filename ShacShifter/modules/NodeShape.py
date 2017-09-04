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