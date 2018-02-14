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
        # self.sOr = []
        # self.sNot = []
        # self.sAnd = []
        # self.sXone = []
        self.message = {}
        self.severity = -1
