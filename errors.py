__author__ = 'ZhangJingtian'

class ParserError(Exception):
    """ParserError class

    The base error class for all other parsing errors.
    """
    pass


class ParserSyntaxError(ParserError):
    """ParserSyntaxError class

    Thrown when a syntax error occurs in the parser.
    """
    pass


class ParserNameError(ParserError):
    """ParserNameError class

    Thrown when a name error occurs in the parser.
    """
    pass


class ParserTypeError(ParserError):
    """ParserTypeError class

    Thrown when a type error occurs in the parser.
    """
    pass