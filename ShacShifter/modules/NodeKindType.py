class NodeKindType:
    """Simple Class for types of Objects"""
    self.isUri = False
    self.isBNode = False
    self.isLiteral = False

    def __init__(self, isUri, isBNode, isLiteral):
        self.isUri = isUri
        self.isBNode = isBNode
        self.isLiteral = isLiteral
        