class WellFormedShape:
    """The WellFormedShape class."""

    def __init__(self):
        self.classUri = ''
        self.uri = ''
        self.name = '' #name and description can have more values than 1, but its semi-restricted to 1 per language tag?
        self.description = ''
        self.targetClass = []
        self.targetNode = []
        self.targetObjectsOf = []
        self.targetSubjectsOf = []
        self.nodeKind = ''
        self.properties = []
        self.defaultValue = ''
        self.path = ''
        self.closed = False
        self.ignoredProperties = []
        self.sOr = []
        self.sNot = []
        self.sAnd = []
        self.sXone = []
        self.message = {}
        self.classes = []
        self.datatype = ''
        self.minCount = -1
        self.maxCount = -1
        self.minExclusive = -1
        self.minInclusive = -1
        self.maxExclusive = -1
        self.MaxInclusive = -1
        self.minLength = -1
        self.maxLength = -1
        self.pattern = ''
        self.flags = ''
        self.languageIn = []
        self.uniqueLang = False
        self.equals = []
        self.disjoint = []
        self.lessThan = []
        self.lessThanOrEquals = []
        self.nodes = []
        self.qualifiedValueShape = []
        self.qualifiedValueShapesDisjoint = []
        self.qualifiedMinCount = -[]
        self.qualifiedMaxCount = -[]
        self.hasValue = []
        self.shIn = []
        self.order = -1
        # maybe add group shape as shape for special useage (extra information for
        # 'grouped' parts of a form?) example in at #group
        # or just keep it as well-formed shape
        self.group = ''
        self.severity = -1
        isSet = {}
        for var in vars(self):
            if not var.startswith('__'):
                isSet[var] = False
        self.isSet = isSet
