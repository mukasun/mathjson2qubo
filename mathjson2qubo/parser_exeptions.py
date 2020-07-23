class ParserError(Exception):
    pass


class NotFoundVariableError(ParserError):
    pass


class VariableIndexOutOfRangeError(ParserError):
    pass


class InvalidMathJsonFormatError(ParserError):
    pass
