class ParserError(Exception):
    pass


class NotFoundVariableError(ParserError):
    pass


class VariableIndexOutOfRangeError(ParserError):
    pass


class InvalidMathJsonFormatError(ParserError):
    pass


class InvalidSubScriptError(ParserError):
    pass


class InvalidSuperScriptError(ParserError):
    pass
