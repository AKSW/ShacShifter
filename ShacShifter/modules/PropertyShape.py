class PropertyShape:
    """The PropertyShape class."""

    def __init__(self):
        self.uri = ''
        self.path = ''
        self.classes = []
        self.datatype = ''
        self.name = {}
        self.description = {}
        self.minCount = -1
        self.maxCount = -1
        self.minExclusive = -1
        self.minInclusive = -1
        self.maxExclusive = -1
        self.maxInclusive = -1
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
        self.qualifiedMinCount = []
        self.qualifiedMaxCount = []
        self.hasValue = []
        self.shIn = []
        self.order = -1
        self.group = ''
        self.message = {}
        self.sOr = []
        self.sNot = []
        self.sAnd = []
        self.sXone = []
        # non-shacl variable for Exceptionhandling
        self.errors = []
        self.isSet = {}
        for var in vars(self):
            if not var.startswith('__'):
                self.isSet[var] = False

    def fill(self, wellFormedShape):
        if not wellFormedShape.isSet['path']:
            raise TypeError('Given Shape is no PropertyShape (no path)')
        for var in vars(self):
            if wellFormedShape.isSet[var]:
                self.isSet[var] = True
                setattr(self, var, getattr(wellFormedShape, var))
