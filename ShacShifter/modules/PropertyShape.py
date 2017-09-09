class PropertyShape:
    #everything that has sh:path as predicate
    def __init__(self):
        self.uri = '' #stays empty if its a blank node
        self.path = ''
        self.shClasses = []
        self.dataType = ''
        self.minCount = ''
        self.maxCount = ''
        self.minExclusive = ''
        self.minInclusive = ''
        self.maxExclusive = ''
        self.MaxInclusive = ''
        self.minLength = ''
        self.maxLength = ''
        self.pattern = ''
        self.flags = ''
        self.languageIn = []
        self.uniqueLang = False
        self.equals = []
        self.disjoint = []
        self.lessThan = []
        self.lessThanOrEquals = []
        self.nodes = []
        #self.qualifiedValueShape = [] #Not exactly sure how multiple qVS are possible with personal min/max counts in the same property
        #self.qualifiedValueShapesDisjoint = False
        #self.qualifiedMinCount = ''
        #self.qualifiedMaxCount = ''
        self.hasValue = []
        self.shIn = []