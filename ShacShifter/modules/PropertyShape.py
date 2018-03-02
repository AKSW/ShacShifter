class PropertyShape:
    """The PropertyShape class."""

    def __init__(self):
        self.uri = ''
        self.path = ''
        self.classes = []
        self.dataType = ''
        self.name = ''
        self.description = ''
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
        self.qualifiedValueShape = ''
        self.qualifiedValueShapesDisjoint = False
        self.qualifiedMinCount = -1
        self.qualifiedMaxCount = -1
        self.hasValue = []
        self.shIn = []
        self.order = -1
        self.message = {}
        # self.sOr = []
        # self.sNot = []
        # self.sAnd = []
        # self.sXone = []
        isSet = {}
        for var in vars(self):
            if not var.startswith('__'):
                isSet[var] = False
        self.isSet = isSet
