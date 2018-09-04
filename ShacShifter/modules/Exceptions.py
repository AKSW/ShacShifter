

class Error(Exception):
    """
    Base class for ShacShifter Exceptions
    """


class ParseError(Error):
    """
    Base Class for Parser Exceptions
    """


class PathError(ParseError):
    """
    Base Class for Path Exceptions
    """


class ConstraintError(ParseError):
    """
    Base Class for Constraint Exceptions
    """


class MaxConstraintError(ConstraintError):
    """
    Thrown when more than one Value exists for certain Shacl Constraints
    """


class ShaclListConstraintError(ConstraintError):
    """
    Thrown when a List doesnt conform to the Shacl list standard
    """


class NodeKindConstraintError(ConstraintError):
    """
    Thrown when a Literal has the wrong type
    """


class DataTypeConstraintError(ConstraintError):
    """
    Thrown when a Literal has the wrong type or the wrong type/language tag
    """


class MinMaxConstraintError(ConstraintError):
    """
    Thrown when min and max parts of ranges don't have min >= max
    """
